#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-15
#  描述：辅助工具类
#
import gc
import net
import uos
import _thread
import checkNet

from misc import Power
from machine import RTC
from usr.znlib.const import sysInfo, sysType
from usr.znlib.log import getLogger
from usr.znlib.base import Singleton


class utils(Singleton):
    log = getLogger("utils")

    # RTC时钟
    def now_rtc(self):
        rtc = RTC().datetime()
        return "{}-{:02d}-{:02d}".format(*rtc[0:3]) + " {:02d}:{:02d}:{:02d}".format(
            *rtc[4:7]
        )

    # 打印系统信息
    def print_moduble_info(self):
        self.log.info("=" * 42)
        try:
            import usys as sys
        except ImportError:
            import sys
        vm = sys.implementation
        self.log.info(" python   : {}".format(sys.version))
        self.log.info(" vm_ver   : {}.{}.{}".format(vm[1][0], vm[1][1], vm[1][2]))

        self.log.info(" pro_ver  : {}".format(sysInfo.PROJECT_VERSION))
        self.log.info(" project  : {}".format(sysInfo.PROJECT_NAME))
        self.log.info(" firmware : {}".format(sysInfo.DEVICE_FIRMWARE_NAME))
        self.log.info(" firm_ver : {}".format(sysInfo.DEVICE_FIRMWARE_VERSION))
        self.log.info(" dev_imei : {}".format(sysInfo.DEVICE_IMEI))
        self.log.info(" dev_sn   : {}".format(sysInfo.DEVICE_SN))

        self.log.info(" free_ram : {} Bytes".format(gc.mem_free()))
        self.log.info(" free_rom : {} Bytes".format(_thread.get_heap_size()))
        usr = uos.statvfs("/usr")
        self.log.info(" free_usr : {} Bytes".format(usr[0] * usr[3]))
        self.log.info(" vbat     : {} mV".format(Power.getVbatt()))

        self.log.info(" OPERATOR : {} ".format(net.operatorName()))
        cfg = sysType.NET_CONFIG.get(net.getConfig()[0], "UNKNOWN")
        self.log.info(" NET      : {} ".format(cfg))
        self.log.info(" CSQ      : {} ".format(net.csqQueryPoll()))
        self.log.info(" RTC      : {} ".format(self.now_rtc()))
        self.log.info("=" * 42)

    # 文件是否存在
    def file_exists(self, file_full):
        try:
            stat = uos.stat(file_full)
            return stat[-4] >= 0  # 大小
        except:
            return False

    def data_to_hex(self, data, sep_bytes=True, dtype="B"):
        """
        将 list/tuple 转换为十六进制字符串
        :param data: list 或 tuple（元素为 int 或 bytes/bytearray）
        :param sep_bytes: True 时按单字节(2位HEX)插入空格分隔
        :param dtype: 数据类型标识，默认 'B' (unsigned char)
        :return: 十六进制字符串
        """
        if not isinstance(data, (list, tuple)):
            raise TypeError("data must be a list or tuple")
        if dtype not in sysType.DTYPE_SIZES:
            raise ValueError("Unsupported dtype: {}".format(dtype))

        size = sysType.DTYPE_SIZES[dtype]
        width = size * 2  # 单个元素占用的 HEX 字符数
        mask = (1 << (8 * size)) - 1
        fmt = "%0{}X".format(width)

        hex_parts = []
        for val in data:
            if isinstance(val, int):
                hex_parts.append(fmt % (val & mask))
            elif isinstance(val, (bytes, bytearray)):
                # 兼容字节对象，按单字节展开
                for b in val:
                    hex_parts.append("%02X" % b)
            else:
                hex_parts.append(fmt % (int(val) & mask))

        full_hex = "".join(hex_parts)
        if sep_bytes:
            # 按单字节(2个HEX字符)分组插入空格
            return " ".join([full_hex[i : i + 2] for i in range(0, len(full_hex), 2)])
        return full_hex

    def hex_to_data(self, data, dtype="B"):
        """
        将十六进制字符串解析为元组
        :param data: 十六进制字符串（可含任意空白分隔）
        :param sep_bytes: API保留参数，解析时自动过滤所有空白，保持接口对称
        :param dtype: 数据类型标识，默认 'B'
        :return: 解析后的整数元组（有符号类型自动转补码）
        """
        if not isinstance(data, str):
            raise TypeError("data must be a string")
        if dtype not in sysType.DTYPE_SIZES:
            raise ValueError("Unsupported dtype: {}".format(dtype))

        size = sysType.DTYPE_SIZES[dtype]
        width = size * 2  # 单个元素预期的 HEX 字符数

        # 移除所有空白字符（兼容空格、换行、制表符等日志格式）
        clean_hex = (
            data.replace(" ", "")
            .replace("\n", "")
            .replace("\r", "")
            .replace("\t", "")
            .upper()
        )

        if len(clean_hex) == 0:
            return tuple()
        if len(clean_hex) % width != 0:
            raise ValueError(
                "Hex length not aligned with dtype width ({} chars per item)".format(
                    width
                )
            )

        bits = 8 * size
        max_val = 1 << bits
        half_max = 1 << (bits - 1)
        is_signed = dtype in ("b", "h", "i", "l", "q")

        res = []
        for i in range(0, len(clean_hex), width):
            chunk = clean_hex[i : i + width]
            try:
                val = int(chunk, 16)
            except ValueError:
                raise ValueError("Invalid hex sequence: '{}'".format(chunk))

            # 有符号类型自动进行符号扩展（C 语言兼容行为）
            if is_signed and val >= half_max:
                val -= max_val
            res.append(val)

        return res

    def data_to_str(self, data):
        """
        将list/tuple/bytes转为字符串
        :param data: 待解析的数据内容
        """
        if isinstance(data, str):
            return data
        
        if isinstance(data, int):
            data = bytes([data])
        elif not isinstance(data, (list, tuple, bytes, bytearray)):
            raise TypeError("Unsupported send data type")
        return "".join([chr(element) for element in data])


# 辅助工具
def getUtils():
    return utils()
