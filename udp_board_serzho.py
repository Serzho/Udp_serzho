#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import os
import pickle
import sys
sys.path.append('EduBot/EduBotLibrary')
import edubot

#IP = '127.0.0.1'
IP = str(os.popen('hostname -I | cut -d\' \' -f1').readline().replace('\n','')) #получаем IP, удаляем \n
PORT = 8000
TIMEOUT = 60

def SetSpeed(leftSpeed, rightSpeed):
    robot.leftMotor.SetSpeed(leftSpeed)
    robot.rightMotor.SetSpeed(rightSpeed)

def Beep():
    robot.Beep()
    return 0
    
robot = edubot.EduBot(1)
assert robot.Check(), 'EduBot not found!!!'
robot.Start() #обязательная процедура, запуск потока отправляющего на контроллер EduBot онлайн сообщений
print ('EduBot started!!!')

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #создаем UDP server
server.bind((IP, PORT)) #запускаем сервер
server.settimeout(TIMEOUT)
print("Listening %s on port %d..." % (IP, PORT))

while True:
    try:
        data = server.recvfrom(1024) # получаем UDP пакет
    except socket.timeout:
        print('Time is out...')
        break
    cmd, param = pickle.loads(data[0]) #разбиваем принятое сообщение на команду и параметры
    addr = data[1] #IP адрес и порт, откуда ссобщение пришло
    
    print(cmd, param, addr)

    if cmd == 'speed':
        leftSpeed, rightSpeed = param
        print('LeftSpeed: %d, RightSpeed: %d' % (leftSpeed, rightSpeed))
        SetSpeed(leftSpeed, rightSpeed)
    elif cmd == 'beep':
        Beep()
        print('Beep!!!')
        
    elif cmd == 'exit':
        break
       
    else:
        print('Unknown command: %s' % cmd)

server.close()

SetSpeed(0, 0)

#останавливаем поток отправки онлайн сообщений в контроллер EduBot
robot.Release()
print('End program')
