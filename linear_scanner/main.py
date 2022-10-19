from time import sleep_ms
from _thread import start_new_thread
from sys import stdin
import utime
from machine import Pin
import select


pin_a = Pin(2, Pin.OUT)
pin_b = Pin(3, Pin.OUT)
pin_c = Pin(4, Pin.OUT)
pin_d = Pin(5, Pin.OUT)

pin_a.low()
pin_b.low()
pin_c.low()
pin_d.low()

L1 = Pin(0, Pin.OUT)            # LEFT Laser

LED = Pin(25, Pin.OUT)
LED.off()


def get_arr_value(arr, i):
    try:
        val = arr[i]
    except IndexError as e:
        val = 'none'
    return val


def get_int_value(in_str):
    try:
        ret = int(in_str)
    except ValueError as e:
        ret = 0
    return ret


def process_msg(a, d, v):
    global rpm

    success = False
    if a == 1:
        # Laser 1 OFF
        L1.off()
        LED.off()
        success = True
    elif a == 2:
        # Laser 1 ON
        L1.on()
        LED.on()
        success = True
    elif a == 6:
        if v > 0:
            cw = d == 0
            step(v, cw)
            success = True

    return success


# Rotate in clockwise, full step
# step      1 2 3 4
#           -------
# pin_a     1 1 0 0
# pin_b     0 1 1 0
# pin_c     0 0 1 1
# pin_d     1 0 0 1


def step(steps, cw):

    for s in range(0, steps):
        # step 1
        pin_a.high()
        pin_b.low()
        pin_c.low()
        pin_d.high()
        utime.sleep_ms(5)

        # step 2
        pin_a.high()
        pin_b.high()
        pin_c.low()
        pin_d.low()
        utime.sleep_ms(5)

        # step 3
        pin_a.low()
        pin_b.high()
        pin_c.high()
        pin_d.low()
        utime.sleep_ms(5)

        # step 4
        pin_a.low()
        pin_b.low()
        pin_c.high()
        pin_d.high()
        utime.sleep_ms(5)

    pin_a.low()
    pin_b.low()
    pin_c.low()
    pin_d.low()


def process_byte_msg():
    global msg_int, comp
    msg_id = msg_int >> 22
    a = ((msg_int >> 16) & 0x003c) >> 2
    d = (msg_int >> 16) & 0x0003
    v = msg_int & 0xffff
    success = process_msg(a, d, v)

    ret = msg_id << 6
    if success:
        ret += 1
        print(str(ret))
    else:
        print(a, d, v)


comp = True
pulse_w = 200
rpm = 5
fspr = 200              # motor full steps per rev
ms = 16                 # driver micro steps setting
ppr = fspr * ms
mps = 0

poll = select.poll()
poll.register(stdin, select.POLLIN)

msg_int = 0

while True:

    if poll.poll(0):
        msg_int = int(stdin.readline(10))
        process_byte_msg()

    sleep_ms(10)
