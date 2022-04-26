import machine
from time import sleep_ms
from tof.VL53L0X import VL53L0X, Vl53l0xAccuracyMode

sensor = VL53L0X(i2c_bus=0, i2c_address=0x29)
sensor.open()
sensor.start_ranging(Vl53l0xAccuracyMode.BEST)

led = machine.Pin(25, machine.Pin.OUT)
led.off()

while True:
    led.on()
    dist = sensor.get_distance()
    print(round(dist, 2))
    sleep_ms(200)
    led.off()
    sleep_ms(800)
