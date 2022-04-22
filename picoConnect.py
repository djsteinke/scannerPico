import serial
from time import sleep

serial = serial.Serial("COM6", 9600, timeout=1)
print('Connected')

i = 0

on = False


def get_msg():
    global i, on
    m = i + 512
    m = m << 4
    m += (1 if on else 2)
    m = m << 2
    m += 1
    m = m << 16
    m += 21345
    on = not on
    return m


try:
    cnt = 50
    msg = ""
    found = True
    while True:
        data = serial.readline()
        if data:
            res = int(data)
            #res = ' '.join(hex(b) for b in data if b not in (0xd, 0xa))
            msg_id = res & 0x7c0
            msg_id = msg_id >> 6
            found = msg_id == i
            complete = res & 0x003f == 1
            print(cnt, data, res, found, complete)

        if cnt >= 5:
            i += 1
            msg_int = get_msg()
            bs = msg_int.to_bytes(4, 'big')
            msg = ' '.join(hex(b) for b in bs)
            print('out', msg_int)
            serial.write(bytes(str(msg_int), encoding='utf-8'))
            cnt = 0
            found = False
        cnt += 1
        #sleep(0.01)
except KeyboardInterrupt:
    serial.close()
    exit()
