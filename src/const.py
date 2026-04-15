#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-13
#  描述：全局常量、变量
#
import uos
import modem


class sysInfo(object):
    # 项目描述
    PROJECT_NAME = "znlib-quec"
    PROJECT_VERSION = "1.0.1"

    # 固件描述
    DEVICE_FIRMWARE_NAME = uos.uname()[0].split("=")[1]
    DEVICE_FIRMWARE_VERSION = modem.getDevFwVersion()

    # 调试开关
    DEBUG = True
