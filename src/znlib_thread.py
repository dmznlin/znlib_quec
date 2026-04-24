#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-22
#  描述：线程相关
#
import usys
import _thread
from .znlib_waiter import getWaiter
from .znlib_base import baseError, locker, singleton


class waitResult(object):
    """支持超时等待的执行结果"""

    def __init__(self):
        self._result = None
        self._error = None
        self._waiter = getWaiter()

    def set(self, res=None, err=None):
        self._result = res
        self._error = err
        self._waiter.wakeup()

    def get(self, timeout=0):
        if self._waiter.waitFor(timeout) is None:
            return None, baseError("get result timeout.")
        else:
            return self._result, self._error


class innerThread(object):
    """将任务打包至线程"""

    def __init__(self, fun, args=(), kwargs=None):
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
            if result:
                result.set(res=rv)
        except Exception as e:
            usys.print_exception(e)
            if result:
                result.set(err=e)

    @property
    def ident(self):
        return self._ident


class jobThread(singleton):
    """
    处理异步小事务的线程
    """

    def __init__(self):
        if hasattr(self, "_initialized"):
            return  # 已初始化
        self._initialized = True

        self._jobs = dict()
        self._lock = locker()
        self._waiter = getWaiter()
        self._thread = innerThread(self._do_job)

    def run(self, fun, *arg):
        with self._lock:
            self._jobs[fun] = arg

        self._thread.start()
        self._waiter.wakeup()

    def _do_job(self):
        while True:
            fun = None
            arg = ()
            with self._lock:
                if len(self._jobs) > 0:
                    item = self._jobs.popitem()
                    fun = item[0]
                    arg = item[1]

            if not fun is None:
                try:
                    fun(*arg)
                except Exception as e:
                    usys.print_exception(e)

            with self._lock:
                num = len(self._jobs)
            if num < 1:  # 进入等待
                self._waiter.waitFor(5000)


def jobs():
    """
    启动作业线程
    """
    return jobThread()


def startThread(fun, *arg, wait_result=False):
    """
    启动线程任务
    :param fun: 回调函数
    :param arg: 回调参数
    :param wait_result: 等待执行结果
    """
    it = innerThread(fun, arg)
    return it, it.start(wait_result)
