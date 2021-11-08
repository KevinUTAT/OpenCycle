# this is from: https://github.com/devbis/st7789py_mpy
# (seems to be under MIT license)

import time
from micropython import const
import ustruct as struct

# commands
ST77XX_NOP = const(0x00)
ST77XX_SWRESET = const(0x01)
ST77XX_RDDID = const(0x04)
ST77XX_RDDST = const(0x09)

ST77XX_SLPIN = const(0x10)
ST77XX_SLPOUT = const(0x11)
ST77XX_PTLON = const(0x12)
ST77XX_NORON = const(0x13)

ST77XX_INVOFF = const(0x20)
ST77XX_INVON = const(0x21)
ST77XX_DISPOFF = const(0x28)
ST77XX_DISPON = const(0x29)
ST77XX_CASET = const(0x2A)
ST77XX_RASET = const(0x2B)
ST77XX_RAMWR = const(0x2C)
ST77XX_RAMRD = const(0x2E)

ST77XX_PTLAR = const(0x30)
ST77XX_COLMOD = const(0x3A)
ST7789_MADCTL = const(0x36)
ST7789_VSCSAD = const(0x37)

ST7789_MADCTL_MY = const(0x80)
ST7789_MADCTL_MX = const(0x40)
ST7789_MADCTL_MV = const(0x20)
ST7789_MADCTL_ML = const(0x10)
ST7789_MADCTL_BGR = const(0x08)
ST7789_MADCTL_MH = const(0x04)
ST7789_MADCTL_RGB = const(0x00)

ST7789_RDID1 = const(0xDA)
ST7789_RDID2 = const(0xDB)
ST7789_RDID3 = const(0xDC)
ST7789_RDID4 = const(0xDD)

ColorMode_65K = const(0x50)
ColorMode_262K = const(0x60)
ColorMode_12bit = const(0x03)
ColorMode_16bit = const(0x05)
ColorMode_18bit = const(0x06)
ColorMode_16M = const(0x07)

# Color definitions
BLACK = const(0x0000)
BLUE = const(0x001F)
RED = const(0xF800)
GREEN = const(0x07E0)
CYAN = const(0x07FF)
MAGENTA = const(0xF81F)
YELLOW = const(0xFFE0)
WHITE = const(0xFFFF)

_ENCODE_PIXEL = ">H"
_ENCODE_POS = ">HH"
_DECODE_PIXEL = ">BBB"

_BUFFER_SIZE = const(256)


def delay_ms(ms):
    time.sleep_ms(ms)


def color565(r, g=0, b=0):
    """Convert red, green and blue values (0-255) into a 16-bit 565 encoding.  As
    a convenience this is also available in the parent adafruit_rgb_display
    package namespace."""
    try:
        r, g, b = r  # see if the first var is a tuple/list
    except TypeError:
        pass
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3


class ST77xx:
    def __init__(self, spi, width, height, reset, dc, cs=None, backlight=None,
                 xstart=-1, ystart=-1):
        """
        display = st7789.ST7789(
            SPI(1, baudrate=40000000, phase=0, polarity=1),
            240, 240,
            reset=machine.Pin(5, machine.Pin.OUT),
            dc=machine.Pin(2, machine.Pin.OUT),
        )

        """
        self.width = width
        self.height = height
        self.spi = spi
        if spi is None:
            import machine
            self.spi = machine.SPI(1,baudrate=32000000, polarity=1, phase=0, bits=8, firstbit=0, sck=machine.Pin(18,machine.Pin.OUT),mosi=machine.Pin(19,machine.Pin.OUT))
            self.spi.init()
        self.reset = reset
        self.dc = dc
        self.cs = cs
        self.backlight = backlight
        if xstart >= 0 and ystart >= 0:
            self.xstart = xstart
            self.ystart = ystart
        elif (self.width, self.height) == (240, 240):
            self.xstart = 0
            self.ystart = 0
        elif (self.width, self.height) == (135, 240):
            self.xstart = 52
            self.ystart = 40
        else:
            raise ValueError(
                "Unsupported display. Only 240x240 and 135x240 are supported "
                "without xstart and ystart provided"
            )

    def dc_low(self):
        self.dc.off()

    def dc_high(self):
        self.dc.on()

    def reset_low(self):
        if self.reset:
            self.reset.off()

    def reset_high(self):
        if self.reset:
            self.reset.on()

    def cs_low(self):
        if self.cs:
            self.cs.off()

    def cs_high(self):
        if self.cs:
            self.cs.on()

    def write(self, command=None, data=None):
        """SPI write to the device: commands and data"""
        self.cs_low()
        if command is not None:
            self.dc_low()
            self.spi.write(bytes([command]))
        if data is not None:
            self.dc_high()
            self.spi.write(data)
        self.cs_high()

    def hard_reset(self):
        self.cs_low()
        self.reset_high()
        delay_ms(50)
        self.reset_low()
        delay_ms(50)
        self.reset_high()
        delay_ms(150)
        self.cs_high()

    def soft_reset(self):
        self.write(ST77XX_SWRESET)
        delay_ms(150)

    def sleep_mode(self, value):
        if value:
            self.write(ST77XX_SLPIN)
        else:
            self.write(ST77XX_SLPOUT)

    def inversion_mode(self, value):
        if value:
            self.write(ST77XX_INVON)
        else:
            self.write(ST77XX_INVOFF)

    def _set_color_mode(self, mode):
        self.write(ST77XX_COLMOD, bytes([mode & 0x77]))

    def init(self, *args, **kwargs):
        self.hard_reset()
        self.sleep_mode(False)
        delay_ms(200)
        self.soft_reset()
        self.sleep_mode(False)
        delay_ms(200)
        
    def rotate(self,n):
        # rotate display colockwise n times
        rotate = (n+2) % 4
        if rotate < 0:
           rotate += 4
        vs=0   
        if rotate == 0:
          self._set_mem_access_mode(0,False)
        elif rotate==2:
          self._set_mem_access_mode(3)
          vs=80
        elif rotate==3:
          self._set_mem_access_mode(5,True)
        elif rotate==1:
          self._set_mem_access_mode(6)
          vs=80
          
        self.write(ST7789_VSCSAD,struct.pack(">H",vs))
            

    def _set_mem_access_mode(self, rotation, vert_mirror=False, horz_mirror=False, is_bgr=False):
        rotation &= 7
        value = {
            0: 0,
            1: ST7789_MADCTL_MX,
            2: ST7789_MADCTL_MY,
            3: ST7789_MADCTL_MX | ST7789_MADCTL_MY,
            4: ST7789_MADCTL_MV,
            5: ST7789_MADCTL_MV | ST7789_MADCTL_MX,
            6: ST7789_MADCTL_MV | ST7789_MADCTL_MY,
            7: ST7789_MADCTL_MV | ST7789_MADCTL_MX | ST7789_MADCTL_MY,
        }[rotation]

        if vert_mirror:
            value |= ST7789_MADCTL_ML
        elif horz_mirror:
            value |= ST7789_MADCTL_MH

        if is_bgr:
            value |= ST7789_MADCTL_BGR
        self.write(ST7789_MADCTL, bytes([value]))

    def _encode_pos(self, x, y):
        """Encode a postion into bytes."""
        return struct.pack(_ENCODE_POS, x, y)

    def _encode_pixel(self, color):
        """Encode a pixel color into bytes."""
        return struct.pack(_ENCODE_PIXEL, color)

    def _set_columns(self, start, end):
        if start > end or end >= self.width:
            return
        start += self.xstart
        end += self.xstart
        self.write(ST77XX_CASET, self._encode_pos(start, end))

    def _set_rows(self, start, end):
        if start > end or end >= self.height:
            return
        start += self.ystart
        end += self.ystart
        self.write(ST77XX_RASET, self._encode_pos(start, end))

    def set_window(self, x0, y0, x1, y1):
        self._set_columns(x0, x1)
        self._set_rows(y0, y1)
        self.write(ST77XX_RAMWR)

    def vline(self, x, y, length, color):
        self.fill_rect(x, y, 1, length, color)

    def hline(self, x, y, length, color):
        self.fill_rect(x, y, length, 1, color)

    def pixel(self, x, y, color):
        self.set_window(x, y, x, y)
        self.write(None, self._encode_pixel(color))

    def blit_buffer(self, buffer, x, y, width, height):
        self.set_window(x, y, x + width - 1, y + height - 1)
        self.write(None, buffer)

    def rect(self, x, y, w, h, color):
        self.hline(x, y, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)
        self.hline(x, y + h - 1, w, color)

    def fill_rect(self, x, y, width, height, color):
        self.set_window(x, y, x + width - 1, y + height - 1)
        chunks, rest = divmod(width * height, _BUFFER_SIZE)
        pixel = self._encode_pixel(color)
        self.dc_high()
        if chunks:
            data = pixel * _BUFFER_SIZE
            for _ in range(chunks):
                self.write(None, data)
        if rest:
            self.write(None, pixel * rest)

    def fill(self, color):
        self.fill_rect(0, 0, self.width, self.height, color)

    def line(self, x0, y0, x1, y1, color):
        # Line drawing function.  Will draw a single pixel wide line starting at
        # x0, y0 and ending at x1, y1.
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        dx = x1 - x0
        dy = abs(y1 - y0)
        err = dx // 2
        if y0 < y1:
            ystep = 1
        else:
            ystep = -1
        while x0 <= x1:
            if steep:
                self.pixel(y0, x0, color)
            else:
                self.pixel(x0, y0, color)
            err -= dy
            if err < 0:
                y0 += ystep
                err += dx
            x0 += 1



class ST7789(ST77xx):
    def init(self, *, color_mode=ColorMode_65K | ColorMode_16bit):
        super().init()
        delay_ms(50)
        self._set_color_mode(color_mode)
        delay_ms(50)
        self.write(ST77XX_NORON)
        delay_ms(50)
        self._set_mem_access_mode(0, True, False, False)
        self.inversion_mode(True)
        delay_ms(50)
        self.write(ST77XX_NORON)
        delay_ms(10)
        self.fill(0)
        self.write(ST77XX_DISPON)
        delay_ms(500)


class ST7789font(ST7789):
    def init(self, *arg, **kw):
        super().init(*arg,**kw)
        self.fontinit()
        #self.testimg()

    def fontinit(self, width=5, height=8, font_name='font5x8.bin'):
        # Specify the drawing area width and height, and the pixel function to
        # call when drawing pixels (should take an x and y param at least).
        # Optionally specify font_name to override the font file to use (default
        # is font5x8.bin).  The font format is a binary file with the following
        # format:
        # - 1 unsigned byte: font character width in pixels
        # - 1 unsigned byte: font character height in pixels
        # - x bytes: font data, in ASCII order covering all 255 characters.
        #            Each character should have a byte for each pixel column of
        #            data (i.e. a 5x8 font has 5 bytes per character).
        self.pixmode = False
        self._width = width
        self._height = height
        self._font_name = font_name
        self._font_width, self._font_height = 0,0
        self.cursx=0
        self.cursy=0
        with open(self._font_name, 'rb') as ff:
          self._font_width, self._font_height = struct.unpack('BB', ff.read(2))
          self._fontdata=ff.read(32 * self._font_width * self._font_height )
          #print(type(self._fontdata))
          #print("read size",self._font_width,self._font_height)
        self._linebuf=bytearray(2*(self._font_width+1)*(self._font_height+1))

    def writechar(self,ch,x=-1,y=-1,fg=WHITE,bg=BLACK,scale=1):
        cnt=0
        # linebuf=self._linebuf
        linebuf = bytearray(scale*scale*2*(self._font_width+1)*(self._font_height+1))
        if x < 0 or y < 0:
            x=self.cursx
            y=self.cursy
        #bbg=struct.pack(">H",bg)
        #bfg=struct.pack(">H",fg)
        bfg=bytes([ (fg >> 8) & 0xff, fg & 0xff ] )
        bbg=bytes([ (bg >> 8) & 0xff, bg & 0xff ] )
        for char_y in range(self._font_height+1):
            for rpy in range(scale):
                for char_x in range(self._font_width+1):
                    for rpx in range(scale):
                        line=  0 if char_x >= self._font_width else int(self._fontdata[((ord(ch) * self._font_width) + char_x)])
                        if self.pixmode:
                            self.pixel(x+char_x,y+char_y, fg if (line >> char_y) & 0x1 else bg)    
                        elif (line >> char_y) & 0x1:
                            #linebuf[cnt:(cnt+1)]  = bfg
                            linebuf[cnt]=bfg[0]
                            linebuf[cnt+1]=bfg[1] 
                        else:
                            #linebuf[cnt:(cnt+1)]  = bbg
                            linebuf[cnt]=bbg[0]
                            linebuf[cnt+1]=bbg[1] 
                        cnt += 2
        if not self.pixmode:        
            self.blit_buffer(memoryview(linebuf), x, y, (self._font_width+1)*scale, (self._font_height+1)*scale)
        
    def showimg(self,fn,x=0,y=0):
        with open(fn,"rb") as f:
          szinfo=f.read(8)
          sx,sy=struct.unpack(">LL",szinfo)
          for cnt in range(max(sy,self._height)):
              buf=f.read(sx*2)
              self.blit_buffer(buf, x, y+cnt, sx, 1)
        
    def writestring(self,stri,x=-1,y=-1,fg=WHITE,bg=BLACK,updatecursor=True,scale=1):
        if x < 0 or y < 0:
            x=self.cursx
            y=self.cursy
        for ch in stri:
            if x + (self._font_width*scale) > self.width:
                x=0
                y += (self._font_height*scale)+1
            if y + (self._font_height*scale) > self.height:
                y=0
                x=0  
            self.writechar(ch,x,y,fg,bg, scale)
            x += (self._font_width*scale) +1
        if updatecursor:
            self.cursx=x
            self.cursy=y
    
    def testimg(self):
        self.fill(BLACK)
        cnt=0
        for k in [ RED, GREEN,  BLUE ]:
            self.fill_rect(cnt*80, 200, 80, 40, k)
            cnt += 1
            
        self.line(0, 239, 119, 0, WHITE)
        self.line(239, 239, 120, 0, YELLOW)
        self.pixel(239, 0, WHITE)
        self.writestring("__--Hello World!--__",60,180)

