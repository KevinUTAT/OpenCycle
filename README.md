# What is this?
This project is to create a fully open sourced cycling computer based on micro-controller hardwares such as ESP32 and Pi Pico. \
This project is still a working progress and are at a very early stage so please forgive me for the current state.
|        Oled debug       |        Oled Normal      |        T-Display        |
|:-----------------------:|:-----------------------:|:-----------------------:|
|![](resource/screen1.png)|![](resource/screen2.png)|![](resource/screen3.png)|
# Why Open Cycle?
Similar project exist on ARM-Linux platforms but I want something that can be run on very miniature hardware while still maintain good battery life. \
One of the goal for this project is to create a software platform to make it easier to make your own cycling computer with your choices of hardware and interface.\
If you have a project with specific hardware and sensor in mind, feel free to try this out or open an issue so I can help as well. 
# Hardware compatibility
You will need a MicroPython compatible micro-controller such as one based on the ESP-32 module or the Pi-Pico module.\
Currently, I have only tested it on the [*DIYMore OLED ESP32 Board*](https://www.diymore.cc/products/diymore-esp32-0-96-inch-oled-display-wifi-bluetooth-18650-battery-shield-development-board-cp2102-module-for-arduino) I don't actually recommend this board but its what I have on hands right now and more tested board are coming.\
You will also need a speed/Cadence sensor for your bike. This can be home made or off-the-shelf as long as it follows the Bluetooth SIG's [*Cycling Speed and Cadence GATT profile*](https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Services/org.bluetooth.service.cycling_speed_and_cadence.xml).\
I uses a [XOSS speed/Cadence sensor](https://shop.xoss.co/collections/xoss-cadence-speed-sensor/products/xoss-cadence-speed-sensor) just because its the cheapest I can find.
# What is working right now?
- BLE communication with the speed/cadence sensor
- SSD1306 displaying
- ST7789 displaying
# How to run
Using your preferred method copy all *.py* file to your micro-controller.\
Make sure your speed/Cadence sensor is awake. \
If you have a SSD1306 OLED display on I2C, run *open_cycle.run_openCycle*.\
Or run *open_cycle.run_openCycle(on_display=False)* if you just want data to be printed.\
You might need to run it more then once to have the bluetooth connection to be connected :(
# Change log:
### 2021-11-13:
Adding support for the TTGO T-Display as its a very nice piece of hardware.
- Modifying the [st7789my](https://gitlab.com/pascalokm/t-watch2020-esp32-with-micropython/-/blob/master/st7789my.py) to enable text scaling and draw circle
- Enable asynchronous display update. Due to the slow nature of ST7789, i change the display to no longer in sync with the bluetooth call back. This allows many nice thing like update speed more often than others and much faster connections speed
- Adding new colour screen with run time and battery voltage 
### 2021-11-06:
Modularize display implementation. Also added new nicer screen with larger speed font.\
Thanks for the nicer [OLED font library](https://github.com/micropython-Chinese-Community/mpy-lib/tree/master/LED/OLED_I2C_ASC) from MicroPython Chinese community
### 2021-10-30:
Add speed and distance calculation
### 2021-10-24:
Finally getting data from the speed/Cadence sensor