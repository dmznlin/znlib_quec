#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-16
#  描述：串口通讯
#
import utime
import _thread
from machine import UART

from .znlib_base import locker
from .znlib_log import getLogger
from .znlib_waiter import getWaiter
from .znlib_config import loadConfig
from .znlib_ringbuf import RingBuffer


class uartSerial(object):
    def __init__(self, cfg):
        try:
            uart_port = getattr(UART, "UART%d" % int(cfg["uart"]))
            self.uart = UART(
                uart_port,
                cfg["baudrate"],
                cfg["databits"],
                cfg["parity"],
                cfg["stopbits"],
                cfg["flowctl"],
            )

            # init rs458 rx/tx pin
            rs485 = cfg["rs485_direction_pin"]
            if rs485 != "":
                rs485_pin = getattr(UART, "GPIO%d" % int(rs485))
                self.uart.control_485(rs485_pin, 1)

        except Exception as e:
            self.log.error("UART init failed: {}".format(e))
            return

        self.callback = cfg["callback"]
        self.resend = cfg["resend"]
        self.poll_interval = cfg["poll_interval_ms"]

        self._running = False
        self._tid = None
        self._err_count = 0

        # 环形缓冲(无符号字节)
        self.rx_buf = RingBuffer(cfg["rxbuf_size"], dtype="B")
        self.tx_buf = RingBuffer(cfg["txbuf_size"], dtype="B")

        # 同步锁定
        self.tx_lock = locker()

        # 等待对象
        self.waiter = getWaiter()

        # 日志对象
        self.log = getLogger("serial")

    def _rx_loop(self):
        # 单次刷 TX 最大字节数，防止大对象分配引发 GC 停顿
        MAX_TX_CHUNK = 128

        while self._running:
            try:
                # 1. 接收硬件数据
                n = self.uart.any()
                if n > 0:
                    chunk = self.uart.read(n)
                    if chunk and self.callback:
                        # 写入接收缓存
                        self.rx_buf.push_batch(tuple(chunk))

                        try:
                            self.callback(self, self.rx_buf)
                        except Exception as e:
                            self.log.error("rx_loop", "callback failed: {}".format(e))

                # 3. 自动刷 TX 缓存
                with self.tx_lock:
                    tx_size = self.tx_buf.size()
                    if tx_size > 0:
                        # 限制单次弹出量，保护嵌入式堆内存
                        send_len = MAX_TX_CHUNK if tx_size > MAX_TX_CHUNK else tx_size
                        tx_data = tuple(self.tx_buf.pop_batch(send_len, self.resend))
                        tx_bytes = bytes(tx_data)

                        # 发送并处理半写/超时情况
                        sent = self.uart.write(tx_bytes)
                        if self.resend and sent is not None:  # 处理重发
                            # 未发送完的数据保留在缓存中
                            self.tx_buf.pop_batch(sent)

                # 主动让出 CPU，维持 QuecPython PPP/TCP 协议栈调度
                utime.sleep_ms(self.poll_interval)

            except Exception as e:
                self.log.error("rx_loop", "{}".format(e))
                # 连续异常熔断，防止拖垮 Modem 协议栈
                self._err_count += 1
                if self._err_count > 10:
                    self._running = False
                utime.sleep_ms(50)

        # 退出信号
        self.waiter.wakeup()

    def start(self):
        if self._running:
            return
        self.rx_buf.clear()
        self.tx_buf.clear()  # 清理缓存

        self._running = True
        self._err_count = 0
        self._tid = _thread.start_new_thread(self._rx_loop, ())

    def stop(self):
        self._running = False
        self.waiter.waitFor(5000)  # 等待线程退出

    def send(self, data):
        """将数据推入 TX 缓冲，由后台线程统一发出（线程安全）"""
        if isinstance(data, int):
            data = bytes([data])
        elif isinstance(data, (list, tuple)):
            data = bytes(data)
        elif isinstance(data, str):
            data = data.encode("utf-8")
        elif not isinstance(data, (bytes, bytearray)):
            raise TypeError("Unsupported send data type")

        with self.tx_lock:
            self.tx_buf.push_batch(tuple(data))


def getSerial(fun, cfg=None):
    """
    返回一个串口通讯对象
    :param cfg: 配置名称或内容(字典)
    """

    # 默认配置
    _cfg = {
        "uart": 2,  # UART编号
        "baudrate": 115200,  # 波特率
        "databits": 8,  # 数据位
        "stopbits": 1,  # 停止位
        "parity": 0,  # 校验位
        "flowctl": 0,  # 硬件控制流
        "callback": None,  # 数据回调
        "resend": False,  # 重新发送
        "rxbuf_size": 64,  # 接收缓存
        "txbuf_size": 32,  # 发送缓存
        "poll_interval_ms": 100,  # 轮询间隔
        "rs485_direction_pin": "",  # 485翻转管脚
    }

    """
    参数说明:
    :param resend: 发送异常时,False直接丢弃,True放入发送缓存
    :param rxbuf_size,txbuf_size: 理想值为3倍数据,即可以缓存三份数据
    :param poll_interval_ms: 理想值为指令间隔的1/3,即每1秒收发一次数据时,间隔为330ms
    """

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

    _cfg["callback"] = fun
    return uartSerial(_cfg)
