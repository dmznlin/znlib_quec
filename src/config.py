#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-14
#  描述：参数配置管理器
#
import ujson
import ql_fs
import _thread
from usr.znlib.base import Singleton, option_lock


class Settings(object):

    def __init__(self, setting_name):
        self.setting_file = "/usr/znlib/{}.json".format(setting_name)
        self.settings = {}
        self.init()

    def __save_config(self):
        try:
            with open(self.setting_file, "w") as f:
                ujson.dump(self.settings, f)
            return True
        except:
            return False

    def __remove_config(self):
        try:
            uos.remove(self.setting_file)
            return True
        except:
            return False

    @option_lock(Singleton._instance_lock)
    def init(self):
        if ql_fs.path_exists(self.setting_file):
            with open(self.setting_file, "r") as f:
                self.settings = ujson.load(f)
                return True
        return False

    @option_lock(Singleton._instance_lock)
    def get(self):
        return self.settings

    @option_lock(Singleton._instance_lock)
    def set(self, val):
        self.settings = val
        return self.__save_config()

    @option_lock(Singleton._instance_lock)
    def save(self):
        return self.__save_config()

    @option_lock(Singleton._instance_lock)
    def remove(self):
        return self.__remove_config()


# 加载配置
def loadConfig(name):
    return Settings(name)
