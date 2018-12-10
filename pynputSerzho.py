#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pynput import keyboard, mouse

import socket
import pickle as pl
import time
import crc16

import threading

keys = []

def SendMessage(msg):
    client.sendto(msg, (IP, PORT))
    
def OnPress(key):
    global listener
    #print("Press ", str(key))
    #Остановка листенера
    if(str(key) in keys) == False:
        keys.append(str(key))
    if key == keyboard.Key.insert: #Остановка на нужную кнопку
        return False

def OnRelease(key):
    while (str(key) in keys) == True:
        keys.remove(str(key))
    #print("Release ", key)

def Listener():
    global running
    listener = keyboard.Listener(on_press = OnPress, on_release = OnRelease)    
    listener.start()
    listener.join()
    running = False



IP = '192.168.8.163' #айпи сервера
PORT = 8000 #порт сервера
BASE_SPEED = 500
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #создаем udp клиент

keyListenerThread = threading.Thread(target = Listener)
keyListenerThread.start()

stateMove = [0, 0]
running = True

direction = ''

while running:
    #print(keys)
    try:
        stateMove = [-int("'w'" in keys) + int("'s'" in keys), \
                     -int("'d'"in keys) + int("'a'" in keys)]
        print(stateMove)

        stateMoveBytes = pl.dumps((BASE_SPEED, stateMove), protocol = 3)

        crc = crc16.crc16xmodem(stateMoveBytes)
        crcBytes = crc.to_bytes(2, byteorder='big', signed = False)

        data = stateMoveBytes + crcBytes
        SendMessage(data)
        time.sleep(0.1)
    except KeyboardInterrupt:
        print('Ctrl + c pressed!!!')
        break


