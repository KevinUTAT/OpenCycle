from bt_csc import BLECSCCentral, run_CSC
from machine import Pin, I2C
import ssd1306

MS_IN_MIN = 60000
SHORT_SIZE = 65536

# using default address 0x3C
i2c = I2C(sda=Pin(5), scl=Pin(4))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

wheelRev = 0
lastUpdate = 0

def display_msg(title, msg0="", msg1="", msg2=""):
    display.fill(0)  
    display.text('OpenCycle', 0, 0, 1)
    display.text(title, 0, 20, 1)
    display.text(msg0, 0, 30, 1)
    display.text(msg1, 0, 40, 1)
    display.text(msg2, 0, 50, 1)
    display.show()

def run_display(raw_data, rpm):
    display.fill(0)  
    display.text('OpenCycle', 0, 0, 1)
    display.text('Wheel Rev: ', 0, 20, 1)
    display.text(str(raw_data[1]), 80, 20, 1)
    display.text('Time: ', 0, 30, 1)
    display.text(str(raw_data[2]), 50, 30, 1)
    display.text('RPM: ', 0, 40, 1)
    display.text(str(rpm), 50, 40, 1)
    display.show()

def print_data(data):
    print("Wheel Rev:", csc_data[1])
    print("Since last:", csc_data[2], "ms")

def on_receive_CSC(csc_data):
    global wheelRev
    global lastUpdate
    # if its the first notification on power up
    if (wheelRev == 0) and (lastUpdate == 0):
        wheelRev = csc_data[1]
        lastUpdate = csc_data[2]
        return
    rev = csc_data[1] - wheelRev
    # handles wraparound
    if lastUpdate > csc_data[2]:
        dt = csc_data[2] + SHORT_SIZE - lastUpdate
    else:
        dt = csc_data[2] - lastUpdate
    if rev == 0 or dt == 0:
        rpm = 0
    else:
        rpm = (rev / dt) * MS_IN_MIN
    
    # update global vars
    wheelRev = csc_data[1]
    lastUpdate = csc_data[2]

    run_display(csc_data, rpm)
    
def run_openCycle(on_display=True):
    if on_display:
        run_CSC(on_receive_CSC, display_msg)
    else:
        run_CSC(print_data)

if __name__ == "__main__":
    run_CSC(on_receive_CSC, display_msg)