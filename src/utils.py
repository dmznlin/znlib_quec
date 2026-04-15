#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-15
#  描述：辅助工具类
#
import gc
import net
import _thread
import checkNet

from misc import Power
from machine import RTC
from usr.znlib.const import sysInfo
from usr.znlib.log import getLogger
from usr.znlib.base import Singleton


class utils(Singleton):
    log = getLogger("utils")

    # 打印系统信息
    def print_moduble_info(self):
        self.log.info("=" * 42)
        self.log.info(" project  : {}".format(sysInfo.PROJECT_NAME))
        self.log.info(" pro_ver  : {}".format(sysInfo.PROJECT_VERSION))
        self.log.info(" firmware : {}".format(sysInfo.DEVICE_FIRMWARE_NAME))
        self.log.info(" firm_ver : {}".format(sysInfo.DEVICE_FIRMWARE_VERSION))

        self.log.info(" free_ram : {} Bytes".format(gc.mem_free()))
        self.log.info(" free_rom : {} Bytes".format(_thread.get_heap_size()))
        self.log.info(" vbat     : {} mV".format(Power.getVbatt()))
        self.log.info(" CSQ      : {} ".format(net.csqQueryPoll()))
        self.log.info("=" * 42)


# 辅助工具
def getUtils():
    return utils()
