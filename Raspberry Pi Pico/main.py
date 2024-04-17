from machine import Pin, I2C
import ssd1306
import framebuf
import time
import sys

import network
import ntptime

from uwebsocketsclient import connect
import ujson as json

from misakifont import MisakiFont

# sandbox (Virtual environment)
#uri = 'wss://api-realtime-sandbox.p2pquake.net:443/v2/ws'

# Production environment
uri = 'wss://api.p2pquake.net:443/v2/ws'

'''
PIN & WiFi Setting
'''
ssid = '***YOUR SSID (2.4GHz)***'
password = '***YOUR PASSWORD***'

alert_led = Pin(10, Pin.OUT)
status_led = Pin(11, Pin.OUT)

# I2C setting (SDA->20, SCL->21)
i2c = I2C(0, sda=Pin(20), scl=Pin(21) )
# Display setting
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

# GP16 -> 14(74HC595)
# GP17 -> 12(74HC595)
# GP18 -> 11(74HC595)
ser_pin = 16
latch_pin = 17
clk_pin = 18

ser = Pin(ser_pin, Pin.OUT)
latch = Pin(latch_pin, Pin.OUT)
clock = Pin(clk_pin, Pin.OUT)

'''
Function to display the point at which the earthquake occurred
'''
fcolor = 1
mf = MisakiFont()

def show_text(text, x, y, fsize, xmax):
    x_origin = x
    for c in text:
        fd = mf.font(ord(c))
        show_bitmap(oled, fd, x, y, fcolor, fsize)
        x += 8 * fsize
        if x >= xmax:
            x = x_origin
            y += 8 * fsize
    oled.show()

def show_bitmap(oled, fd, x, y, color, size):
    for row in range(0, 7):
        for col in range(0, 7):
            if (0x80 >> col) & fd[row]:
                oled.fill_rect(int(x + col * size), int(y + row * size), size, size, color)

'''
functions
'''
def zfill(s, width):
    if len(s) < width:
        return ('0' * (width - len(s))) + s
    else:
        return s
    
def setRegister(ser, clock, val):
    for i in range(0, 8):
        # CLOCK : LOW -> HIGH
        clock.off()
        # Input data in order from the least significant bit
        ser.value(val & (0x01 << i))
        clock.on()
        
def scale_to_value(scale):
    scale_dict = {
        "-1": "?",
        "10": "1",
        "20": "2",
        "30": "3",
        "40": "4",
        "50": "5弱",
        "55": "5強",
        "60": "6弱",
        "65": "6強",
        "70": "7"
    }
    return scale_dict.get(str(scale), "?")

def seismic_intensity(max_scale_value):
    if len(max_scale_value) >= 2:
        max_scale_scale = max_scale_value[1:]
        max_scale_value = max_scale_value[:1]
        show_text(max_scale_scale, 120, 8, 1, 128)
    show_text(max_scale_value, 104, 0, 2, 128)

def seismic_magnitude(magnitude):
    magnitude = str(magnitude)
    show_text('M', 104, 16, 1, 128)
    show_text(magnitude, 104, 24, 1, 128)

def happen_date(date):
    show_text(date, 4, 16, 1, 96)

def happen_time(time):
    show_text(time, 4, 24, 1, 96)

def happen_depth(depth):
    show_text(depth, 0, 8, 1, 96)

def happen_location(location):
    show_text(location, 4, 0, 1, 96)
    
def make_frame():
    oled.fill_rect(0, 0, 2, 8, 1)
    oled.fill_rect(0, 16, 2, 16, 1)
    oled.fill_rect(100, 0, 2, 31, 1)

'''
Prefectures List
'''
def pref_to_led(pref):
    sr1 = {
        "北海道": 0b10000000,
        "青森県": 0b01000000,
        "岩手県": 0b00100000,
        "宮城県": 0b00010000,
        "秋田県": 0b00001000,
        "山形県": 0b00000100,
        "福島県": 0b00000010,
        "茨城県": 0b00000001,
        "青森": 0b01000000,
        "岩手": 0b00100000,
        "宮城": 0b00010000,
        "秋田": 0b00001000,
        "山形": 0b00000100,
        "福島": 0b00000010,
        "茨城": 0b00000001
    }

    sr2 = {
        "栃木県": 0b10000000,
        "群馬県": 0b01000000,
        "埼玉県": 0b00100000,
        "千葉県": 0b00010000,
        "東京都": 0b00001000,
        "神奈川県": 0b00000100,
        "新潟県": 0b00000010,
        "富山県": 0b00000001,
        "栃木": 0b10000000,
        "群馬": 0b01000000,
        "埼玉": 0b00100000,
        "千葉": 0b00010000,
        "東京": 0b00001000,
        "神奈川": 0b00000100,
        "新潟": 0b00000010,
        "富山": 0b00000001
    }

    sr3 = {
        "石川県": 0b10000000,
        "福井県": 0b01000000,
        "山梨県": 0b00100000,
        "長野県": 0b00010000,
        "岐阜県": 0b00001000,
        "静岡県": 0b00000100,
        "愛知県": 0b00000010,
        "三重県": 0b00000001,
        "石川": 0b10000000,
        "福井": 0b01000000,
        "山梨": 0b00100000,
        "長野": 0b00010000,
        "岐阜": 0b00001000,
        "静岡": 0b00000100,
        "愛知": 0b00000010,
        "三重": 0b00000001
    }

    sr4 = {
        "滋賀県": 0b10000000,
        "京都府": 0b01000000,
        "大阪府": 0b00100000,
        "兵庫県": 0b00010000,
        "奈良県": 0b00001000,
        "和歌山県": 0b00000100,
        "鳥取県": 0b00000010,
        "島根県": 0b00000001,
        "滋賀": 0b10000000,
        "京都": 0b01000000,
        "大阪": 0b00100000,
        "兵庫": 0b00010000,
        "奈良": 0b00001000,
        "和歌山": 0b00000100,
        "鳥取": 0b00000010,
        "島根": 0b00000001
    }

    sr5 = {
        "岡山県": 0b10000000,
        "広島県": 0b01000000,
        "山口県": 0b00100000,
        "徳島県": 0b00010000,
        "香川県": 0b00001000,
        "愛媛県": 0b00000100,
        "高知県": 0b00000010,
        "福岡県": 0b00000001,
        "岡山": 0b10000000,
        "広島": 0b01000000,
        "山口": 0b00100000,
        "徳島": 0b00010000,
        "香川": 0b00001000,
        "愛媛": 0b00000100,
        "高知": 0b00000010,
        "福岡": 0b00000001
    }

    sr6 = {
        "佐賀県": 0b10000000,
        "長崎県": 0b01000000,
        "熊本県": 0b00100000,
        "大分県": 0b00010000,
        "宮崎県": 0b00001000,
        "鹿児島県": 0b00000100,
        "沖縄県": 0b00000010,
        "佐賀": 0b10000000,
        "長崎": 0b01000000,
        "熊本": 0b00100000,
        "大分": 0b00010000,
        "宮崎": 0b00001000,
        "鹿児島": 0b00000100,
        "沖縄": 0b00000010
    }
    
    # Make list named srs
    srs = [sr1, sr2, sr3, sr4, sr5, sr6]
    
    # Initial
    initial_binary = 0
    sr1_send = sr2_send = sr3_send = sr4_send = sr5_send = sr6_send = initial_binary

    for idx, sr in enumerate(srs, start=1):
        for prefecture in pref:
            if prefecture in sr:
                bit_value = sr[prefecture]

                if idx == 1:
                    sr1_send = sr1_send + bit_value
                elif idx == 2:
                    sr2_send = sr2_send + bit_value
                elif idx == 3:
                    sr3_send = sr3_send + bit_value
                elif idx == 4:
                    sr4_send = sr4_send + bit_value
                elif idx == 5:
                    sr5_send = sr5_send + bit_value
                elif idx == 6:
                    sr6_send = sr6_send + bit_value

    # LATCH : LOW -> HIGH
    latch.off()
    setRegister(ser, clock, sr6_send)
    setRegister(ser, clock, sr5_send)
    setRegister(ser, clock, sr4_send)
    setRegister(ser, clock, sr3_send)
    setRegister(ser, clock, sr2_send)
    setRegister(ser, clock, sr1_send)
    latch.on()

'''
RESET LED
'''
status_led.off()
alert_led.off()

initial_binary = 0
sr1_send = sr2_send = sr3_send = sr4_send = sr5_send = sr6_send = initial_binary

latch.off()
setRegister(ser, clock, sr6_send)
setRegister(ser, clock, sr5_send)
setRegister(ser, clock, sr4_send)
setRegister(ser, clock, sr3_send)
setRegister(ser, clock, sr2_send)
setRegister(ser, clock, sr1_send)
latch.on()

'''
Display at startup
'''
# Display MicroPython logo
oled.fill_rect(0, 0, 32, 32, 1)
oled.fill_rect(2, 2, 28, 28, 0)
oled.vline(9, 8, 22, 1)
oled.vline(16, 2, 22, 1)
oled.vline(23, 8, 22, 1)
oled.fill_rect(26, 24, 2, 4, 1)
# Display text
oled.text('Run by', 40, 7, 1)
oled.text('MicroPython', 40, 17, 1)
# Show
oled.show()
time.sleep(1.5)

# Hiding the text
oled.fill_rect(32, 0, 128, 32, 0)
oled.show()

'''
Setup to connect to WiFi
'''
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Loop until connection is established
max_wait = 0
while max_wait <= 20:
    # Hiding the text
    oled.fill_rect(32, 0, 128, 32, 0)
    oled.show()
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    # Display text
    oled.text('Connection', 40, 7, 1)
    oled.text(f'trial:{max_wait}/20', 40, 17, 1)
    oled.show()
    max_wait += 1
    time.sleep(1)
    
wlan_status = wlan.status()
print('Status code:' +str(wlan_status))

# Handle connection error
# Error meanings
# 0  Link Down
# 1  Link Join
# 2  Link NoIp
# 3  Link Up
# -1 Link Fail
# -2 Link NoNet
# -3 Link BadAuth

status = wlan.ifconfig()
#print('ip = ' + status[0])

if wlan_status == 3:
    # Display text
    oled.text('WiFi is', 40, 7, 1)
    oled.text('connected!!', 40, 17, 1)
    # Show
    oled.show()
    time.sleep(1.5)
    # Clear display
    oled.fill(0)
    oled.show()
else:
    # Display text
    oled.text('WiFi is NOT', 40, 7, 1)
    oled.text('connected!!', 40, 17, 1)
    # Show
    oled.show()
    status_led.on()
    sys.exit()

'''
Obtain the time from an NTP server 
(since the time information must be added to the certificate or it will be rejected)
'''
ntptime.settime()

'''
Raspberry Pi Logo
'''
# Raspberry Pi logo as 32x32 bytearray
buffer = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
fb = framebuf.FrameBuffer(buffer, 32, 32, framebuf.MONO_HLSB)
oled.blit(fb, 49, 0)
oled.show()

'''
functions for getting earthquake information using Websocket
'''
websocket = connect(uri)
 
try:
    while True:
        data = websocket.recv()
        data = json.loads(data)
        
        code = data['code']
            
        # code:556 -> Earthquake Early Warning Alert
        if code == 556:
            # ON alertLED
            alert_led.on()                
            time = data['earthquake']['arrivalTime']
            # No data -> max_scale = data['earthquake']['maxScale']
            max_scale = '!'
            magnitude = data['earthquake']['hypocenter']['magnitude']
            depth = data['earthquake']['hypocenter']['depth']
            location = data['earthquake']['hypocenter']['name']
            
            pref = list(set(point['pref'] for point in data['areas']))
            
            if magnitude == -1:
                magnitude = '?'
                
            if location == '':
                location = '計測中'

            if depth == -1:
                depth = '?'

            depth = f'（深さ：{depth}㎞）'
            
            date = time.split()[0]
            time = time.split()[1]
            
            oled.fill(0)
            oled.show()
            
            # Display earthquake information
            seismic_intensity(max_scale_value)
            seismic_magnitude(magnitude)
            happen_depth(depth)
            happen_location(location)
            happen_date(date)
            happen_time(time)
            make_frame()
            oled.show()
            
            # Show the prefecture with LED
            pref_to_led(pref)
            
        # code:551 -> Earthquake Information
        elif code == 551:
            # Reset alertLED
            alert_led.off() 
            time = data['earthquake']['time']
            max_scale = data['earthquake']['maxScale']
            magnitude = data['earthquake']['hypocenter']['magnitude']
            depth = data['earthquake']['hypocenter']['depth']
            location = data['earthquake']['hypocenter']['name']
            
            pref = list(set(point['pref'] for point in data['points']))
            
            # Converts maximum seismic intensity ID to a numerical value
            max_scale_value = scale_to_value(max_scale)

            if magnitude == -1:
                magnitude = '?'
                
            if location == '':
                location = '計測中'

            if depth == -1:
                depth = '?'

            depth = f'（深さ：{depth}㎞）'
            
            date = time.split()[0]
            time = time.split()[1]
            
            oled.fill(0)
            oled.show()
            
            # Display earthquake information
            seismic_intensity(max_scale_value)
            seismic_magnitude(magnitude)
            happen_depth(depth)
            happen_location(location)
            happen_date(date)
            happen_time(time)
            make_frame()
            oled.show()
            
            # Show the prefecture with LED
            pref_to_led(pref)

        else:
            # Blink
            status_led.on()
            time.sleep(0.5)
            status_led.off()
            time.sleep(0.5)
            status_led.on()
            time.sleep(0.5)
            status_led.off()
            time.sleep(0.5)
            
except Exception as e:
    status_led.on()
    oled.fill(0)
    oled.show()
    show_text(f'Error:{e}', 0, 0, 1, 128)

finally:
    # Close WebSocket
    websocket.close()
