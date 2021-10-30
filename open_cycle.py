from bt_csc import BLECSCCentral, run_CSC
from machine import Pin, I2C
import ssd1306

MS_IN_MIN = 60000
SHORT_SIZE = 65536
WHEEL_CIRC = 2155 # mm, for 32-622 (700x32C)
KPH2MMPM = 16667 # km/h to mm/min

# using default address 0x3C
i2c = I2C(sda=Pin(5), scl=Pin(4))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

wheelRev = 0
lastUpdate = 0

rev_count = 0

def display_msg(title, msg0="", msg1="", msg2=""):
    display.fill(0)  
    display.text('OpenCycle', 0, 0, 1)
    display.text(title, 0, 20, 1)
    display.text(msg0, 0, 30, 1)
    display.text(msg1, 0, 40, 1)
    display.text(msg2, 0, 50, 1)
    display.show()

def run_debug_display(raw_data, rpm, speed, distance):
    display.fill(0)  
    display.text('OpenCycle', 0, 0, 1)
    display.text('Wheel Rev: ', 0, 10, 1)
    display.text(str(raw_data[1]), 80, 10, 1)
    display.text('Time: ', 0, 20, 1)
    display.text(str(raw_data[2]), 50, 20, 1)
    display.text('RPM: ', 0, 30, 1)
    display.text(str(rpm), 50, 30, 1)
    display.text('Speed: ', 0, 40, 1)
    display.text(str(speed), 50, 40, 1)
    display.text('Distance: ', 0, 50, 1)
    display.text(str(distance), 70, 50, 1)
    display.show()

def print_data(data):
    print("Wheel Rev:", csc_data[1])
    print("Since last:", csc_data[2], "ms")

def on_receive_CSC(csc_data):
    global wheelRev
    global lastUpdate
    global rev_count
    # if its the first notification on power up
    if (wheelRev == 0) and (lastUpdate == 0):
        wheelRev = csc_data[1]
        lastUpdate = csc_data[2]
        return
    rev = csc_data[1] - wheelRev
    rev_count += rev
    # handles wraparound
    if lastUpdate > csc_data[2]:
        dt = csc_data[2] + SHORT_SIZE - lastUpdate
    else:
        dt = csc_data[2] - lastUpdate
    if rev == 0 or dt == 0:
        rpm = 0
    else:
        rpm = (rev / dt) * MS_IN_MIN
        
    speed = (rpm * WHEEL_CIRC) / KPH2MMPM
    dist = (rev_count * WHEEL_CIRC) / 1000000
    
    # update global vars
    wheelRev = csc_data[1]
    lastUpdate = csc_data[2]

    run_debug_display(csc_data, rpm, speed, dist)
    
    
def run_openCycle(on_display=True):
    if on_display:
        run_CSC(on_receive_CSC, display_msg)
    else:
        run_CSC(print_data)

if __name__ == "__main__":
    run_CSC(on_receive_CSC, display_msg)