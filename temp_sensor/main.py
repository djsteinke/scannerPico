import machine
from time import sleep_ms

try:
    # Create I2C object
    i2c = machine.I2C(0, scl=machine.Pin(21), sda=machine.Pin(20))

    # Print out any addresses found
    devices = i2c.scan()

    for i in range(0, 100):
        if devices:
            for d in devices:
                print(hex(d))
        else:
            print('ping')
        sleep_ms(1000)
except Exception as e:
    print(str(e))
