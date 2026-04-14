#
#  作者：dmzn@163.com 2026-04-13
#  描述：带时间、标签的日志
#
# -*- coding: utf-8 -*-
import utime
from usr.znlib.const import SysInfo


class Logger:
    def __init__(self, name):
        self.name = name
        self.__debug = SysInfo.DEBUG
        self.__level = "D"
        self.__level_code = {
            "D": 0,  # debug
            "I": 1,  # info
            "W": 2,  # warn
            "E": 3,  # error
            "C": 4,  # critical
        }

    def get_debug(self):
        return self.__debug

    def set_debug(self, debug):
        if isinstance(debug, bool):
            self.__debug = debug
            return True
        return False

    def get_level(self):
        return self.__level

    def set_level(self, level):
        if self.__level_code.get(level) is not None:
            self.__level = level
            return True
        return False

    def log(self, name, level, *message):
        if self.__debug is False:
            if self.__level_code[level] < self.__level_code[self.__level]:
                return

        if hasattr(utime, "strftime"):
            if len(message) < 2:
                print(
                    "[{}]".format(utime.strftime("%Y-%m-%d %H:%M:%S")),  # type: ignore
                    "{}".format(level) + "/{}".format(name),
                    *message
                )
            else:
                print(
                    "[{}]".format(utime.strftime("%Y-%m-%d %H:%M:%S")),  # type: ignore
                    "{}".format(level) + "/{}".format(name) + ".{}".format(message[0]),
                    *message[1:]
                )
        else:
            t = utime.localtime()
            if len(message) < 2:
                print(
                    "[{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}]".format(*t),
                    "{}".format(level) + "/{}".format(name),
                    *message
                )
            else:
                print(
                    "[{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}]".format(*t),
                    "{}".format(level) + "/{}".format(name) + ".{}".format(message[0]),
                    *message[1:]
                )

    def critical(self, *message):
        self.log(self.name, "C", *message)

    def error(self, *message):
        self.log(self.name, "E", *message)

    def warn(self, *message):
        self.log(self.name, "W", *message)

    def info(self, *message):
        self.log(self.name, "I", *message)

    def debug(self, *message):
        self.log(self.name, "D", *message)


def getLogger(name):
    return Logger(name)
