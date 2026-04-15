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
    def __init__(self, fun, arg, loop):
        self._fun = fun
        self._arg = arg
        self._loop = loop

        self._timer = osTimer()
        self._timer_started = False

    def _timer_cb(self, arg):
        try:
            self._fun(*self._arg)
        except Exception as err:
            log.error("timer_cb", err)

        if not self._loop:  # 单次执行后删除
            self.stop()

    # 启动计时
    def start(self, interval):
        if self._timer_started:
            self.stop(False)
        self._timer.start(interval, 1 if self._loop else 0, self._timer_cb)
        self._timer_started = True

    # 停止计时
    def stop(self, clear=True):
        if self._timer_started:
            self._timer.stop()
            self._timer_started = False
        if clear:
            self._timer.delete_timer()
            log.info("stop", "clear ok")


# 定时任务
def startTimer(fun, *arg, interval=1000, loop=True):
    tm = timer(fun, arg, loop)
    tm.start(interval)
    return tm
