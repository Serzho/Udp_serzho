#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import os
import pickle as pl
import sys
sys.path.append('EduBot/EduBotLibrary')
import edubot
import crc16


import Adafruit_SSD1306

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

SERVO_MIN_POS = 42
SERVO_MID_POS = 62
SERVO_MAX_POS = 82

def SetSpeed(leftSpeed, rightSpeed):
    robot.leftMotor.SetSpeed(leftSpeed)
    robot.rightMotor.SetSpeed(rightSpeed)

def SetCameraServoPos(position):
    if position > SERVO_MAX_POS:
        position = SERVO_MAX_POS
    elif position > SERVO_MIN_POS:
        position = SERVO_MIN_POS
    robot.servo[0].SetPosition(position)

def TextDisplay(text):
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    widthText, heightText = draw.textsize(text)
    widthDisp, heightDisp = robot.displaySize
    draw.text(((widthDisp - widthText)//2 ,(heightDisp - heightText)//2), text ,font = font, fill=255)
    disp.image(image)
    disp.display()

def Beep(beep):
    if beep:
        robot.Beep()
IP = '192.168.8.163' #айпи сервера
PORT = 8000 #порт сервера
TIMEOUT = 60 #время ожидания ответа сервера [сек]

#128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst = None)

# Initialize library.
disp.begin()

# Get display width and height.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

robot = edubot.EduBot(True)
assert robot.Check(), 'EduBot not found!!!'
robot.Start() #обязательная процедура, запуск потока отправляющего на контроллер EduBot онлайн сообщений
print ('EduBot started!!!')
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #создаем udp сервер

server.bind((IP, PORT)) #запускаем udp сервер
print("Listening on port %d..." % PORT) #выводим сообщение о запуске сервера
server.settimeout(TIMEOUT) #указываем серверу время ожидания

draw = ImageDraw.Draw(image)

# Clear display.
disp.clear()

# Load default font.
#font = ImageFont.load_default()
fontFile = 'DejaVuSans.ttf'
font = ImageFont.truetype(fontFile, 15)

stateMove = [0, 0]
leftSpeed = 0
rightSpeed = 0
USER_IP = ''

old_text = ''

while True: #создаем бесконечный цикл    
    try:
        packet = server.recvfrom(1024) #попытка получить 1024 байта
    except socket.timeout:
        print("Time is out...")
        break

    #print("Message: %s" % msg.decode'utf-8' + str(adrs))
    data = packet[0]
    if(USER_IP == ''):
        USER_IP = packet[1][0]
    else:
        if(USER_IP == packet[1][0]):
            crcBytes = data[-2:]
            crc = int.from_bytes(crcBytes, byteorder="big", signed = False)

            stateMoveBytes = data[:-2]
            newCrc = crc16.crc16xmodem(stateMoveBytes)
            #print(crc, newCrc)
            if crc == newCrc:
            #print(stateMove)
                text, BASE_SPEED, stateMove, servoPos, beep, automat = pl.loads(stateMoveBytes)
                leftSpeed = int(stateMove[0] * BASE_SPEED + stateMove[1] * BASE_SPEED // 2)
                rightSpeed = int(-stateMove[0] * BASE_SPEED + stateMove[1] * BASE_SPEED // 2)
                SetSpeed(leftSpeed,rightSpeed)
                #print(leftSpeed, rightSpeed)
                SetCameraServoPos(servoPos)
                Beep(beep)
                if(text!=old_text):
                    TextDisplay(text)
                    old_text = text
        else:
            print('Invalid IP %s' % packet[1][0])

SetCameraServoPos(SERVO_MID_POS = 62)
robot.ClearDisplay()
server.close()
SetSpeed(0, 0)
robot.Release()
