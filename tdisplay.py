from st7789my import (ST7789font, BLACK, BLUE, RED, 
                    GREEN, CYAN, MAGENTA, YELLOW, WHITE)
from machine import Pin, ADC
from display import Display
import time
import _thread


class TDisplay(Display):

    def __init__(self, cs=5, dc=16, bl=4, sck=18, mosi=19, bat=34):
        super().__init__()
        self.BL = Pin(4,Pin.OUT)
        self.tdisp = ST7789font(None,135,240,reset=None, \
            cs=Pin(5,Pin.OUT),dc=Pin(16,Pin.OUT),backlight=self.BL)
        self.bat = ADC(Pin(bat))
        
    def init(self):
        self.BL.on()
        self.tdisp.init()
        self.timer = time.time()

    def s2hms(self, time_s):
        h = int(time_s / 3600)
        m = int((time_s - h*3600) / 60)
        s = time_s - h*3600 - m*60
        return h, m, s
    
    def clear(self):
        self.tdisp.fill(BLACK)


class DebugTdisp(TDisplay):

    def __init__(self, cs=5, dc=16, bl=4, sck=18, mosi=19, bat=34):
        super().__init__(cs, dc, bl, sck, mosi)

    def show_csc(self, speed, distance, rpm, raw):
        self.tdisp.writestring("OpenCycle", 0, 0)
        self.tdisp.writestring("Wheel Rev: ", 0, 10)
        self.tdisp.writestring(str(raw[1]), 80, 10)
        self.tdisp.writestring("Time: ", 0, 20)
        self.tdisp.writestring(str(raw[2]), 50, 20)
        self.tdisp.writestring("RPM: ", 0, 30)
        self.tdisp.writestring(str(rpm), 50, 30)
        self.tdisp.writestring("Speed: ", 0, 40)
        self.tdisp.writestring(str(speed), 50, 40)
        self.tdisp.writestring("Distance: ", 0, 50)
        self.tdisp.writestring(str(distance), 70, 50)

    def show_msg(self, title, msg0="", msg1="", msg2=""):
        self.tdisp.writestring(title, 0, 0)
        self.tdisp.writestring(msg0, 0, 10)
        self.tdisp.writestring(msg1, 0, 20)
        self.tdisp.writestring(msg2, 0, 30)


class ColorTdisp(TDisplay):

    def __inti__(self, cs=5, dc=16, bl=4, sck=18, mosi=19, bat=34):
        super().__init__(cs, dc, bl, sck, mosi, bat)

    def init(self):
        super().init()
        self.csc_on = False
        self.msg_on = False

    def run_msg_screen(self):
        while self.msg_screen:
            self._show_msg()

    def run_csc_screen(self):
        count = 0
        while self.csc_screen:
            if count >= 5:
                self._show_csc()
                count = 0
            else:
                self._show_speed()
                count += 1


    def show_msg(self, title, msg0="", msg1="", msg2=""):
        self.title = title
        self.msg0 = msg0
        self.msg1 = msg1
        self.msg2 = msg2

        if not self.msg_screen:
            self.msg_screen = True
            self.csc_screen = False
            _thread.start_new_thread(self.run_msg_screen, ())

    def show_csc(self, speed, distance, rpm, raw):
        self.speed = speed
        self.distance = distance
        self.rpm = rpm
        self.raw = raw

        if not self.csc_screen:
            self.csc_screen = True
            self.msg_screen = False
            _thread.start_new_thread(self.run_csc_screen, ())

    def _show_msg(self):
        if not self.msg_on:
            self.msg_on = True
            self.csc_on = False
            time.sleep(2)
            self.clear()

        self.tdisp.writestring("OpenCycle", 18, 0, fg=RED, scale=2)
        self.tdisp.fill_rect(0, 20, 135, 160, BLACK)
        self.tdisp.writestring(self.title, 0, 20, scale=2)
        self.tdisp.writestring(self.msg0, 0, 60, scale=2)
        self.tdisp.writestring(self.msg1, 0, 100, scale=2)
        self.tdisp.writestring(self.msg2, 0, 140, scale=2)

    def _show_csc(self):
        if not self.csc_on:
            self.csc_on = True
            self.msg_on = False
            time.sleep(2)
            self.clear()

        self.tdisp.writestring("OpenCycle", 18, 0, fg=RED, scale=2)
        bat_v = self.bat.read() / 4095 * 2.0 * 3.3 * 1.1
        self.tdisp.writestring(str(bat_v)+'V', 40, 30, fg=YELLOW, scale=2)

        self.tdisp.writestring("{:#.3g}".format(self.speed), 3, 100, fg=CYAN, scale=6)
        self.tdisp.fill_rect(0, 150, 135, 5, BLACK)
        self.tdisp.fill_rect(67-int(self.speed), 150, int(self.speed*2), 5, RED)

        self.tdisp.writestring(("{:#.3g}".format(self.distance)) + "Km", 10, 160, fg=MAGENTA, scale=3)

        h, m, s = self.s2hms(time.time() - self.timer)
        self.tdisp.writestring((str(h)+':'+str(m)+':'+str(s)), 40, 200, scale=2)

    def _show_speed(self):
        if not self.csc_on:
            self.csc_on = True
            self.msg_on = False
            time.sleep(2)
            self.clear()
        
        self.tdisp.writestring("{:#.3g}".format(self.speed), 3, 100, fg=CYAN, scale=6)
        self.tdisp.fill_rect(0, 150, 135, 5, BLACK)
        self.tdisp.fill_rect(67-int(self.speed), 150, int(self.speed*2), 5, RED)
        




if __name__ == "__main__":
    test_diplay = ColorTdisp()
    test_diplay.init()
    test_diplay.test_csc()
