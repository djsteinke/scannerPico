import machine
from time import sleep_ms
from sys import exit


def reg_write(reg, in_data):
    """
    Write bytes to the specified register.
    """
    # Construct message
    msg = bytearray()
    msg.append(in_data)
    # Write out message to register
    i2c.writeto_mem(ADDR, reg, msg)


def reg_read(reg, nbytes=1):
    """
    Read byte(s) from specified register. If nbytes > 1, read from consecutive
    registers.
    """
    # Check to make sure caller is asking for 1 or more bytes
    if nbytes < 1:
        return bytearray()
    # Request data from specified register(s) over I2C
    ret = i2c.readfrom_mem(ADDR, reg, nbytes)
    return ret


# I2C address
ADDR = 0x38

# Create I2C object
i2c = machine.I2C(0, scl=machine.Pin(21), sda=machine.Pin(20))

# Print out any addresses found
devices = i2c.scan()

sleep_ms(30000)

for i in range(0, 100):
    if devices:
        for d in devices:
            print(hex(d))
            if hex(d) == ADDR:
                break
    sleep_ms(1000)

config = [0x08, 0x00]
measure_cmd = [0x33, 0x00]

# Registers
REG_DEVID = 0x00
REG_POWER_CTL = 0x08
REG_DATAX0 = 0x32

data = reg_read(REG_DEVID)

print(data)


"""
# Read device ID to make sure that we can communicate with the ADXL343
data = reg_read(i2c, ADXL343_ADDR, REG_DEVID)
if (data != bytearray((DEVID,))):
    print("ERROR: Could not communicate with ADXL343")
    sys.exit()

# Read Power Control register
data = reg_read(i2c, ADXL343_ADDR, REG_POWER_CTL)
print(data)

# Tell ADXL343 to start taking measurements by setting Measure bit to high
data = int.from_bytes(data, "big") | (1 << 3)
reg_write(i2c, ADXL343_ADDR, REG_POWER_CTL, data)

# Test: read Power Control register back to make sure Measure bit was set
data = reg_read(i2c, ADXL343_ADDR, REG_POWER_CTL)
print(data)

bus.write_i2c_block_data(0x38, 0xE1, config)
byt = bus.read_byte(0x38)
bus.write_i2c_block_data(0x38, 0xAC, measure_cmd)
time.sleep(0.5)
data = bus.read_i2c_block_data(0x38, 0x00)

temp_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
temp_c = ((temp_raw * 200) / 1048576) - 50
humid_raw = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
humid = humid_raw * 100 / 1048576
print(round(temp_c, 2))
print(round(humid, 1))
"""
