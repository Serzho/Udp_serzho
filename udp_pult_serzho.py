#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import pickle as pl
import time
import pygame

def SendCommand(cmd, param = 0):
    msg = pl.dumps([cmd, param])
    client.sendto(msg, (IP, PORT))

def SetSpeed(leftSpeed, rightSpeed):
    SendCommand('speed', (leftSpeed, rightSpeed))
    
def Beep():
    SendCommand('beep')

def Exit():
    SendCommand('exit')

SPEED = 200
ROTATE_K = 0.8
IP = '192.168.8.163' #айпи сервера
PORT = 8000 #порт сервера

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #создаем udp клиент

running = True

pygame.init() #инициализация Pygame

screen = pygame.display.set_mode([640, 480]) #создаем окно программы
clock = pygame.time.Clock() #для осуществления задержки
pygame.joystick.init() #инициализация библиотеки джойстика

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
            if event.key == pygame.K_LEFT:
                SetSpeed(int(SPEED*ROTATE_K), -int(SPEED*ROTATE_K))
            elif event.key == pygame.K_RIGHT:
                SetSpeed(-int(SPEED*ROTATE_K), int(SPEED*ROTATE_K))
            elif event.key == pygame.K_UP:
                SetSpeed(SPEED, SPEED)
            elif event.key == pygame.K_DOWN:
                SetSpeed(-SPEED, -SPEED)
            elif event.key == pygame.K_SPACE:
                Beep()
            elif event.key == pygame.K_PAGEUP:
                pass
            elif event.key == pygame.K_PAGEDOWN:
                pass
        elif event.type == pygame.KEYUP:
            SetSpeed(0,0)
            
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

pygame.quit() #завершаем Pygame

client.close()
