import utime
from machine import Pin, UART


PUL = Pin(12, Pin.OUT)          # Motor pulse
DIR = Pin(13, Pin.OUT)          # Motor direction
ENBL = Pin(9, Pin.OUT)          # Motor enable

L1 = Pin(6, Pin.OUT)            # LEFT Laser
L2 = Pin(7, Pin.OUT)            # RIGHT laser

LED = Pin(25, Pin.OUT)
LED.off()


def process_msg(data):
    global rpm, mps
    msgs = data.split(":")
    msg_id = msgs[0]
    msg = ""
    response = f"{msg_id}"
    if len(msgs > 1):
        msg = msgs[1]
    if msg == "L10":
        # Laser 1 OFF
        response += ":laser1off"
        L1.off()
        LED.off()
    elif msg == "L11":
        # Laser 1 ON
        response += ":laser1on"
        L1.on()
        LED.on()
    elif msg == "L20":
        # Laser 2 OFF
        response += ":laser2off"
        L2.off()
    elif msg == "L21":
        # Laser 2 ON
        response += ":laser2on"
        L2.on()
    elif msg == "RPM":
        if len(msgs) > 2:
            rpm = msgs[2]
            set_mps()
    elif msg == "STEP":
        if len(msgs) > 2:
            steps = msgs[2]
            cw = False
            if len(msgs) > 3:
                cw = msgs[3] == "CW"
            step(steps, cw)

    # Serial.print(response)
    # delay(250)


def step(steps, cw):
    if cw:
        DIR.on()
    else:
        DIR.off()
    for n in range(0, steps):
        PUL.on()
        utime.sleep_ms(mps)
        PUL.off()
        utime.sleep_ms(mps)
    return True


def set_mps():
    global mps
    mps = int(60000 / rpm / ppr / 2)


rpm = 5
fspr = 200              # motor full steps per rev
ms = 16                 # driver micro steps setting
ppr = fspr * ms
mps = 0
uart = UART(0, 9600)

set_mps()

cnt = 0
while True:

    if uart.any() > 0:
        process_msg(uart.read())

    utime.sleep_ms(250)
    cnt += 1
    if cnt > 500:
        raise Exception('End after 500.')
