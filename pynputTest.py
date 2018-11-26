#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pynput import keyboard, mouse

import socket
import pickle as pl
import time

import threading

keys = []

def SendMessage(msg):
    client.sendto(str(msg).encode('utf-8'), (IP, PORT))
    
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



IP = '192.168.8.173' #айпи сервера
PORT = 8000 #порт сервера

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #создаем udp клиент

keyListenerThread = threading.Thread(target = Listener)
keyListenerThread.start()

stateMove = [0, 0]

running = True

direction = ''

while running:
    #print(keys)
    try:
        stateMove = [-int("'a'" in keys) + int("'d'" in keys), \
                     -int("'s'"in keys) + int("'w'" in keys)]
        print(stateMove)
        SendMessage(str(stateMove[0]) + ' , ' + str(stateMove[1]))
        time.sleep(0.1)
    except KeyboardInterrupt:
        print('Ctrl + c pressed!!!')
        break


