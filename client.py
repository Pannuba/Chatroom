#!/usr/bin/env python3

from socket import *
from threading import Thread
from tkinter import *

def listen():

	while True:		# Senza il loop lo fa solo una volta
		response = clientSocket.recv(512)
		response = response.decode('utf-8')

		if response == '__#@*^GOODBYE^*@#__':
			print('Server disconnected')
			break

		print(response)

def getMessage(self):
	message = textbox.get()
	textbox.delete(0, 'end')	# Svuota la barra di input
	
	if message == '':		# Controlla che il messaggio non sia vuoto
		print('Empty string, not sent')
	
	elif len(message) >= 512:	# Dovrei controllare dopo encoding, ma forse non cambia
		print('Message is too long (< 512 chars)')

	else:
		sendMessage(message)
	

def sendMessage(message):		# Finalmente funziona... Ma solo con "self". Nei tutorial non c'è
	message = message.encode('utf-8')	# Se premo solo invio il messaggio è b''
	clientSocket.send(message)	# Se è vuoto non lo manda!

serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

username = input('Username: ')
while len(username) >= 64:
	username = input('Username is too long (> 64 chars): ')
username = username.encode('utf-8')
clientSocket.send(username)

listenThread = Thread(target=listen, args=())
listenThread.daemon = True		# Per far chiudere il programma con quit(), altrimenti si blocca
listenThread.start()

root = Tk()
root.geometry('800x20')
root.title('SuperChat 9000 - logged in as ' + username.decode('utf-8'))
textbox = Entry(root)
textbox.bind("<Return>", getMessage)
textbox.pack(side = BOTTOM, fill = X)
root.mainloop()		# Fino a che non si chiude la GUI lo script non procede

clientSocket.send('!quit'.encode('utf-8'))	# Senza questo il server non chiude il socket e va in crisi
clientSocket.close()
quit()