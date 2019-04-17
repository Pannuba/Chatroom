#!/usr/bin/env python3

from socket import *
from threading import Thread
from tkinter import *		# import as tk?
from configparser import *
import signal

def sigint_handler(signum, frame):		# Eseguito quando viene premuto CTRL + C
	print('Quitting...')
	clientSocket.send('!quit'.encode('utf-8'))
	clientSocket.close()
	quit()

def buildLoginWindow():
	global loginWindow
	loginWindow = Tk()													# Window
	loginWindow.geometry('300x120')
	loginWindow.resizable(False, False)
	loginWindow.title('SuperChat 9000 - login')
	loginWindow.protocol("WM_DELETE_WINDOW", quit)
	userLabel = Label(loginWindow, text = 'Username:')					# User label
	userLabel.pack()
	userField = Entry(loginWindow)										# User field
	userField.pack(side = TOP)
	pwLabel = Label(loginWindow, text = 'Password:')					# Password label
	pwLabel.pack()
	pwField = Entry(loginWindow)										# Password field
	pwField.pack()
	button = Button(text = 'Login', command = lambda: login(userField, pwField, loginWindow))	# Faccio userField globale?
	button.pack(side = BOTTOM)

def buildChatWindow():
	global chatWindow, textbox, chat
	chatWindow = Tk()													# Window
	chatWindow.geometry('640x480')
	chatWindow.minsize(width = 160, height = 120)
	chatWindow.title('SuperChat 9000 - logged in as ' + username)
	textbox = Entry(chatWindow)											# Textbox
	textbox.bind("<Return>", getMessage)
	textbox.pack(side = BOTTOM, fill = X)
	chat = Text(chatWindow, state = DISABLED)	# Non ho bisogno di width e height perché ho expand in pack
	bar = Scrollbar(chatWindow, width = 16, command = chat.yview)		# Scrollbar, chat window
	chat.bind("<1>", lambda event: chat.focus_set())	# Permette di copiare il testo, nonostante sia DISABLED
	chat.config(yscrollcommand = bar.set)
	bar.pack(side = RIGHT, fill = Y)
	chat.pack(expand = True, side = LEFT, fill = BOTH)

def login(userField, pwField, loginWindow):
	global username, password		# Non so perché qua metto userField e in getMessage self, però funziona
	username = userField.get()		# Controllare lunghezza username... Ma come con Tkinter?
	password = pwField.get()	# svolge tutto il login in questa funzione
	
	while username == '':		# Non va
		loginWindow.destroy()
		print('no')
	
	clientSocket.connect((serverName, serverPort))	# Connessione al server
	clientSocket.send(username.encode('utf-8'))		# Se non va fare encode nella linea prima
	loginWindow.destroy()		# Così lo script procede

def listen():
	
	while True:		# Senza il loop lo fa solo una volta
		response = clientSocket.recv(512)
		response = response.decode('utf-8')		# Fare funzione per distinguere tra comando e risposta

		if response == 'GOODBYE':		# Fare una funzione per controllare la risposta?
			print('Server disconnected')
			break
		
		elif response == 'BANNED':
			print('This user has been banned')
			break

		chat.config(state = NORMAL)		# Perché altrimenti non si aggiorna
		chat.insert(END, response + '\n')
		chat.config(state = DISABLED)

def getMessage(self):			# Finalmente funziona... Ma solo con "self". Nei tutorial non c'è
	message = textbox.get()
	textbox.delete(0, 'end')	# Svuota la barra di input
	
	if message == '':		# Controlla che il messaggio non sia vuoto
		print('Empty string, not sent')
	
	elif len(message) > 512:	# Dovrei controllare dopo encoding, ma forse non cambia
		print('Message is too long (< 512 chars)')

	else:
		clientSocket.send(message.encode('utf-8'))

def main():
	global serverPort, serverName, clientSocket

	signal.signal(signal.SIGINT, sigint_handler)

	config = ConfigParser()
	config.read('client_config.ini')
	serverPort = int(config.get('Settings', 'port'))

	serverName = 'localhost'
	clientSocket = socket(AF_INET, SOCK_STREAM)

	buildLoginWindow()
	loginWindow.mainloop()

	'''username = input('Username: ')
	while len(username) > 16:
		username = input('Username is too long (< 16 chars): ')
	username = username.encode('utf-8')
	clientSocket.send(username)'''

	listenThread = Thread(target=listen, args=())
	listenThread.daemon = True		# Per far chiudere il programma con quit(), altrimenti si blocca
	listenThread.start()

	buildChatWindow()
	chatWindow.mainloop()		# Fino a che non si chiude la GUI lo script non procede
	
	sigint_handler(0, 0)		  # 0, 0 perché non so cosa fanno signum e frame

if __name__ == '__main__':
	main()