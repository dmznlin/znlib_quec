#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-14
#  描述：基础类
#
import _thread


def option_lock(thread_lock):
    """Function thread lock decorator"""

    def function_lock(func):
        def wrapperd_fun(*args, **kwargs):
            with thread_lock:
                return func(*args, **kwargs)

        return wrapperd_fun

    return function_lock


class BaseError(Exception):
    """Exception base class"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Singleton(object):
    """Singleton base class"""

    _instance_lock = _thread.allocate_lock()

    def __init__(self, *args, **kwargs):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            Singleton.instance = {}

        if str(cls) not in Singleton.instance.keys():
            with Singleton._instance_lock:
                _instance = super().__new__(cls)
                Singleton.instance[str(cls)] = _instance

        return Singleton.instance[str(cls)]
