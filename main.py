import machine
from time import sleep_ms


def write_mem(reg, data):
    buf = bytearray()
    for d in data:
        buf.append(d)
    i2c.writeto_mem(address, reg, buf)


def write(data):
    buf = bytearray()
    for d in data:
        buf.append(d)
    i2c.writeto(address, buf)


def read_mem(reg, nbytes=1):
    return i2c.readfrom_mem(address, reg, nbytes)


def read(nbytes=1):
    return i2c.readfrom(address, nbytes)


def measure():
    global temp_c, temp_f, humid
    write_mem(0xAC, measure_cmd)
    sleep_ms(250)
    while True:
        ret = read(1)
        if ret[0] & 0x01 == 0:
            break
        sleep_ms(50)
    data = read(7)
    temp_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
    temp_c = round((temp_raw / 1048575 * 200) - 50, 2)
    temp_f = round(temp_c * 1.8 + 32.0, 2)
    humid_raw = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
    humid = round(humid_raw / 1048576 * 100, 1)


def led_flash(cnt=1):
    for i in range(0, cnt):
        led.on()
        sleep_ms(250)
        led.off()
        sleep_ms(250)


def get_out():
    return '{"c": %0.2f, "f": %0.2f, "h": %0.1f}' % (temp_c, temp_f, humid)


led = machine.Pin(25, machine.Pin.OUT)

# wait for sensor to power up
sleep_ms(500)

# I2C address
address = 0x38
measure_cmd = [0x30, 0x00]

temp_c = 0.00
temp_f = 0.00
humid = 0.0

# Create I2C object
i2c = machine.I2C(0, scl=machine.Pin(21), sda=machine.Pin(20))

write([0x71])
state_word = read()
device_check = read_mem(0x18)
if state_word == device_check:
    led_flash(5)

sleep_ms(10)

while True:
    measure()
    print(get_out())
    led_flash()
    machine.lightsleep(60000)
