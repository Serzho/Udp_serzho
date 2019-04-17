#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#библиотеки для работы с i2c монитором питания INA219
from ina219 import INA219
from ina219 import DeviceRangeError

#библиетека для работы с OLED дисплеем
import Adafruit_SSD1306

#библиотеки для работы с изображениями Python Image Library
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import socket
import os
import pickle
import sys
import subprocess as sp

import time
import threading
import crc16

sys.path.append('EduBot/EduBotLibrary')
import edubot

import cv2
import numpy as np
import psutil

sys.path.append('/home/pi/RPicam-Streamer/')

import rpicam

#поток для контроля напряжения и тока
#и отображения на дисплее

class StateThread(threading.Thread):
    def __init__(self, robot, ina219, disp):
        super(StateThread, self).__init__()
        self.daemon = True
        self._stopped = threading.Event() #событие для остановки потока
        self._robot = robot
        self._ina = ina219
        self._disp = disp

        
    def run(self):
        image = Image.new('1', (self._disp.width, self._disp.height)) #создаем ч/б картинку для отрисовки на дисплее
        draw = ImageDraw.Draw(image) #создаем объект для рисования на картинке
        font = ImageFont.load_default() #создаем шрифт для отрисовки на дисплее

        print('State thread started')
        while not self._stopped.is_set():
            # Отрисовываем на картинке черный прямоугольник, тем самым её очищая
            draw.rectangle((0, 0, self._disp.width, self._disp.height), outline=0, fill=0)
            
            #Отрисовываем строчки текста с текущими значениями напряжения, сылы тока и мощности
            draw.text((0, 0), "Edubot project", font=font, fill=255)
            draw.text((0, 10), "Voltage: %.2fV" % self._ina.voltage(), font=font, fill=255)
            draw.text((0, 20), "Current: %.2fmA" % self._ina.current(), font=font, fill=255)
            draw.text((0, 30), "Power: %.2f" % self._ina.power(), font=font, fill=255)

            # Копируем картинку на дисплей
            self._disp.image(image)

            #Обновляем дисплей
            self._disp.display()
            time.sleep(1)
            
        print('State thread stopped')

    def stop(self): #остановка потока
        self._stopped.set()
        self.join()

class FrameHandlerThread(threading.Thread):
    
    def __init__(self, stream):
        super(FrameHandlerThread, self).__init__()
        self.daemon = True
        self.rpiCamStream = stream
        self._frame = None
        self._frameCount = 0
        self._stopped = threading.Event() #событие для остановки потока
        self._newFrameEvent = threading.Event() #событие для контроля поступления кадров
        
    def run(self):
        print('Frame handler started')
        while not self._stopped.is_set():
            self.rpiCamStream.frameRequest() #отправил запрос на новый кадр
            self._newFrameEvent.wait() #ждем появления нового кадра
            '''
            if not (self._frame is None): #если кадр есть
                
                #--------------------------------------
                # тут у нас обрабока кадра self._frame средствами OpenCV
                time.sleep(0.1) #имитируем обработку кадра
                imgFleName = 'frame%d.jpg' % self._frameCount
                #cv2.imwrite(imgFleName, self._frame) #сохраняем полученный кадр в файл
                #print('Write image file: %s' % imgFleName)
                self._frameCount += 1
                #--------------------------------------
                '''
            self._newFrameEvent.clear() #сбрасываем событие
            
        print('Frame handler stopped')

    def stop(self): #остановка потока
        self._stopped.set()
        if not self._newFrameEvent.is_set(): #если кадр не обрабатывается
            self._frame = None
            self._newFrameEvent.set() 
        self.join()

    def setFrame(self, frame): #задание нового кадра для обработки
        if not self._newFrameEvent.is_set(): #если обработчик готов принять новый кадр
            self._frame = frame
            self._newFrameEvent.set() #задали событие
        return self._newFrameEvent.is_set()

                
def onFrameCallback(frame): #обработчик события 'получен кадр'
    #print('New frame')
    frameHandlerThread.setFrame(frame) #задали новый кадр

def SetSpeed(leftSpeed, rightSpeed):
    robot.leftMotor.SetSpeed(leftSpeed)
    robot.rightMotor.SetSpeed(rightSpeed)
    return 0

def ServoUp():
    global servoPos
    servoPos -= 10
    if servoPos < 0:
        servoPos = 0
    robot.servo[0].SetPosition(servoPos)
    print ('ServoPos = %d' % servoPos)
    return 0

def ServoDown():
    global servoPos
    servoPos += 10
    if servoPos > 125:
        servoPos = 125
    robot.servo[0].SetPosition(servoPos)
    print ('ServoPos = %d' % servoPos)
    return 0

def transmit():
    global frameHandlerThread
    global IP_RTP
    global RTP_PORT
    print('Start transmit...')
    #проверка наличия камеры в системе  
    assert rpicam.checkCamera(), 'Raspberry Pi camera not found'
    print('Raspberry Pi camera found')

    print('OpenCV version: %s' % cv2.__version__)


    FORMAT = rpicam.VIDEO_MJPEG #поток MJPEG
    WIDTH, HEIGHT = 320, 240
    RESOLUTION = (WIDTH, HEIGHT)
    FRAMERATE = 30


    rpiCamStreamer = rpicam.RPiCamStreamer(FORMAT, RESOLUTION, FRAMERATE)
    rpiCamStreamer.setPort(RTP_PORT)
    rpiCamStreamer.setHost(IP_RTP)
    
    rpiCamStreamer.start() #запускаем трансляцию

    #поток обработки кадров    
    frameHandlerThread = FrameHandlerThread(rpiCamStreamer)
    frameHandlerThread.start() #запускаем обработку
    

def recv_data():
    global running
    global old_data
    global IP_RTP 
    global first_cicle
    global transmit
    
    data = []
    try:
        data = server.recvfrom(1024) #пытаемся получить данные
        if first_cicle: #если первая иттерация, то записываем IP первого устройства, приславшего пакет с данными
            IP_RTP = data[1][0]
            first_cicle = False
            transmit()
        if data != old_data and data[1][0] == IP_RTP : #если пакет данных "устарел", то игнорируем
            old_data = data
            return data
        else:
            return None
    except socket.timeout: #если вышло время, то выходим из цикла
        running = False
        print("Time is out...")

def end():
    global frameHandlerThread
    global running
    global transmit
    running = False
    SetSpeed(0,0)
    robot.Release()
    server.close()
    try:
        #останавливаем обработку кадров
        frameHandlerThread.stop()

        #останов трансляции c камеры
        rpiCamStreamer.stop()    
        rpiCamStreamer.close()
    except(NameError):
        pass
        
    print('End program')
    
IP = str(os.popen('hostname -I | cut -d\' \' -f1').readline().replace('\n','')) #получаем IP, удаляем \n
PORT = 8000
IP_RTP = ''
#IP_RTP = '192.168.1.104'
RTP_PORT = 5000 #порт отправки RTP видео

print('SELF IP: %s \n PORT: %d' % (IP, PORT)) #вывод IP и PORT

TIMEOUT = 120 #время ожидания

SHUNT_OHMS = 0.01 #значение сопротивления шунта на плате EduBot
MAX_EXPECTED_AMPS = 2.0

servoPos = 62
    
robot = edubot.EduBot(1)
assert robot.Check(), 'EduBot not found!!!'
robot.Start() #обязательная процедура, запуск потока отправляющего на контроллер EduBot онлайн сообщений

print ('EduBot started!!!')

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #создаем UDP сервер
server.bind((IP, PORT)) #запускаем сервер
server.settimeout(TIMEOUT) #указываем время ожидания сервера

print("Listening %s on port %d..." % (IP, PORT)) #вывод о запуске сервера

ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS) #создаем обект для работы с INA219
ina.configure(ina.RANGE_16V)
    
disp = Adafruit_SSD1306.SSD1306_128_64(rst = None) #создаем обект для работы c OLED дисплеем 128х64
disp.begin() #инициализируем дисплей
    
disp.clear() #очищаем дисплей
disp.display() #обновляем дисплей

if sys.argv[1] == 1:  
    #создаем и запускаем поток отображающий данные телеметрии да дисплее робота
    stateThread = StateThread(robot, ina, disp)
    stateThread.start()

running = True
direction = [0, 0]
command = []
first_cicle = True
old_data = []
auto = False

rightSpeed = 0
leftSpeed = 0

while running:  
    try:      
        cmd = [] #список всех команд, отправляемых роботу
        data = recv_data()
    
        if data:
            cmd, crc = pickle.loads(data[0]) #распаковываем команду и значение контрольной суммы
            crc_new = crc16.crc16xmodem(cmd) #расчитываем контрольную сумму полученных данных
            if crc == crc_new: #сравниваем контрольные суммы и проверяем целостность данных
                cmd = pickle.loads(cmd) #распаковываем список команд
                leftSpeed, rightSpeed, command, servo, automat = cmd
                #print(direction, speed, command, servo)
                
                

                if auto != automat:
                    auto = automat
                    if auto == False:
                        print('Automat has been disabled...')
                    else:
                        print('Automat has been enabled...')

                SetSpeed(leftSpeed, rightSpeed)

                if(auto):
                   
                    servoPos = 0
                else:
                    
                    if servo == 1:
                        ServoUp()
                    elif servo == -1:
                        ServoDown()
                    
        
            
        #else:
            #SetSpeed(direction[0] * speed + (direction[1] * speed)//2, direction[0] * speed - (direction[1] * speed)//2)
    
        if "b" in command:
            robot.Beep()
        if "e" in command:
            end()
        time.sleep(0.1)
        
    except:
        print("Stopped...")
        end()
end()
print("End program")
