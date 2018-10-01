from lab3 import Lab3
from lab3 import *
import lab3

class Lab3_imu(Lab3):
    def __init__(self):
        # super
        super(Lab3_imu, self).__init__()

        # IMU
        self.init_imu()
        self.imu_timer = Timer(5)
        self.imu_timer.init(period=1000, mode=Timer.ONE_SHOT, callback=self.imu_cb)
        self.imu_buf = bytearray(6)
        self.x = 0
        self.y = 0
        self.z = 0

        # OLED
        self.i2c_imu = I2C(scl=Pin(SCL), sda=Pin(SDA), freq=100000)
        
        # test LED
        self.test_led2 = Pin(TEST_LED2, Pin.OUT)
        self.test_led2.off()
        
        return

################ IMU ######################

    def imu_x(self):
        self.imu_buf = self.i2c_imu.readfrom_mem(IMU_ADDR, IMU_REG, 6)
        self.x = (int(self.imu_buf[1]) << 8) | self.imu_buf[0]
        if self.x > 32767:
            self.x = self.x - 65536
        return

    def imu_y(self):
        self.imu_buf = self.i2c_imu.readfrom_mem(IMU_ADDR, IMU_REG, 6)
        self.y = (int(self.imu_buf[3]) << 8) | self.imu_buf[2]
        if self.y > 32767:
            self.y = self.y - 65536
        return

    def imu_z(self):
        self.imu_buf = self.i2c_imu.readfrom_mem(IMU_ADDR, IMU_REG, 6)
        self.z = (int(self.imu_buf[5]) << 8) | self.imu_buf[4]
        if self.z > 32767:
            self.z = self.z - 65536
        return

    def imu_cb(self, timer):
        self.imu_x()
        self.imu_y()
        self.imu_z()
        text = "x:{} y:{} z:{}".format(self.x, self.y, self.z)
        #super(Lab3_imu, self).print_text(text)
        super(Lab3_imu, self).scroll_text(2)
        return


    def init_imu(self):
        b = bytearray(1)
        b[0] = 0
        self.i2c.writeto_mem(IMU_ADDR, 0x2d, b)
        b[0] = 16
        self.i2c.writeto_mem(IMU_ADDR, 0x2d, b)
        b[0] = 8
        self.i2c.writeto_mem(IMU_ADDR, 0x2d, b)
        return


