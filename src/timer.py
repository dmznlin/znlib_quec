#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-15
#  描述：计时器
#
import osTimer
from usr.znlib.log import getLogger

log = getLogger("timer")


class timer(object):
    def __init__(self, fun, arg):
        self._fun = fun
        self._arg = arg

        self._timer = osTimer()
        self.timer_started = False

    def _timer_cb(self, arg):
        try:
            self._fun(*self._arg)
        except Exception as err:
            log.error("timer_cb", err)

    # 启动
    def start(self, interval, loop):
        if self.timer_started:
            self.stop()
        self._timer.start(interval, 1 if loop else 0, self._timer_cb)
        self.timer_started = True

    # 停止
    def stop(self):
        if self.timer_started:
            self._timer.stop()
            self.timer_started = False


# 定时任务
def startTimer(fun, *arg, interval=1000, loop=True):
    tm = timer(fun, arg)
    tm.start(interval, loop)
    return tm
