from time import sleep_ms
from _thread import start_new_thread
from sys import stdin
import utime
from machine import Pin


PUL = Pin(18, Pin.OUT)          # Motor pulse
DIR = Pin(19, Pin.OUT)          # Motor direction
ENBL = Pin(20, Pin.OUT)          # Motor enable

L1 = Pin(16, Pin.OUT)            # LEFT Laser
L2 = Pin(17, Pin.OUT)            # RIGHT laser

LED = Pin(25, Pin.OUT)
LED.off()


class USB(object):
    def __init__(self):
        #
        # global variables to share between both threads/processors
        #
        self.bufferSize = 1024  # size of circular self.buffer to allocate
        self.buffer = [' '] * self.bufferSize  # circuolar incomming USB serial data self.buffer (pre fill)
        self.bufferEcho = False  # USB serial port echo incooming characters (True/False)
        self.bufferNextIn, self.bufferNextOut = 0, 0  # pointers to next in/out character in circualr self.buffer
        self.terminateThread = False  # tell 'self.bufferSTDIN' function to terminate (True/False)

    def buffer_stdin(self):
        while True:  # endless loop
            if self.terminateThread:  # if requested by main thread ...
                break  # ... exit loop
            self.buffer[self.bufferNextIn] = stdin.read(1)  # wait for/store next byte from USB serial
            if self.bufferEcho:  # if echo is True ...
                print(self.buffer[self.bufferNextIn], end='')  # ... output byte to USB serial
            self.bufferNextIn += 1  # bump pointer
            if self.bufferNextIn == self.bufferSize:  # ... and wrap, if necessary
                self.bufferNextIn = 0

    def get_byte_buffer(self):
        if self.bufferNextOut == self.bufferNextIn:  # if no unclaimed byte in self.buffer ...
            return ''  # ... return a null string
        n = self.bufferNextOut  # save current pointer
        self.bufferNextOut += 1  # bump pointer
        if self.bufferNextOut == self.bufferSize:  # ... wrap, if necessary
            self.bufferNextOut = 0
        return self.buffer[n]  # return byte from self.buffer


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


def process_msg(data):
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


def step(steps, cw):
    if cw:
        DIR.off()
    else:
        DIR.on()
    for n in range(0, steps):
        PUL.on()
        utime.sleep_ms(pulse_w)
        PUL.off()
        utime.sleep_ms(mps)


def set_mps():
    global mps
    mps = int(60000000 / rpm / ppr) - pulse_w


pulse_w = 200
rpm = 5
fspr = 200              # motor full steps per rev
ms = 16                 # driver micro steps setting
ppr = fspr * ms
mps = 0

set_mps()

usb = USB()
stdin_thread = start_new_thread(usb.buffer_stdin, ())

while True:

    buffCh = usb.get_byte_buffer()  # get a byte if it is available?
    s = ""
    while buffCh:
        s += ''.join([b for b in buffCh])
        buffCh = usb.get_byte_buffer()  # get a byte if it is available?
    if len(s) > 0:
        process_msg(s)

    sleep_ms(50)
