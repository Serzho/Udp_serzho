#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import os
import pickle as pl
import sys
sys.path.append('EduBot/EduBotLibrary')
import edubot
import crc16

def SetSpeed(leftSpeed, rightSpeed):
    robot.leftMotor.SetSpeed(leftSpeed)
    robot.rightMotor.SetSpeed(rightSpeed)

IP = '192.168.8.163' #айпи сервера
PORT = 8000 #порт сервера
TIMEOUT = 60 #время ожидания ответа сервера [сек]

robot = edubot.EduBot(1)
assert robot.Check(), 'EduBot not found!!!'
robot.Start() #обязательная процедура, запуск потока отправляющего на контроллер EduBot онлайн сообщений
print ('EduBot started!!!')
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #создаем udp сервер

server.bind((IP, PORT)) #запускаем udp сервер
print("Listening on port %d..." % PORT) #выводим сообщение о запуске сервера
server.settimeout(TIMEOUT) #указываем серверу время ожидания

stateMove = [0, 0]
leftSpeed = 0
rightSpeed = 0

while True: #создаем бесконечный цикл    
    try:
        packet = server.recvfrom(1024) #попытка получить 1024 байта
    except socket.timeout:
        print("Time is out...")
        break

    #print("Message: %s" % msg.decode'utf-8' + str(adrs))
    data = packet[0]

    crcBytes = data[-2:]
    crc = int.from_bytes(crcBytes, byteorder="big", signed = False)

    stateMoveBytes = data[:-2]
    newCrc = crc16.crc16xmodem(stateMoveBytes)
    #print(crc, newCrc)
    if crc == newCrc:
    #print(stateMove)
        stateMove = pl.loads(stateMoveBytes)
        leftSpeed = stateMove[1] * 450 + stateMove[0] * 300
        rightSpeed = -stateMove[1] * 450 + stateMove[0] * 300
        SetSpeed(leftSpeed,rightSpeed)
        #print(leftSpeed, rightSpeed)
    
server.close()
SetSpeed(0, 0)
robot.Release()
