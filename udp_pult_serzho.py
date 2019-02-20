#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pygame
import os

#библиотеки для работы с сервером
import socket
import pickle

#sys.path.append('/home/serzho/RPicam-Streamer-master/')
sys.path.append('/home/user6/RPicam-Streamer')
import time
import receiver
import threading
import crc16

def onFrameCallback(data, width, height):
    frame = pygame.image.frombuffer(data, (width, height), 'RGB')
    screen.blit(frame, (0,0))
    
def sendCommand(data):
    global old_crc
    global running
    global IP_ROBOT
    global PORT
    
    if not running:
        data[2].append("e")
    data = pickle.dumps(data)#запаковываем данные
    crc = get_crc(data)#вычисляем контрольную сумму пакета
    msg = pickle.dumps((data, crc))#прикрепляем вычисленную контрольную сумму к пакету данных
    if crc != old_crc:#если есть изменения параметров, то отправляем на робота
        client.sendto(msg, (IP_ROBOT, PORT))
        old_crc = crc
        #print(keys, direction, power, cmd, servo)
    
def get_crc(data):
    return crc16.crc16xmodem(data)
    
def recv_reply():
    global reply
    reply = client.recvfrom(1024) #принимаем ответ от сервера
    print("Reply: %s", reply) #выводим сообщение
    
def end():
    client.close() #закрываем udp клиент
    print("End program")
    recv.stop_pipeline()
    recv.null_pipeline()
    pygame.quit() #завершаем Pygame


keys = set()

SPEED = 350
ROTATE_K = 0.8
IP_ROBOT = '192.168.8.161'
SELF_IP = str(os.popen('hostname -I | cut -d\' \' -f1').readline().replace('\n',''))

PORT = 8000
RTP_PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

running = True

pygame.init() #инициализация Pygame
pygame.mixer.quit()

screen = pygame.display.set_mode([320, 240]) #создаем окно программы
clock = pygame.time.Clock() #для осуществления задержки
pygame.joystick.init() #инициализация библиотеки джойстика


recv = receiver.StreamReceiver(receiver.VIDEO_MJPEG, onFrameCallback)
recv.setHost(IP_ROBOT)
recv.setPort(RTP_PORT)
recv.play_pipeline()

fraps = 24

old_crc = None

command = []
direction = [0,0]
automat = False 

myFont = pygame.font.Font(None, 26)
text = myFont.render('', True, [255,0,0])
try:
    joy = pygame.joystick.Joystick(0) # создаем объект джойстик
    joy.init() # инициализируем джойстик
    print('Enabled joystick: ' + joy.get_name())
except pygame.error:
    print('no joystick found.')

while running:
    for event in pygame.event.get(): #пробегаемся в цикле по всем событиям Pygame
        #print(event)
        if 'b' in command:
            command.remove('b')
        if event.type == pygame.QUIT: #проверка на выход из окна
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                keys.add("l")
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                keys.add("r")
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                keys.add("u")
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                keys.add("d")
            elif event.key == pygame.K_SPACE:
                command.append("b")
            elif event.key == pygame.K_PAGEUP:
                keys.add("su")
            elif event.key == pygame.K_PAGEDOWN:
                keys.add("sd")
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                keys.remove("l")
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                keys.remove("r")
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                keys.remove("u")
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                keys.remove("d")
            elif event.key == pygame.K_PAGEUP:
                keys.remove("su")
            elif event.key == pygame.K_PAGEDOWN:
                keys.remove("sd")
            
        elif event.type == pygame.JOYAXISMOTION: #перемещение стиков
            if event.axis == 2:
                if event.value > 0:
                    keys.add("sd")
                else:
                    try:
                        keys.remove("sd")
                    except:
                        pass
            elif event.axis == 5:
                if event.value > 0:
                    keys.add("su")
                else:
                    try:
                        keys.remove("su")
                    except:
                        pass
                    
            elif event.axis == 0:
                if event.value > 0.2:
                    keys.add("r")
                elif event.value < -0.2:
                    keys.add("l")
                elif abs(event.value) < 0.2:
                    try:
                        keys.remove("r")
                    except:
                        pass
                    try:
                        keys.remove("l")
                    except:
                        pass
                    
            elif event.axis == 1:
                if event.value > 0.2:
                    keys.add("d")
                elif event.value < -0.2:
                    keys.add("u")
                elif abs(event.value) < 0.2:
                    try:
                        keys.remove("d")
                    except:
                        pass
                    try:
                        keys.remove("u")
                    except:
                        pass
                
        elif event.type == pygame.JOYBUTTONDOWN:
            #print(event)
            if event.button == 5:
                SPEED += 10
                print(SPEED)
            elif event.button == 4:
                SPEED -= 10
                print(SPEED)
            elif event.button == 7:
                command.append("b")
            elif event.button == 8:
                command.append("b")
                running = False
            elif event.button == 3:
                automat = not(automat)
                if(automat):
                    text = myFont.render('AUTOMAT ENABLED', True, [255,0,0])
                else:
                    text = myFont.render('', True, [255,0,0])
        
        direction[0] = int("d" in keys) - int("u" in keys)
        direction[1] = int("r" in keys) - int("l" in keys)
        servo = int("su" in keys) - int("sd" in keys)
        
        sendCommand((direction, SPEED, command, servo, automat))
    screen.blit(text, [10, 10])
    pygame.display.update()         
    clock.tick(fraps) #задержка обеспечивающая 30 кадров в секунду

end()
