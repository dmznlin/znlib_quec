# -*- coding: utf-8 -*-
from usr.znlib.const import SysInfo

SysInfo.DEBUG = True

import utime
from usr.znlib.log import getLogger

log = getLogger(__name__)


def test_log():
    # log.set_debug(True)
    log.set_level("W")

    for i in range(1, 5):
        log.error(i, "hello", "word")


print(SysInfo.DEBUG)
print(SysInfo.DEVICE_FIRMWARE_VERSION)

# 日志
test_log()

from usr.znlib.config import loadConfig

cfg = loadConfig("znlib")
print(cfg.get()["ntp"])
cfg = None

cfg = loadConfig("mqtt")
print(cfg.get()["subs"]["srv"])

from usr.znlib.waiter import getWaiter

waiter = getWaiter()
from usr.znlib.timer import startTimer


def wakeup(a):
    waiter.wakeup("hello")


tm = startTimer(lambda: waiter.wakeup("hello"),interval=100, loop=False)

wdt = waiter.waitFor(1200)

if wdt == None:
    log.warn("waitfor: timeout")
else:
    log.info("waitfor: " + str(wdt))
