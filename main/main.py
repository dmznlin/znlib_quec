# -*- coding: utf-8 -*-
from usr.znlib.const import SysInfo
SysInfo.DEBUG = True   
                
import utime
from usr.znlib.log import getLogger

def test_log():
    log = getLogger("test")
    # log.set_debug(True)
    log.set_level("W")

    for i in range(1, 10):
        log.info("tag", "hello", "word")


print(SysInfo.DEBUG)
print(SysInfo.DEVICE_FIRMWARE_VERSION)
# 日志

test_log()
