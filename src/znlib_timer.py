#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-15
#  描述：计时器
#
import osTimer
from .znlib_log import getLogger
from .znlib_const import timerMode
from .znlib_base import singleton, locker


class jobTimer(singleton):
    """
    处理小事务的计时器
    """

    def __init__(self):
        if hasattr(self, "_initialized"):
            return  # 已初始化
        self._initialized = True

        self._jobs = dict()
        self._lock = locker()
        self._timer = osTimer()
        self._timer_started = False

        # 日志对象
        self.log = getLogger("jobTimer")

    def run(self, fun, *arg):
        with self._lock:
            self._jobs[fun] = arg

        if not self._timer_started:
            self._timer.start(
                1000,
                timerMode.PERIODIC,
                self._do_job,
            )

            self._timer_started = True

    def _do_job(self, arg):
        while True:
            fun = None
            arg = ()
            with self._lock:
                if len(self._jobs) > 0:
                    item = self._jobs.popitem()
                    fun = item[0]
                    arg = item[1]

            if fun is None:
                break
            try:
                fun(*arg)
            except Exception as e:
                self.log.error(":" * 32, obj=e)

        self._timer.stop()
        self._timer_started = False


def jobs():
    """
    启动作业计时器
    """
    return jobTimer()


def _del_timer(_timer):
    # 异步执行删除
    _timer.delete_timer()


class timer(object):
    def __init__(self, fun, arg, auto_clear):
        self._fun = fun
        self._arg = arg
        self._clear = auto_clear

        self._times = 0
        self._timer = osTimer()
        self._timer_started = False

        # 日志对象
        self.log = getLogger("timer")

    def _timer_cb(self, arg):
        try:
            self._fun(*self._arg)
        except Exception as e:
            self.log.error("timer_cb", "{}".format(e))

        if self._times > 0:  # 计次结束后删除
            self._times -= 1
            if self._times == 0:
                self.stop(False)
                if self._clear:
                    # 异步删除,避开在回调中自杀
                    jobs().run(_del_timer, self._timer)

    def start(self, interval, times=0):
        """
        启动计时器
        :param interval: 计时间隔
        :param times: 计时次数,记完关闭
        """
        if self._timer_started:
            self.stop(False)
        self._times = times
        self._timer.start(
            interval,
            timerMode.PERIODIC if times != 1 else timerMode.ONE_SHOT,
            self._timer_cb,
        )
        self._timer_started = True

    # 停止计时
    def stop(self, clear=None):
        if self._timer_started:
            self._timer.stop()
            self._timer_started = False

        if clear is None:
            clear = self._clear
        if clear:
            self._timer.delete_timer()
            self.log.info("stop", "clear ok")


def startTimer(fun, *arg, interval=1000, auto_clear=True, times=0):
    """
    启动定时任务
    :param fun: 回调函数
    :param arg: 回调参数
    :param interval: 计时间隔,单位毫秒
    :param auto_clear: 计时结束清理对象
    :param times: 计时次数,0表示不限次数
    """
    tm = timer(fun, arg, auto_clear)
    tm.start(interval, times)
    return tm
