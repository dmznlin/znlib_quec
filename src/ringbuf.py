#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  作者：dmzn@163.com 2026-04-16
#  描述：环形缓冲区
#
from usr.znlib.const import sysType
from usr.znlib.utils import utils


class RingBuffer:
    """
    环形缓冲区（适配 QuecPython / EC600CN）
    特性：
      - 支持 dtype 类型约束，默认 'B' (unsigned char, 1字节)
      - 满覆盖策略，固定容量，零动态内存分配
      - 批量 push/pop 内联优化，避免函数调用与取模开销
    """

    def __init__(self, capacity, dtype="B"):
        if dtype not in sysType.DTYPE_SIZES:
            raise ValueError(
                "Unsupported dtype: '{}'. Must be one of {}".format(
                    dtype, list(sysType.DTYPE_SIZES.keys())
                )
            )

        self.dtype = dtype
        self.capacity = capacity
        self.buffer = [0] * capacity  # 预分配，统一用 0 初始化避免 None 类型判断
        self.head = 0
        self.tail = 0
        self.count = 0

    def push(self, data):
        """写入单条数据。满时自动覆盖最旧数据。"""
        self.buffer[self.tail] = data
        self.tail += 1
        if self.tail >= self.capacity:
            self.tail = 0
        if self.count < self.capacity:
            self.count += 1
        else:
            self.head += 1
            if self.head >= self.capacity:
                self.head = 0
        return True

    def push_batch(self, data):
        """批量写入数据。支持 list 或 tuple。"""
        if not isinstance(data, (list, tuple)):
            raise TypeError("Batch data must be a list or tuple")
        n = len(data)
        if n == 0:
            return 0

        if n >= self.capacity:
            # 数据量 >= 容量：直接覆盖整个缓冲区
            start = n - self.capacity
            for i in range(self.capacity):
                self.buffer[i] = data[start + i]
            self.head = 0
            self.tail = 0
            self.count = self.capacity
            return n

        for item in data:
            self.buffer[self.tail] = item
            self.tail += 1
            if self.tail >= self.capacity:
                self.tail = 0
            if self.count < self.capacity:
                self.count += 1
            else:
                self.head += 1
                if self.head >= self.capacity:
                    self.head = 0
        return n

    def pop(self):
        """读取并移除最旧数据。为空时返回 None。"""
        if self.count == 0:
            return None
        data = self.buffer[self.head]
        self.head += 1
        if self.head >= self.capacity:
            self.head = 0
        self.count -= 1
        return data

    def pop_batch(self, n, virtual=False):
        """
        批量取出数据。返回 list，数量不超过 n。
        :param virtual: 只取数据,不移动指针
        """
        if n <= 0:
            return []
        actual = n if n < self.count else self.count
        if actual == 0:
            return []

        res = [None] * actual
        idx = self.head
        for i in range(actual):
            res[i] = self.buffer[idx]
            idx += 1
            if idx >= self.capacity:
                idx = 0

        if not virtual:
            self.head = idx
            self.count -= actual
        return res

    def pick_range(self):
        """
        数据范围下标
        :param begin: 开始索引
        :param end: 索引上限(不包括)
        """
        if self.count == 0:
            return 0, 0
        return self.head, self.head + self.count

    def r_i(self, _index):
        """
        获取真实下标(read-index)
        :param _index: 下标值
        """
        if _index < self.capacity:
            return _index
        return _index % self.capacity

    def pick_move(self, _index):
        """
        移动至指定下标
        :param _index: 下标值
        """
        self.head = self.r_i(_index)
        if self.head <= self.tail:  # 未折返
            self.count = self.tail - self.head
        else:  # 数据折返
            self.count = self.capacity - self.head + self.tail

    def pick_data(self, start, end):
        """
        获取下标[start:end]的数据
        :param start,end: 下标,前闭后开
        """
        start = self.r_i(start)
        end = self.r_i(end)
        if start <= end:
            return self.buffer[start:end]

        res = self.buffer[start : self.capacity]
        res.extend(self.buffer[0 : self.r_i(end)])
        return res

    def print_hex(self, sep_bytes=True):
        """
        按 dtype 占用字节数打印十六进制，不足自动补 0
        :param sep_bytes: True=每字节(2位HEX)空格分隔; False=连续打印
        """
        if self.count == 0:
            return ""
        else:
            return utils.data_to_hex(
                self.pop_batch(self.count, True), sep_bytes, self.dtype
            )

    def is_empty(self):
        return self.count == 0

    def is_full(self):
        return self.count == self.capacity

    def size(self):
        return self.count

    def clear(self):
        self.head = 0
        self.tail = 0
        self.count = 0

    def __len__(self):
        return self.count
