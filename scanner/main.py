from time import sleep_ms
from _thread import start_new_thread
from sys import stdin
import utime
from machine import Pin
import select


PUL = Pin(18, Pin.OUT)          # Motor pulse
DIR = Pin(19, Pin.OUT)          # Motor direction
ENBL = Pin(20, Pin.OUT)          # Motor enable
ENBL.on()

L1 = Pin(16, Pin.OUT)            # LEFT Laser
L2 = Pin(17, Pin.OUT)            # RIGHT laser

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


def process_msg_old(data):
    global rpm, mps
    msgs = data.split(":")
    msg_id = get_arr_value(msgs, 0)
    msg = get_arr_value(msgs, 1)

    found = False
    if msg == "L10":
        # Laser 1 OFF
        L1.off()
        LED.off()
        found = True
    elif msg == "L11":
        # Laser 1 ON
        L1.on()
        LED.on()
        found = True
    elif msg == "L20":
        # Laser 2 OFF
        L2.off()
        found = True
    elif msg == "L21":
        # Laser 2 ON
        L2.on()
        found = True
    elif msg == "RPM":
        tmp = get_int_value(get_arr_value(msgs, 2))
        if tmp > 0:
            rpm = tmp
            set_mps()
            found = True
    elif msg == "STEP":
        tmp = get_int_value(get_arr_value(msgs, 2))
        if tmp > 0:
            steps = tmp
            cw = (get_arr_value(msgs, 3) == "CW")
            step(steps, cw)
            found = True

    if found:
        response = f"{msg_id}:{msg}:1:end"
    else:
        response = f"{msg_id}:{msg}:0:end"
    print(response)


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
    elif a == 3:
        # Laser 2 OFF
        L2.off()
        success = True
    elif a == 4:
        # Laser 2 ON
        L2.on()
        success = True
    elif a == 5:
        if v > 0:
            rpm = v
            set_mps()
            success = True
    elif a == 6:
        if v > 0:
            cw = d == 0
            step(v, cw)
            success = True

    return success


def step(steps, cw):
    if cw:
        DIR.off()
    else:
        DIR.on()
    for n in range(0, steps):
        PUL.on()
        utime.sleep_us(pulse_w)
        PUL.off()
        utime.sleep_us(mps)


def set_mps():
    global mps
    mps = int(60000000 / rpm / ppr) - pulse_w


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

set_mps()

poll = select.poll()
poll.register(stdin, select.POLLIN)

msg_int = 0

while True:

    if poll.poll(0):
        msg_int = int(stdin.readline(10))
        process_byte_msg()

    sleep_ms(10)
