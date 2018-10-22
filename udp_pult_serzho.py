#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import pickle as pl

def SendCommand(cmd, param):
    msg = pl.dumps([cmd, param])
    client.sendto(msg, (IP, PORT))

def SetSpeed(leftSpeed, rightSpeed):
    SendCommand('speed', (leftSpeed, rightSpeed))
    
    
IP = '127.0.0.1' #айпи сервера
PORT = 8000 #порт сервера

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #создаем udp клиент

SetSpeed(100,100)

client.close()
