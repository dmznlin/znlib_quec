#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-14
#  描述：参数配置管理器
#
import ujson
import _thread
from usr.znlib.utils import utils
from usr.znlib.log import getLogger
from usr.znlib.base import Singleton, option_lock


class settings(object):
    log = getLogger("settings")

    def __init__(self, setting_name):
        # 规避模块传输异常,使用 txt 扩展名
        self.setting_file = "/usr/znlib/{}.txt".format(setting_name)
        self.settings = {}

    def __save_config(self):
        try:
            with open(self.setting_file, "w") as f:
                ujson.dump(self.settings, f)
            return True
        except Exception as e:
            self.log.error("save", "{}:{}".format(self.setting_file, e))
            return False

    def __remove_config(self):
        try:
            uos.remove(self.setting_file)
            return True
        except Exception as e:
            self.log.error("remove", "file:{} error:{}".format(self.setting_file, e))
            return False

    @option_lock(Singleton.sync_lock)
    def load(self):
        if utils.file_exists(self.setting_file):
            try:
                with open(self.setting_file, "r") as f:
                    self.settings = ujson.load(f)
                    return True
            except Exception as e:
                self.log.error("load", "file:{} error:{}".format(self.setting_file, e))
        else:
            self.log.error("load", "{} not found".format(self.setting_file))
        return False

    @option_lock(Singleton.sync_lock)
    def get(self):
        return self.settings

    @option_lock(Singleton.sync_lock)
    def set(self, val):
        self.settings = val
        return self.__save_config()

    @option_lock(Singleton.sync_lock)
    def save(self):
        return self.__save_config()

    @option_lock(Singleton.sync_lock)
    def remove(self):
        return self.__remove_config()


# 加载配置
def loadConfig(name):
    cfg = settings(name)
    return cfg, cfg.load()
