#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import pickle as pl

def SetSpeed(lS, rS):
    print(lS, rS)

IP = '192.168.8.173' #айпи сервера
PORT = 8000 #порт сервера
TIMEOUT = 60 #время ожидания ответа сервера [сек]

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #создаем udp сервер
server.bind((IP, PORT)) #запускаем udp сервер
print("Listening on port %d..." % PORT) #выводим сообщение о запуске сервера
server.settimeout(TIMEOUT) #указываем серверу время ожидания

stateMove = [0, 0]
leftSpeed = 0
rightSpeed = 0

while True: #создаем бесконечный цикл    
    try:
        data = server.recvfrom(1024) #попытка получить 1024 байта
    except socket.timeout:
        print("Time is out...")
        break
    msg = data[0] #разбиваем ответ на сообщение
    adrs = data[1] #и адресс с портом откуда пришло сообщение
    #print("Message: %s" % msg.decode'utf-8' + str(adrs))
    stateMove = pl.loads(msg)
    #print(stateMove)
    leftSpeed = stateMove[0] * 100 + stateMove[1] * 50
    rightSpeed = -stateMove[0] * 100 + stateMove[1] * 50
    SetSpeed(leftSpeed,rightSpeed)
    
    
server.close()
