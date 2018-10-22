#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket

#IP = '127.0.0.1' #айпи сервера
IP = '192.168.8.177' #айпи севера
PORT = 8000 #порт сервера

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #создаем udp клиент
msg = input("Enter message to send: ") #Ввод сообщения
client.sendto(msg.encode('utf-8'), (IP, PORT)) #Отправка сообщения на сервер

msg = client.recvfrom(1024) #принимаем ответ от сервера
reply = msg[0] #разбиваем ответ на сообщение
address = msg[1] #и адрес с портом откуда пришло сообщение
print('Serever reply: %s' % reply.decode('utf-8')) #выводим сообщение 
client.close() #закрываем клиент
