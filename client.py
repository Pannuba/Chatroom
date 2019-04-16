#!/usr/bin/env python3

from socket import *
from threading import Thread
from tkinter import *
import signal

def sigint_handler(signum, frame):		# Eseguito quando viene premuto CTRL + C
	print('Quitting...')
	clientSocket.send('!quit'.encode('utf-8'))
	clientSocket.close()
	quit()

def listen():

	while True:		# Senza il loop lo fa solo una volta
		response = clientSocket.recv(512)
		response = response.decode('utf-8')

		if response == 'GOODBYE':		# Fare una funzione per controllare la risposta?
			print('Server disconnected')
			break
		
		elif response == 'BANNED':
			print('This user has been banned')
			break

		#print(response)
		chat.insert(END, response + '\n')


def getMessage(self):			# Finalmente funziona... Ma solo con "self". Nei tutorial non c'è
	message = textbox.get()
	textbox.delete(0, 'end')	# Svuota la barra di input
	
	if message == '':		# Controlla che il messaggio non sia vuoto
		print('Empty string, not sent')
	
	elif len(message) > 512:	# Dovrei controllare dopo encoding, ma forse non cambia
		print('Message is too long (< 512 chars)')

	else:
		sendMessage(message)
	

def sendMessage(message):
	message = message.encode('utf-8')	# Se premo solo invio il messaggio è b''
	clientSocket.send(message)	# Se è vuoto non lo manda!

def main():
	signal.signal(signal.SIGINT, sigint_handler)

	serverName = 'localhost'
	serverPort = 12000
	global clientSocket
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect((serverName, serverPort))

	username = input('Username: ')
	while len(username) > 64:
		username = input('Username is too long (< 64 chars): ')
	username = username.encode('utf-8')
	clientSocket.send(username)

	listenThread = Thread(target=listen, args=())
	listenThread.daemon = True		# Per far chiudere il programma con quit(), altrimenti si blocca
	listenThread.start()

	root = Tk()
	root.geometry('1280x720')
	root.title('SuperChat 9000 - logged in as ' + username.decode('utf-8'))
	global textbox
	textbox = Entry(root)
	textbox.bind("<Return>", getMessage)
	textbox.pack(side = BOTTOM, fill = X)
	global chat
	chat = Text(root, height=100)		# Senza height non si estende a tutta la finestra
	chat.pack(side = TOP, fill = BOTH)
	root.mainloop()		# Fino a che non si chiude la GUI lo script non procede

	clientSocket.send('!quit'.encode('utf-8'))	# Senza questo il server non chiude il socket e va in crisi
	clientSocket.close()
	quit()

if __name__ == '__main__':
	main()