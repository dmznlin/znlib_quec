#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-22
#  描述：线程相关
#
import _thread
from .znlib_base import baseError
from .znlib_waiter import getWaiter


class waitResult(object):
    """支持超时等待的执行结果"""

    def __init__(self):
        self._result = None
        self._error = None
        self._waiter = getWaiter()

    def set(self, res=None, err=None):
        self._result = res
        self._error = err
        self._waiter.wakup()

    def get(self, timeout=0):
        if self._waiter.waitFor(timeout):
            return self._result, self._error
        else:
            return None, baseError("get result timeout.")


class innerThread(object):
    """将任务打包至线程"""

    def __init__(self, fun, args, kwargs=None):
        self._fun = fun
        self._args = args
        self._kwargs = kwargs or {}
        self._ident = None

    def __repr__(self):
        return "<Thread {}>".format(self._ident)

    def is_running(self):
        if self._ident is None:
            return False
        else:
            return _thread.threadIsRunning(self._ident)

    def start(self, wait_result=False):
        if self.is_running():
            return None
        result = None

        if wait_result:
            result = waitResult()
        self._ident = _thread.start_new_thread(self.run, (result,))
        return result

    def stop(self):
        if self.is_running():
            _thread.stop_thread(self._ident)
            self._ident = None

    def run(self, result):
        try:
            rv = self._fun(*self._args, **self._kwargs)
        except Exception as e:
            usys.print_exception(e)
            if result:
                result.set(err=e)
        else:
            if result:
                result.set(res=rv)

    @property
    def ident(self):
        return self._ident


def startThread(fun, *arg, wait_result=False):
    """
    启动线程任务
    :param fun: 回调函数
    :param arg: 回调参数
    :param wait_result: 等待执行结果
    """
    it = innerThread(fun, arg)
    return it, it.start(wait_result)
