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



IP = '192.168.8.177' #айпи сервера
PORT = 8000 #порт сервера

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #создаем udp клиент

keyListenerThread = threading.Thread(target = Listener)
keyListenerThread.start()

running = True

direction = ''

while running:
    #print(keys)
    try:
        if(keys.count("'a'")!=0)and(keys.count("'w'")==0)and(keys.count("'s'")==0)and(keys.count("'d'")==0):
            direction = ('LEFT')
        elif(keys.count("'a'")==0)and(keys.count("'w'")!=0)and(keys.count("'s'")==0)and(keys.count("'d'")==0):
            direction = ('UP')
        elif(keys.count("'a'")==0)and(keys.count("'w'")==0)and(keys.count("'s'")==0)and(keys.count("'d'")!=0):
            direction = ('RIGHT')
        elif(keys.count("'a'")==0)and(keys.count("'w'")==0)and(keys.count("'s'")!=0)and(keys.count("'d'")==0):
            direction = ('DOWN')
        elif(keys.count("'a'")!=0)and(keys.count("'w'")!=0)and(keys.count("'s'")==0)and(keys.count("'d'")==0):
            direction = ('LEFTUP')
        elif(keys.count("'a'")==0)and(keys.count("'w'")!=0)and(keys.count("'s'")==0)and(keys.count("'d'")!=0):
            direction = ('UPRIGHT')
        elif(keys.count("'a'")==0)and(keys.count("'w'")==0)and(keys.count("'s'")!=0)and(keys.count("'d'")!=0):
            direction = ('RIGHTDOWN')
        elif(keys.count("'a'")!=0)and(keys.count("'w'")==0)and(keys.count("'s'")!=0)and(keys.count("'d'")==0):
            direction = ('LEFTDOWN')
        elif(not("'a'" in keys)and not("'w'" in keys)and not("'s'" in keys)and not("'d'" in keys)):
            direction = 'None' 
        print(direction)
        time.sleep(0.1)
    except KeyboardInterrupt:
        print('Ctrl + c pressed!!!')
        break


