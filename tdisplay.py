from st7789my import ST7789font 
from machine import Pin
from display import Display


class TDisplay(Display):

    def __init__(self, cs=5, dc=16, bl=4, sck=18, mosi=19):
        super().__init__()
        self.BL = Pin(4,Pin.OUT)
        self.tdisp = ST7789font(None,135,240,reset=None,cs=Pin(5,Pin.OUT),dc=Pin(16,Pin.OUT),backlight=self.BL)
        
        
    def init(self):
        self.BL.on()
        self.tdisp.init()


class DebugTdisp(TDisplay):

    def __init__(self, cs=5, dc=16, bl=4, sck=18, mosi=19):
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


if __mane__ == "__main__":
    test_diplay = DebugTdisp()
    DebugTdisp.init()
    DebugTdisp.test_msg()
