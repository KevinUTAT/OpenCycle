from bt_csc import BLECSCCentral, run_CSC
from machine import Pin, I2C
import ssd1306

# using default address 0x3C
i2c = I2C(sda=Pin(5), scl=Pin(4))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

def run_display(display_data):
    display.fill_rect(0,0,127,63,0)  
    display.text('Open Cycle', 0, 0, )
    display.text('Wheel Rev: ', 0, 10, 2)
    display.text(str(display_data[1]), 80, 10, 2)
    display.text('Time: ', 0, 30, 2)
    display.text(str(display_data[2]), 50, 30, 2)
    display.show()

def print_data(data):
    print("Wheel Rev:", csc_data[1])
    print("Since last:", csc_data[2], "ms")
    
def run_openCycle(on_display=True):
    if on_display:
        run_CSC(run_display)
    else:
        run_CSC(print_data)

if __name__ == "__main__":
    run_CSC(run_display)