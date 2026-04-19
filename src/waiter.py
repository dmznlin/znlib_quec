#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-15
#  描述：异步转同步
#
import osTimer
from queue import Queue
from usr.znlib.base import Singleton

class waiter(object):
    def __init__(self):
        self._queue = Queue(maxsize=1)
        self._timer = None

    # 计时结束
    def _timer_cb(self, arg):
        with Singleton.sync_lock:
            if self._queue.size() == 0:
                self._queue.put(None)

    # 开启等待
    def waitFor(self, timeout=0):
        with Singleton.sync_lock:
            while not self._queue.empty():
                data = self._queue.get()
        # clear singnal

        timer_started = False
        if timeout > 0:
            if self._timer == None:
                self._timer = osTimer()
            self._timer.start(timeout, 0, self._timer_cb)
            timer_started = True

        # 进入等待
        data = self._queue.get()
        if timer_started:
            self._timer.stop()
        return data

    # 唤醒等待
    def wakeup(self, data=None):
        if data == None:
            data = 0
        with Singleton.sync_lock:
            if self._queue.size() == 0:
                self._queue.put(data)


# 等待对象
def getWaiter():
    return waiter()
