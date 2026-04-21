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
import ubinascii

from misc import Power
from machine import RTC
from .znlib_const import sysInfo, sysType
from .znlib_log import getLogger
from .znlib_base import Singleton, BaseError


class utils(Singleton):
    log = getLogger("utils")

    # 记录异常并抛出
    @classmethod
    def raise_error(cls, tag, msg):
        cls.log.error(tag, msg)
        raise BaseError(msg)

    # RTC时钟
    @classmethod
    def now_rtc(cls):
        rtc = RTC().datetime()
        return "{}-{:02d}-{:02d}".format(*rtc[0:3]) + " {:02d}:{:02d}:{:02d}".format(
            *rtc[4:7]
        )

    # 打印系统信息
    @classmethod
    def print_moduble_info(cls):
        cls.log.info("=" * 42)
        try:
            import usys as sys
        except ImportError:
            import sys
        vm = sys.implementation
        cls.log.info(" python   : {}".format(sys.version))
        cls.log.info(" vm_ver   : {}.{}.{}".format(vm[1][0], vm[1][1], vm[1][2]))

        cls.log.info(" pro_ver  : {}".format(sysInfo.PROJECT_VERSION))
        cls.log.info(" project  : {}".format(sysInfo.PROJECT_NAME))
        cls.log.info(" firmware : {}".format(sysInfo.DEVICE_FIRMWARE_NAME))
        cls.log.info(" firm_ver : {}".format(sysInfo.DEVICE_FIRMWARE_VERSION))
        cls.log.info(" dev_imei : {}".format(sysInfo.DEVICE_IMEI))
        cls.log.info(" dev_sn   : {}".format(sysInfo.DEVICE_SN))

        cls.log.info(" free_ram : {} Bytes".format(gc.mem_free()))
        cls.log.info(" free_rom : {} Bytes".format(_thread.get_heap_size()))
        usr = uos.statvfs("/usr")
        cls.log.info(" free_usr : {} Bytes".format(usr[0] * usr[3]))
        cls.log.info(" vbat     : {} mV".format(Power.getVbatt()))

        cls.log.info(" OPERATOR : {} ".format(net.operatorName()))
        cfg = sysType.NET_CONFIG.get(net.getConfig()[0], "UNKNOWN")
        cls.log.info(" NET      : {} ".format(cfg))
        cls.log.info(" CSQ      : {} ".format(net.csqQueryPoll()))
        cls.log.info(" RTC      : {} ".format(cls.now_rtc()))
        cls.log.info("=" * 42)

    # 文件是否存在
    @classmethod
    def file_exists(cls, file_full):
        try:
            stat = uos.stat(file_full)
            return stat[-4] >= 0  # 大小
        except:
            return False

    @classmethod
    def data_to_hex(cls, data, sep_bytes=True, dtype="B"):
        """
        将 list/tuple 转换为十六进制字符串
        :param data: list 或 tuple（元素为 int 或 bytes/bytearray）
        :param sep_bytes: True 时按单字节(2位HEX)插入空格分隔
        :param dtype: 数据类型标识，默认 'B' (unsigned char)
        :return: 十六进制字符串
        """
        if isinstance(data, str):
            dtype = "B"
            data = data.encode("utf-8")
        elif not isinstance(data, (list, tuple)):
            cls.raise_error("data_to_hex", "data must be a list or tuple")
        if dtype not in sysType.DTYPE_SIZES:
            cls.raise_error("data_to_hex", "Unsupported dtype: {}".format(dtype))

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

    @classmethod
    def hex_to_data(cls, data, dtype="B"):
        """
        将十六进制字符串解析为元组
        :param data: 十六进制字符串（可含任意空白分隔）
        :param sep_bytes: API保留参数，解析时自动过滤所有空白，保持接口对称
        :param dtype: 数据类型标识，默认 'B'
        :return: 解析后的整数元组（有符号类型自动转补码）
        """
        if not isinstance(data, str):
            cls.raise_error("hex_to_data", "data must be a string")
        if dtype not in sysType.DTYPE_SIZES:
            cls.raise_error("hex_to_data", "Unsupported dtype: {}".format(dtype))

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
            cls.raise_error(
                "hex_to_data",
                "Hex length not aligned with dtype width ({} chars per item)".format(
                    width
                ),
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
                cls.raise_error(
                    "hex_to_data", "Invalid hex sequence: '{}'".format(chunk)
                )

            # 有符号类型自动进行符号扩展（C 语言兼容行为）
            if is_signed and val >= half_max:
                val -= max_val
            res.append(val)

        return res

    @classmethod
    def data_to_str(cls, data):
        """
        将list/tuple/bytes转为字符串
        :param data: 待解析的数据内容
        """
        if isinstance(data, str):
            return data

        if isinstance(data, int):
            data = bytes([data])
        elif not isinstance(data, (list, tuple, bytes, bytearray)):
            cls.raise_error("data_to_str", "Unsupported send data type")
        return "".join([chr(element) for element in data])

    @classmethod
    def encode_base64(cls, data):
        """
        将str/list/tuple/bytes统一转换为bytes后再进行Base64编码。
        :param data: 待编码的数据 (str, list, tuple, or bytes)
        :return: Base64编码后的bytes对象
        :raises TypeError: 如果输入类型不受支持
        :raises ValueError: 如果list/tuple中包含无法转换为字节的元素
        """
        if isinstance(data, bytes):
            # 直接路径：输入已是bytes，无需转换
            byte_data = data
        elif isinstance(data, str):
            # 字符串路径：使用UTF-8编码转换为bytes
            byte_data = data.encode("utf-8")
        elif isinstance(data, (list, tuple)):
            # 容器路径：将容器内的整数转换为bytes
            # 只有在0-255范围内的整数才能被视作合法的字节值
            byte_list = []
            for item in data:
                if not isinstance(item, int) or not (0 <= item < 256):
                    cls.raise_error(
                        "encode_base64",
                        "list or tuple elements-{} must be integers in range [0, 255].".format(
                            item
                        ),
                    )
                byte_list.append(item)
            byte_data = bytes(byte_list)
        else:
            # 其他不支持的类型
            cls.raise_error(
                "encode_base64",
                "Unsupported data type for encoding: {}".format(type(data).__name__),
            )

        # 调用ubinascii模块进行Base64编码
        # b2a_base64返回值已包含换行符 [[5]]
        return ubinascii.b2a_base64(byte_data)

    @classmethod
    def decode_base64(cls, base64_str):
        """
        将Base64编码的字符串解码为原始的字节数据。
        :param base64_str: Base64编码的字符串
        :return: 解码后的bytes对象
        :raises ValueError: 如果输入的字符串格式不正确，不符合Base64规范
        """
        # 直接调用ubinascii模块进行解码
        # 输入必须是有效的Base64字符串 [[1,2]]
        return ubinascii.a2b_base64(base64_str)
