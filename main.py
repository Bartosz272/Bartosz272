import select
import sys
from machine import I2C,ADC, Pin
import utime
import dht
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

I2C_ADDR     = 0x27
I2C_NUM_ROWS = 4
I2C_NUM_COLS = 20
i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

led = Pin(4, Pin.OUT)
pump = Pin(5,Pin.OUT)
pump2 = Pin(6,Pin.OUT)
water_level_led = Pin(3,Pin.OUT)
DHT_sensor = dht.DHT11(Pin(14))
moisture_sensor = ADC(Pin(26))
water_level_sensor = machine.ADC(27)
# setup poll to read USB port
poll_object = select.poll()
poll_object.register(sys.stdin,1)

def function_1(x=2):
    print("Executing function 1")
    try:
        DHT_sensor.measure()
        temp = DHT_sensor.temperature()
        hum = DHT_sensor.humidity()
        
        lcd.move_to(0,0)
        lcd.putstr('Temperature: %3.1f C' %temp)
        lcd.move_to(0,1)
        lcd.putstr('Humidity: %3.1f 1%%' %hum)
    except:
        lcd.move_to(0,0)
        lcd.putstr('DHT sensor ERROR')
        lcd.move_to(0,1)
        lcd.putstr('DHT sensor ERROR')
    try:
        value = moisture_sensor.read_u16()
        value_12bit = value >> 4
        lcd.move_to(0,2)
        lcd.putstr(f'Soil moistnes:{value_12bit}')
    except:
        lcd.move_to(0,2)
        lcd.putstr('Soil Moisture sensor ERROR')
    try:
        water_level_value = water_level_sensor.read_u16()
        if water_level_value < 5000:
            water_level_led.on()
        else:
            water_level_led.off()
    except:
        water_level_led.toggle()       
    if x == 1:
        lcd.putstr('Light: ON ')
    elif x ==0:
        lcd.putstr('Light: OFF')
    else:
        lcd.move_to(0,3)
    print(f'{temp},{hum},{value_12bit}')
    return value_12bit
    

def function_2():
    led.on()
    x = 1
    function_1(x)
    
def function_3():
    led.off()
    x = 0
    function_1(x)
    
def function_4():
    function_1()
    value = moisture_sensor.read_u16()
    value_12bit = value >> 4
    if value_12bit > 200:
        while True:
            value = moisture_sensor.read_u16()
            value_12bit = value >> 4
            if value_12bit < 150:
                pump.on()
            else:
                break
            
    pump.off()

    

print("Started looking")
while True:
    # check usb input
    if poll_object.poll(0):
        #read as character
        input = sys.stdin.read(1)
        if input == "1":
            #refresh screen, gather Data - DHT,moistens, level of water
            function_1()
        elif input == "2":
            #change light, if low moist water
            
            function_2()
        elif input == "3":
            function_3()
        elif input == "4":
            function_4()
        else:   
            print (input, "Received. Was expecting 1 or 2")