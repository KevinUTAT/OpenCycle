import ssd1306
from machine import Pin, I2C
from oled_font.oled import OLED12864_I2C
from display import Display

class OledDisplay(Display):

    def __init__(self, sda, scl):
        super().__init__()
        self.sda = sda
        self.scl = scl

    def init(self):
        self.i2c = I2C(sda=Pin(self.sda), scl=Pin(self.scl))
        self.ssd_display = ssd1306.SSD1306_I2C(128, 64, self.i2c)
        self.ssd_display_ascii = OLED12864_I2C(self.i2c)

    def clear(self):
        self.ssd_display.fill(0)


# for debugging
class DebugOled(OledDisplay):

    def __init__(self, sda, scl):
        super().__init__(sda, scl)

    def show_csc(self, speed, distance, rpm, raw):
        self.clear()
        self.ssd_display.text('OpenCycle', 0, 0, 1)
        self.ssd_display.text('Wheel Rev: ', 0, 10, 1)
        self.ssd_display.text(str(raw[1]), 80, 10, 1)
        self.ssd_display.text('Time: ', 0, 20, 1)
        self.ssd_display.text(str(raw[2]), 50, 20, 1)
        self.ssd_display.text('RPM: ', 0, 30, 1)
        self.ssd_display.text(str(rpm), 50, 30, 1)
        self.ssd_display.text('Speed: ', 0, 40, 1)
        self.ssd_display.text(str(speed), 50, 40, 1)
        self.ssd_display.text('Distance: ', 0, 50, 1)
        self.ssd_display.text(str(distance), 70, 50, 1)
        self.ssd_display.show()

    def show_msg(self, title, msg0="", msg1="", msg2=""):
        self.clear()
        self.ssd_display.text('OpenCycle', 0, 0, 1)
        self.ssd_display.text(title, 0, 20, 1)
        self.ssd_display.text(msg0, 0, 30, 1)
        self.ssd_display.text(msg1, 0, 40, 1)
        self.ssd_display.text(msg2, 0, 50, 1)
        self.ssd_display.show()


# speed and distance
class OCOled(OledDisplay):

    def __init__(self, sda, scl):
        super().__init__(sda, scl)

    def show_csc(self, speed, distance, rpm, raw):
        if not self.csc_screen:
            self.ssd_display_ascii.clear()
            self.csc_screen = True
        self.ssd_display_ascii.Font('Font_6x8')
        self.ssd_display_ascii.text(0, 0, "OpenCycle")
        self.ssd_display_ascii.Font("Font_16x32")
        self.ssd_display_ascii.text(0, 1, "{:#.4g}".format(speed))
        self.ssd_display_ascii.Font("Font_8x16")
        self.ssd_display_ascii.text(90, 3, "Km/h")
        self.ssd_display_ascii.text(0, 5, "{:#.6g}".format(distance))
        self.ssd_display_ascii.text(90, 5, "Km")

    def show_msg(self, title, msg0="", msg1="", msg2=""):
        self.csc_screen = False
        self.ssd_display_ascii.clear()
        self.ssd_display_ascii.Font("Font_6x8")
        self.ssd_display_ascii.text(0, 0, title)
        self.ssd_display_ascii.text(0, 1, msg0)
        self.ssd_display_ascii.text(0, 2, msg1)
        self.ssd_display_ascii.text(0, 3, msg2)
