#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-15
#  描述：异步转同步
#
#  提示: waiter中使用了定时器,切勿在计时器中使用.
#
import osTimer
from queue import Queue
from .znlib_base import locker


class waiter(object):
    def __init__(self):
        self._queue = Queue(maxsize=1)
        self._timer = None
        self._locker = locker()

    # 计时结束
    def _timer_cb(self, arg):
        with self._locker:
            if self._queue.empty():
                self._queue.put(None)

    # 开启等待
    def waitFor(self, timeout=0):
        if timeout > 0:
            if self._timer is None:
                self._timer = osTimer()
            self._timer.start(timeout, 0, self._timer_cb)

        # 进入等待
        data = self._queue.get()
        if timeout > 0:
            self._timer.stop()
        return data

    # 唤醒等待
    def wakeup(self, data=None):
        if data == None:
            data = 0
        with self._locker:
            if self._queue.empty():
                self._queue.put(data)


# 等待对象
def getWaiter():
    return waiter()
