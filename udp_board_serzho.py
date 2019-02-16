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


def SetSpeed(leftSpeed, rightSpeed):
    robot.leftMotor.SetSpeed(leftSpeed)
    robot.rightMotor.SetSpeed(rightSpeed)
    return 0

def StopMotor():    
    robot.leftMotor.SetSpeed(0)
    robot.rightMotor.SetSpeed(0)
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
            os.popen('/home/pi/EduBot/mjpeg.py %s' % IP_RTP)
            
        if data != old_data and data[1][0] == IP_RTP : #если пакет данных "устарел", то игнорируем
            old_data = data
            return data
        else:
            return None
    except socket.timeout: #если вышло время, то выходим из цикла
        running = False
        print("Time is out...")

def update_current():
    """обновляем характеристики питании и записываем в список параметров"""
    global all_data
    all_data[1][3] = round(ina.voltage(), 2)
    all_data[1][4] = round(ina.current() / 1000, 3)
    
def print_data():
    """выводим на экран все важные данные из списка параметров"""
    global running
    global USER_IP
    while running:
        os.system('clear')#очищаем терминал
        if USER_IP:
            print("\nробот захвачен, IP - ", USER_IP)
        for i in range(len(all_data[0])):
            print(all_data[0][i], " : ", all_data[1][i]) #выводим все данные из all_data
        print("сервы - ", servo)
        time.sleep(0.1)
    #выводим характеристики питания
        
    send_reply(all_data)#отправляем параметры на пульт

def end():
    global running
    
    running = False
    StopMotor()
    robot.Release()
    server.close()
    
IP = str(os.popen('hostname -I | cut -d\' \' -f1').readline().replace('\n','')) #получаем IP, удаляем \n
PORT = 8000
IP_RTP = ''
#IP_RTP = '192.168.1.104'

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
    
#создаем и запускаем поток отображающий данные телеметрии да дисплее робота
stateThread = StateThread(robot, ina, disp)
stateThread.start()

running = True
direction = [0, 0]
command = []
servo = 0
first_cicle = True
old_data = []

while running:  
    try:
        global direction
        global command
        global all_data
        global first_cicle
        global IP_RTP
        global servo

        leftSpeed = 0 #скорость левого двигателя
        rightSpeed = 0 #скорость правого двигателя
        cmd = [] #список всех команд, отправляемых роботу
        data = recv_data()

        #update_current()
    
        if data:
            cmd, crc = pickle.loads(data[0]) #распаковываем команду и значение контрольной суммы
            crc_new = crc16.crc16xmodem(cmd) #расчитываем контрольную сумму полученных данных
            if crc == crc_new: #сравниваем контрольные суммы и проверяем целостность данных
                cmd = pickle.loads(cmd) #распаковываем список команд
                direction, speed, command, servo = cmd
                if servo == 1:
                    ServoUp()
                elif servo == -1:
                    ServoDown()
        
        SetSpeed(direction[0] * speed + (direction[1] * speed)//2, direction[0] * speed - (direction[1] * speed)//2)
    
        if "beep" in command:
            robot.Beep()
        if "end" in command:
            end()
        time.sleep(0.1)
        
    except (KeyboardInterrupt, SystemExit):
        print("KeyboardInterrupt")
        end()
end()
print("End program")
