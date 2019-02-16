#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pygame
import xmlrpc.client

sys.path.append('/home/serzho/RPicam-Streamer-master/')

import time
import receiver
import threading


SPEED = 350
ROTATE_K = 0.8
IP_ROBOT = '192.168.1.103'
SELF_IP = '192.168.1.104'

PORT = 8000
RTP_PORT = 5000

running = True

pygame.init() #инициализация Pygame

screen = pygame.display.set_mode([640, 360]) #создаем окно программы
clock = pygame.time.Clock() #для осуществления задержки
pygame.joystick.init() #инициализация библиотеки джойстика

client = xmlrpc.client.ServerProxy('http://%s:%d' % (IP_ROBOT, PORT))

recv = receiver.StreamReceiver(receiver.FORMAT_MJPEG, (SELF_IP, RTP_PORT))
screen = recv.play_pipeline()


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
                client.SetSpeed(-int(SPEED*ROTATE_K), int(SPEED*ROTATE_K))
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                client.SetSpeed(int(SPEED*ROTATE_K), -int(SPEED*ROTATE_K))
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                client.SetSpeed(-SPEED, -SPEED)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                client.SetSpeed(SPEED, SPEED)
            elif event.key == pygame.K_SPACE:
                client.Speak()
            elif event.key == pygame.K_PAGEUP:
                client.ServoUp()
            elif event.key == pygame.K_PAGEDOWN:
                client.ServoDown()
        elif event.type == pygame.KEYUP:
            client.StopMotor()
            
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
                
    clock.tick(30) #задержка обеспечивающая 30 кадров в секунду

recv.stop_pipeline()
recv.null_pipeline()

pygame.quit() #завершаем Pygame

