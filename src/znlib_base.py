#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-14
#  描述：基础类
#
import _thread


class locker(object):
    """同步锁定"""

    def __init__(self):
        self._lock = _thread.allocate_lock()
        self._owner = None

    def __del__(self):
        _thread.delete_lock(self._lock)

    def __enter__(self):
        return self.enter()

    def __exit__(self, *args, **kwargs):
        self.leave()

    @property
    def owner(self):
        return self._owner

    @property
    def is_owned(self):
        return self._lock.locked() and self._lock.owner == _thread.get_ident()

    def enter(self):
        flag = self._lock.acquire()
        self._owner = _thread.get_ident()
        return flag

    def leave(self):
        self._owner = None
        return self._lock.release()

    def locked(self):
        return self._lock.locked()


def option_lock(thread_lock):
    """Function thread lock decorator"""

    def function_lock(func):
        def wrapperd_fun(*args, **kwargs):
            with thread_lock:
                return func(*args, **kwargs)

        return wrapperd_fun

    return function_lock


class baseError(Exception):
    """异常基类"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class singleton(object):
    """单实例基类"""

    # 低使用率公用同步锁
    sync_lock = locker()

    def __init__(self, *args, **kwargs):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            Singleton.instance = {}

        with Singleton.sync_lock:
            if str(cls) not in Singleton.instance.keys():
                _instance = super().__new__(cls)
                Singleton.instance[str(cls)] = _instance

        return Singleton.instance[str(cls)]
