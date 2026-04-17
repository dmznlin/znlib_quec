# -*- coding: utf-8 -*-
from usr.znlib.const import sysInfo

sysInfo.DEBUG = True

import utime
from usr.znlib.log import getLogger

log = getLogger("main")


def test_log():
    # log.set_debug(True)
    log.set_level("W")

    for i in range(1, 5):
        log.info(i, "hello", "word")


print(sysInfo.DEBUG)
print(sysInfo.DEVICE_FIRMWARE_VERSION)

# 日志
test_log()

from usr.znlib.config import loadConfig

cfg, ok = loadConfig("znlib")
if ok:
    print(cfg.get()["ntp"])
    cfg = None

cfg, ok = loadConfig("mqtt")
if ok:
    print(cfg.get()["subs"]["srv"])

from usr.znlib.waiter import getWaiter

waiter = getWaiter()
from usr.znlib.timer import startTimer

tm = startTimer(lambda: waiter.wakeup("hello"), interval=100, times=1)

wdt = waiter.waitFor(1200)

if wdt == None:
    log.warn("waitfor: timeout")
else:
    log.info("waitfor: " + str(wdt))

counter = 0


def count():
    global counter
    counter = counter + 1
    print(counter)


tm = startTimer(count, interval=100, times=5)
import utime

utime.sleep(1)

from usr.znlib.utils import getUtils

utils = getUtils()
utils.print_moduble_info()

if utils.file_exists("/usr/znlib/null.txt"):
    log.info("file exists")
else:
    log.warn("file not exists")

log.info(utils.data_to_str("Hello"))

l_a = [1, 2, 3, 4]
log.info(l_a)
l_a[1] = 5
log.info(l_a)

l_b = [1] * 5
log.info(l_b)

# 1. 基础转换 (dtype='B' 1字节)
raw = [0x1, 0xFF, 0x0A, 0x88]
hex_str = utils.data_to_hex(raw, sep_bytes=True)
print("data_hex:", hex_str)  # 输出: 01FF 0A88

# 2. 反向解析
parsed = utils.hex_to_data("01FF 0A88", dtype="B")
print("hex_data:", parsed)  # 输出: (1, 255, 10, 136)

# 3. 多字节类型 (dtype='H' 2字节无符号)
multi = [0x1234, 0xABCD, 0xFFFF]
hex_multi = utils.data_to_hex(multi, sep_bytes=False, dtype="H")
print("16bit hex:", hex_multi)  # 输出: 1234ABCDFFFF

# 4. 有符号自动补码 (dtype='l' 4字节有符号)
signed_hex = "FFFFFFFF 00000001 80000000"
signed_tuple = utils.hex_to_data(signed_hex, dtype="l")
print("signed parse:", signed_tuple)  # 输出: (-1, 1, -2147483648)

# 5. 字节流混合输入
mixed = [0x01, b"\xaa\xbb", 0xCC]
print("mixed hex:", utils.data_to_hex(mixed, dtype="B"))  # 输出: 01AABBCC

from usr.znlib.ringbuf import RingBuffer

# 1. 默认 dtype='B' (1字节)
rb8 = RingBuffer(8, dtype="B")
rb8.push_batch([0x1, 0xFF, 0xA, 0x0])
print("dtype=B (1字节):")
print(rb8.print_hex(sep_bytes=False))  # 输出: 01FF0A00
print(rb8.print_hex(sep_bytes=True))  # 输出: 01FF 0A00

# 2. 修改 dtype='H' (2字节，无符号短整型)
rb16 = RingBuffer(6, dtype="H")
rb16.push_batch([0x1, 0xABCD, 0xFF, 0x1234])
print("\ndtype=H (2字节):")
print(rb16.print_hex(sep_bytes=False))  # 输出: 0001ABCD00FF1234
print(rb16.print_hex(sep_bytes=True))  # 输出: 0001 ABCD 00FF 1234

# 3. 修改 dtype='l' (4字节，有符号长整型)
rb32 = RingBuffer(3, dtype="l")
rb32.push_batch([-1, 0xDEADBEEF, 0x1])
print("\ndtype=l (4字节):")
print(rb32.print_hex(sep_bytes=False))  # 输出: FFFFFFFFDEADBEEF00000001
print(rb32.print_hex(sep_bytes=True))  # 输出: FFFFFFFF DEADBEEF 00000001


def on_data(serial, rx):
    buf = utils.data_to_str(rx.pop_batch(rx.size()))
    log.info(buf)
    serial.send("modal: " + buf)


from usr.znlib.serial import getSerial

serial = getSerial(on_data)
serial.start()
