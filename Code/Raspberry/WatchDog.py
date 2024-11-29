from time import sleep
from rpi_TM1638 import TMBoards

import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

import signal
import subprocess
import os

## TM1638 SETTINGS
DIO = 11
CLK = 9
STB = 10

## OLED SETTINGS
WIDTH = 128
HEIGHT = 64
BORDER = 5
SCL = 3
SDA = 2

# Define the Reset Pin
oled_reset = None
# instanciante Oled
# Use for I2C.
i2c = busio.I2C(SCL, SDA)  # uses board.SCL and board.SDA
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)
# instanciante TMboard
TM = TMBoards(DIO, CLK, STB, 0)
TM.clearDisplay()
tmOff = False

logo = Image.open("logo.png")
logo_r = logo.resize((WIDTH,HEIGHT), Image.BICUBIC)
logo_bw = logo_r.convert("1")

# Display image
oled.image(logo_bw)
oled.show()
sleep(1)

image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

def clearTM():
    TM.clearDisplay()
    TM.clearDisplay()

def handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        clearTM()
        oled.fill(0)
        oled.show()
        exit(1)

signal.signal(signal.SIGINT, handler)

def drawText(text: str):

    # Load default font.
    font = ImageFont.load_default()

    # Draw Some Text
    (font_width, font_height) = font.getsize(text)
    draw.text(
        (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
        text,
        font=font,
        fill=0,
    )

    # Display image
    oled.image(image)
    oled.show()

# Used to display mainMenu
def mainMenu():
    TM.segments[0] = 'MAINMENU'

    # Draw background
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

    # Load font
    font = ImageFont.load_default()

    draw.text((5,2), "START", font=font, fill=0,)
    draw.text((43,2), "SETTINGS", font=font, fill=0,)
    draw.text((100,2), "QUIT", font=font, fill=0,)

    draw.line([(38, 0), (38,15)], fill=0, width=1)
    draw.line([(94, 0), (94,15)], fill=0, width=1)

    # Display image
    oled.image(image)
    oled.show()

# Used to display mainMenu
def settingsMenu():
    TM.segments[0] = 'SETTINGS'
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

    # Load font
    font = ImageFont.load_default()

    draw.text((5,2), "SAVE", font=font, fill=0,)
    draw.text((43,2), "DEFAULTS", font=font, fill=0,)
    draw.text((100,2), "BACK", font=font, fill=0,)
    draw.text((5,20), "1. Bitrate", font=font, fill=0,)
    draw.text((5,30), "2. FPS", font=font, fill=0,)
    draw.text((5,40), "3. Beep", font=font, fill=0,)
    draw.text((5,50), "4. Port", font=font, fill=0,)
    draw.line([(38, 0), (38,15)], fill=0, width=1)
    draw.line([(94, 0), (94,15)], fill=0, width=1)

    # Display image
    oled.image(image)
    oled.show()

# Clears board and display before quitting
def quit():
    TM.clearDisplay()
    TM.clearDisplay()
    oled.fill(0)
    oled.show()
    exit(1)

# Turns display off
def screenOFF():
    global tmOff
    tmOff = True
    clearTM()
    TM.leds[0] = True
    TM.leds[1] = True
    TM.leds[2] = True
    TM.leds[3] = True
    TM.leds[4] = True
    TM.segments[0] = "OLED   5"
    for i in range (4, -1, -1):
        sleep(1)
        TM.leds[i] = False
        TM.segments[7] = f"{i}"
    TM.segments[0] = "SCRN OFF"
    oled.write_cmd(0xAE)

# Turns display on
def screenON():
    global tmOff
    tmOff = False
    oled.write_cmd(0xaf)
    TM.segments[0] = "MAINMENU"

def main():
    inMain = True
    inSettings = False
    mainMenu()
    while True:
        if (TM.switches[0] and inMain):
            TM.leds[0] = True
            drawText("STARTED")
            screenOFF()
            os.system("sudo /home/martin/WatchDog/sentry-picam -record -rot 180 -mthreshold 12 -run /home/martin/WatchDog/scripts/processUpload.sh")
        elif (TM.switches[0] and inSettings):
            TM.leds[0] = True
            drawText("SAVED")
            sleep(1)
            settingsMenu()
            TM.leds[0] = False
        elif (TM.switches[1] and inMain):
            TM.leds[1] = True
            inMain = False
            inSettings = True
            settingsMenu()
            TM.leds[1] = False
        elif (TM.switches[1] and inSettings):
            TM.leds[1] = True
            drawText("DEFAULTs")
            sleep(1)
            settingsMenu()
            TM.leds[1] = False
        elif (TM.switches[2] and inMain):
            TM.leds[2] = True
            quit()
        elif (TM.switches[2] and inSettings):
            TM.leds[2] = True
            inMain = True
            inSettings = False
            mainMenu()
            TM.leds[2] = False
        elif (TM.switches[7] and tmOff):
            TM.leds[7] = True
            sleep(1)
            screenON()
            TM.leds[7] = False
main()