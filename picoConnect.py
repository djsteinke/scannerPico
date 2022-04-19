import serial
from time import sleep

serial = serial.Serial("COM5", 9600, timeout=1)
print('Connected')

try:
    while True:
        data = serial.readline()
        s_data = data.decode().rstrip()
        if len(s_data) > 0:
            print(f'{s_data}')
        sleep(0.1)
except KeyboardInterrupt:
    serial.close()
    exit()
