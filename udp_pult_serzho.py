#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pygame
import os

#библиотеки для работы с сервером
import socket
import pickle

sys.path.append('/home/serzho/RPicam-Streamer-master/')

import time
import receiver
import threading
import crc16


def sendCommand(data):
    global old_crc
    global running
    global IP_ROBOT
    global PORT
    
    if not running:
        data[2].append("end")
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
IP_ROBOT = '192.168.1.103'
SELF_IP = str(os.popen('hostname -I | cut -d\' \' -f1').readline().replace('\n',''))

PORT = 8000
RTP_PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

running = True

pygame.init() #инициализация Pygame
pygame.mixer.quit()

screen = pygame.display.set_mode([640, 360]) #создаем окно программы
clock = pygame.time.Clock() #для осуществления задержки
pygame.joystick.init() #инициализация библиотеки джойстика


recv = receiver.StreamReceiver(receiver.FORMAT_MJPEG, (SELF_IP, RTP_PORT))
screen = recv.play_pipeline()

fraps = 24

old_crc = None

command = []
direction = [0,0]

try:
    joy = pygame.joystick.Joystick(0) # создаем объект джойстик
    joy.init() # инициализируем джойстик
    print('Enabled joystick: ' + joy.get_name())
except pygame.error:
    print('no joystick found.')

while running:
    for event in pygame.event.get(): #пробегаемся в цикле по всем событиям Pygame
        #print(event)
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
                command.append("beep")
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
            #print(event)
            if event.axis == 1:
                print('0', event.value)
                if event.value > 0:
                    client.SetSpeed(-100, -100)
                elif event.value < 0:
                    client.SetSpeed(100, 100)
                else:
                    client.StopMotor()
            elif event.axis == 0:
                print('1', event.value)
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                client.Speak()

        direction[0] = int("d" in keys) - int("u" in keys)
        direction[1] = int("r" in keys) - int("l" in keys)
        servo = int("su" in keys) - int("sd" in keys)
        
        sendCommand((direction, SPEED, command, servo))
                
    clock.tick(fraps) #задержка обеспечивающая 30 кадров в секунду

end()
