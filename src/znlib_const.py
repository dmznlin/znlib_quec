#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-13
#  描述：全局常量、变量
#
import uos
import modem


class sysInfo:
    # 项目描述
    PROJECT_NAME = "znlib-quec"
    PROJECT_VERSION = "1.0.1"

    # 固件描述
    DEVICE_FIRMWARE_NAME = uos.uname()[0].split("=")[1]
    DEVICE_FIRMWARE_VERSION = modem.getDevFwVersion()

    # 设备标识
    DEVICE_IMEI = modem.getDevImei()
    DEVICE_SN = modem.getDevSN()

    # 调试开关
    DEBUG = True


class byteOrder:
    # 大端序列
    big = "big"
    # 小端序列
    little = "little"


class timerMode:
    # 单次
    ONE_SHOT = 0
    # 周期
    PERIODIC = 1


class msgType:
    # at 消息
    AT_MODE = 0
    # RFC1662协议
    RFC1662 = 1
    # SMS 消息
    SMS = 2
    # 客户端消息
    TCP_CLI = 3
    # 服务端消息
    TCP_SER = 4


class cmdMode:
    # 查询模式
    READ = "read"
    # 设置模式
    WRITE = "write"
    # 其他
    OTHER = "other"
    # active
    ACTIVE = "active"


class tcpMode:
    """
    模块TCP连接模式,客户端模式或服务端模式
    """

    CLIENT_MODE = 0
    SERVER_MODE = 1
    MIX_MODE = 2
    MAX_TCP_MODE = 3


class socketError:
    ERR_AGAIN = -1
    ERR_SUCCESS = 0
    ERR_NOMEM = 1
    ERR_PROTOCOL = 2
    ERR_INVAL = 3
    ERR_NO_CONN = 4
    ERR_CONN_REFUSED = 5
    ERR_NOT_FOUND = 6
    ERR_CONN_LOST = 7
    ERR_PAYLOAD_SIZE = 9
    ERR_NOT_SUPPORTED = 10
    ERR_UNKNOWN = 13
    ERR_ERRNO = 14


class socketState:
    STA_ERROR = -1
    STA_CLOSED = 0
    STA_LISTEN = 1
    STA_SYN_SENT = 2
    STA_SYN_RCVD = 3
    STA_ESTABLISHED = 4
    STA_FIN_WAIT_1 = 5
    STA_FIN_WAIT_2 = 6
    STA_CLOSE_WAIT = 7
    STA_CLOSING = 8
    STA_LAST_ACK = 9
    STA_TIME_WAIT = 10


class sysType:
    # 数据类型映射表
    DTYPE_SIZES = {
        "b": 1,  # signed char
        "B": 1,  # unsigned char
        "h": 2,  # signed short
        "H": 2,  # unsigned short
        "i": 2,  # signed int
        "I": 2,  # unsigned int
        "l": 4,  # signed long
        "L": 4,  # unsigned long
        "q": 8,  # signed long long
        "Q": 8,  # unsigned long long
        "f": 4,  # float (DEFAULT)
        "d": 8,  # double
    }

    # 网络模式及漫游配置
    NET_CONFIG = {
        0: "GSM",
        1: "UMTS",
        2: "GSM_UMTS(自动)",
        3: "GSM_UMTS(GSM 优先)",
        4: "GSM_UMTS(UMTS 优先)",
        5: "LTE",
        6: "GSM_LTE(自动)",
        7: "GSM_LTE(GSM 优先)",
        8: "GSM_LTE(LTE 优先)",
        9: "UMTS_LTE(自动)",
        10: "UMTS_LTE(UMTS 优先)",
        11: "UMTS_LTE(LTE 优先)",
        12: "GSM_UMTS_LTE(自动)",
        13: "GSM_UMTS_LTE(GSM 优先)",
        14: "GSM_UMTS_LTE(UMTS 优先)",
        15: "GSM_UMTS_LTE(LTE 优先)",
        16: "GSM_LTE(双链路)",
        17: "UMTS_LTE(双链路)",
        18: "GSM_UMTS_LTE(双链路)",
        19: "CATM，BG95系列支持",
        20: "GSM_CATM(GSM 优先)",
        21: "CATNB, BG95系列支持",
        22: "GSM_CATNB(GSM 优先)",
        23: "CATM_CATNB(CATM 优先)",
        24: "GSM_CATM_CATNB(GSM 优先)",
        25: "CATM_GSM(CATM 优先)",
        26: "CATNB_GSM(CATNB 优先)",
        27: "CATNB_CATM(CATNB 优先)",
        28: "GSM_CATNB_CATM(GSM 优先)",
        29: "CATM_GSM_CATNB(CATM 优先)",
        30: "CATM_CATNB_GSM(CATM 优先)",
        31: "CATNB_GSM_CATM(CATNB 优先)",
        32: "CATNB_CATM_GSM(CATNB 优先)",
        33: "CATNB_GSM(企标)",
    }
