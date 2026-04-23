#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-19
#  描述：modbus rtu over serial
#
import time
import ustruct
from .znlib_log import getLogger
from .znlib_const import byteOrder, dt
from .znlib_serial import getSerial
from .znlib_waiter import getWaiter
from .znlib_config import loadConfig


class modbusClient:
    # Modbus 功能码常量
    READ_COILS = 0x01
    READ_DISCRETE_INPUTS = 0x02
    READ_HOLDING_REGISTERS = 0x03
    READ_INPUT_REGISTERS = 0x04
    WRITE_SINGLE_COIL = 0x05
    WRITE_SINGLE_REGISTER = 0x06
    WRITE_MULTIPLE_COILS = 0x0F
    WRITE_MULTIPLE_REGISTERS = 0x10

    def __init__(self, cfg):
        """
        初始化 Modbus 客户端
        :param serial_port: 已初始化的 SerialPort 实例
        :param timeout_ms: 接收响应的超时时间(毫秒)
        """
        self.slave_id = 0  # 从站标识
        self.op_type = 0  # 操作码
        self.is_read = True  # 读写标识

        self.serial = getSerial(self._onRecv, cfg["uart"])
        self.timeout_ms = cfg["timeout_ms"]
        self.crc_endian = byteOrder.little

        # 等待对象
        self.waiter = getWaiter()

        # 日志对象
        self.log = getLogger("modbus")

    def connect(self, active):
        if active:  # 打开连接
            self.serial.start()
        else:  # 关闭连接
            self.serial.stop()

    def _calculate_crc16(self, data):
        """
        计算 Modbus RTU 的 CRC16 校验码
        :param data: bytes 数据
        :param crc_endian: CRC 校验码的字节序
        :return: 2字节的 CRC(根据 crc_endian 决定字节序)
        """
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001  # 多项式 0xA001
                else:
                    crc >>= 1

        # 根据配置返回字节序
        # 标准 Modbus RTU 是低字节在前，高字节在后 (little)
        return crc.to_bytes(2, self.crc_endian)

    def _send_request(
        self,
        slave_id,
        func_code,
        start_addr,
        quantity,
        payload=None,
    ):
        self.slave_id = slave_id  # 从站标识
        self.op_type = func_code  # 操作码
        self.is_read = func_code < 5  # 读写标识

        # 构建 PDU (协议数据单元)
        pdu = bytearray(
            [slave_id, func_code, (start_addr >> 8) & 0xFF, start_addr & 0xFF]
        )

        if payload:
            pdu.extend(payload)
        else:  # 如果没有 payload，则添加数量 (2字节)
            pdu.extend(bytearray([(quantity >> 8) & 0xFF, quantity & 0xFF]))

        # 计算 CRC 并附加
        crc = self._calculate_crc16(pdu)
        frame = pdu + crc

        # 发送数据
        self.serial.send(frame)

        # 等待结果
        return self.waiter.waitFor(self.timeout_ms)

    def _onRecv(self, serial, rx):
        """
        接收并解析modbus协议
        :param rx: 接收缓冲区
        """
        idx, end = rx.pick_range()
        while idx < end:
            if self.is_read:
                if end - idx < 5:  # 数据不全:地址1 功能码1 数据量1 数据n 校验2
                    break
            elif end - idx < 8:  # 数据不全:地址1 功能码1 地址2 数据2 校验2
                break

            if (
                rx.buffer[rx.r_i(idx)] != self.slave_id  # 站地址匹配
                or rx.buffer[rx.r_i(idx + 1)] != self.op_type  # 功能码匹配
            ):

                idx = idx + 1  # 忽略不匹配
                rx.pick_move(idx)  # 更新开始游标
                continue

            dLen = 0
            if self.is_read:
                dLen = rx.buffer[rx.r_i(idx + 2)] + idx + 2  # 校验前位置
            else:
                dLen = idx + 5  # 写操作的应答数据,定长 8 位
            end

            if dLen + 2 >= end:  # 数据未收完
                break

            crc_val = 0
            if self.crc_endian == byteOrder.big:
                crc_val = (
                    rx.buffer[rx.r_i(dLen + 1)] * 256 + rx.buffer[rx.r_i(dLen + 2)]
                )
            else:
                crc_val = (
                    rx.buffer[rx.r_i(dLen + 2)] * 256 + rx.buffer[rx.r_i(dLen + 1)]
                )

            crc_data = self._calculate_crc16(rx.pick_data(idx, dLen + 1))
            crc_recv = crc_data[1] * 256 + crc_data[0]

            if crc_val == crc_recv:  # 校验通过
                res = []
                if (
                    self.op_type == self.READ_HOLDING_REGISTERS  # 读保持寄存器
                    or self.op_type == self.READ_INPUT_REGISTERS  # 读输入寄存器
                ):
                    i = idx + 3
                    while i < dLen:
                        res.append(
                            rx.buffer[rx.r_i(i)] * 256 + rx.buffer[rx.r_i(i + 1)]
                        )  # 大端数据
                        i += 2

                elif (
                    self.op_type == self.READ_COILS  # 读线圈状态
                    or self.op_type == self.READ_DISCRETE_INPUTS  # 读离散输入状态
                ):
                    i = idx + 3
                    while i <= dLen:
                        res.append(rx.buffer[rx.r_i(i)])
                        i += 1

                # 返回数据
                self.waiter.wakeup(res)

            idx = dLen + 3  # 下一组索引
            rx.pick_move(idx)  # 更新开始游标

    def read_coils(self, slave_id, start_addr, quantity):
        return self._send_request(slave_id, self.READ_COILS, start_addr, quantity)

    def read_holding_registers(self, slave_id, start_addr, quantity):
        return self._send_request(
            slave_id, self.READ_HOLDING_REGISTERS, start_addr, quantity
        )

    def write_single_coil(self, slave_id, addr, value):
        val_hex = 0xFF00 if value != 0 else 0x0000
        payload = val_hex.to_bytes(2, byteOrder.big)
        return (
            self._send_request(slave_id, self.WRITE_SINGLE_COIL, addr, 0, payload)
            is not None
        )

    def write_multiple_coils(self, slave_id, addr, coil_num, value):
        fmt = dt.fmt(dt.big, dt.ushort, dt.uchar)
        payload = bytearray(ustruct.pack(fmt, coil_num, len(values) * 2))  # 大端2+1

        for val in values:
            payload.extend(val.to_bytes(2, byteOrder.big))

        return (
            self._send_request(slave_id, self.WRITE_MULTIPLE_COILS, addr, 0, payload)
            is not None
        )

    def write_single_register(self, slave_id, addr, value):
        payload = value.to_bytes(2, byteOrder.big)
        return (
            self._send_request(slave_id, self.WRITE_SINGLE_REGISTER, addr, 0, payload)
            is not None
        )

    def write_multiple_registers(self, slave_id, start_addr, values):
        num = len(values)
        fmt = dt.fmt(dt.big, dt.ushort, dt.uchar)
        payload = bytearray(ustruct.pack(fmt, num, num * 2))  # 大端2+1

        for val in values:
            payload.extend(val.to_bytes(2, byteOrder.big))

        return (
            self._send_request(
                slave_id,
                self.WRITE_MULTIPLE_REGISTERS,
                start_addr,
                0,
                payload,
            )
            is not None
        )


def getModbus(cfg=None):
    """
    返回一个基于串口的modbus对象
    :param cfg: 配置名称或内容(字典)
    """

    # 默认配置
    _cfg = {
        "uart": "uart",  # UART配置
        "timeout_ms": 1000,  # 读写超时
        "slavers": {},  # 从站列表
    }

    # 载入配置文件
    if isinstance(cfg, str):
        cfg_file, ok = loadConfig(cfg)
        if ok:  # 载入配置
            cfg = cfg_file.get()
        else:  # 保存默认
            cfg = None
            cfg_file.set(_cfg)

    # 合并默认值
    if isinstance(cfg, dict):
        _cfg.update(cfg)
    return modbusClient(_cfg), _cfg["slavers"]
