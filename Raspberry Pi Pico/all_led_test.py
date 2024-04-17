from machine import Pin
import time

# GP16 -> 14(74HC595)
# GP17 -> 12(74HC595)
# GP18 -> 11(74HC595)
ser_pin = 16
latch_pin = 17
clk_pin = 18

ser = Pin(ser_pin, Pin.OUT)
latch = Pin(latch_pin, Pin.OUT)
clock = Pin(clk_pin, Pin.OUT)

def setRegister(ser, clock, val):
    for i in range(0, 8):
        # CLOCK : LOW -> HIGH
        clock.off()
        ser.value(val & (0x01 << i))
        clock.on()
        
def zfill(s, width):
    if len(s) < width:
        return ('0' * (width - len(s))) + s
    else:
        return s
    
def pref_to_led(pref):
    sr1 = {
        "北海道": 0b10000000,
        "青森県": 0b01000000,
        "岩手県": 0b00100000,
        "宮城県": 0b00010000,
        "秋田県": 0b00001000,
        "山形県": 0b00000100,
        "福島県": 0b00000010,
        "茨城県": 0b00000001
    }

    sr2 = {
        "栃木県": 0b10000000,
        "群馬県": 0b01000000,
        "埼玉県": 0b00100000,
        "千葉県": 0b00010000,
        "東京都": 0b00001000,
        "神奈川県": 0b00000100,
        "新潟県": 0b00000010,
        "富山県": 0b00000001
    }

    sr3 = {
        "石川県": 0b10000000,
        "福井県": 0b01000000,
        "山梨県": 0b00100000,
        "長野県": 0b00010000,
        "岐阜県": 0b00001000,
        "静岡県": 0b00000100,
        "愛知県": 0b00000010,
        "三重県": 0b00000001
    }

    sr4 = {
        "滋賀県": 0b10000000,
        "京都府": 0b01000000,
        "大阪府": 0b00100000,
        "兵庫県": 0b00010000,
        "奈良県": 0b00001000,
        "和歌山県": 0b00000100,
        "鳥取県": 0b00000010,
        "島根県": 0b00000001
    }

    sr5 = {
        "岡山県": 0b10000000,
        "広島県": 0b01000000,
        "山口県": 0b00100000,
        "徳島県": 0b00010000,
        "香川県": 0b00001000,
        "愛媛県": 0b00000100,
        "高知県": 0b00000010,
        "福岡県": 0b00000001
    }

    sr6 = {
        "佐賀県": 0b10000000,
        "長崎県": 0b01000000,
        "熊本県": 0b00100000,
        "大分県": 0b00010000,
        "宮崎県": 0b00001000,
        "鹿児島県": 0b00000100,
        "沖縄県": 0b00000010
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

prefectures = [
    '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
    '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
    '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県',
    '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県',
    '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
    '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
    '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
]


pref_to_led(prefectures)
