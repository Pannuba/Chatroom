#!/usr/bin/env python3

from socket import *
from threading import Thread
from tkinter import *
from configparser import *
import signal, sys, time

def quit(signum, frame):		# Eseguito quando viene premuto CTRL + C
	print('Quitting...')
	try:					# Solo qui il ; per concatenare metodi sullo stesso oggetto funziona...
		clientSocket.send('!quit'.encode('utf-8')); shutdown(); close()
	except:
		pass		# Per quando non si è ancora connesso al server
	sys.exit()

def checkUsername(username):

	boolean = False

	if len(username) > 16:
		popup('Login failed', 'Username can\'t be longer than 16 characters')

		if username.strip() != username:
			popup('Login failed', 'Username cannot start or end with spaces')

	if username == '':
		popup('Login failed', 'Username field cannot be empty')
	
	else:
		boolean = True

	return boolean

def popup(title, message):		# Creare un popup di errore, o passare qua un parametro che faccia uscire?
	popup = Tk()
	popup.geometry('320x80')
	popup.resizable(False, False)
	popup.title(title)
	popup.focus()
	popup.protocol("WM_DELETE_WINDOW", popup.destroy)
	popupMessage = Label(popup, text=message, pady=10)#, width=20, height=20)
	popupMessage.pack(side=TOP, fill=BOTH)		# Forse fill non va
	popupButton = Button(popup, text='OK', command=popup.destroy)
	popupButton.pack(side=BOTTOM, pady=10)
	popup.mainloop()

def buildQuitWindow():
	global quitWindow
	quitWindow = Tk()
	quitWindow.geometry('100x100')
	quitWindow.resizable(False, False)
	quitWindow.title('Are you sure you want to quit?')
	quitWindow.focus()
	yesButton = Button(quitWindow, text='Yes', command=quitWindow.destroy)	# Per ora entrambi sono destroy
	yesButton.pack(side=LEFT)
	noButton = Button(quitWindow, text='No', command=quitWindow.destroy)
	noButton.pack(side=RIGHT)

def buildLoginWindow():
	global loginWindow
	loginWindow = Tk()													# Window
	loginWindow.geometry('300x120')
	loginWindow.resizable(False, False)
	loginWindow.title('SuperChat 9000 - login')
	loginWindow.protocol("WM_DELETE_WINDOW", sys.exit)
	userLabel = Label(loginWindow, text='Username:')					# User label
	userLabel.pack()
	userField = Entry(loginWindow)										# User field
	userField.pack(side=TOP)
	pwLabel = Label(loginWindow, text='Password:')					# Password label
	pwLabel.pack()
	pwField = Entry(loginWindow, show='*')										# Password field
	pwField.pack()
	button = Button(text='Login', command=lambda: login(userField, pwField, loginWindow))	# Faccio userField globale?
	button.pack(side=BOTTOM)

def buildChatWindow():
	global chatWindow, textbox, chat
	chatWindow = Tk()													# Window
	chatWindow.geometry('640x480')
	chatWindow.minsize(width=160, height=120)
	chatWindow.title('SuperChat 9000 - logged in as ' + username)
	textbox = Entry(chatWindow)											# Textbox
	textbox.bind("<Return>", getMessage)
	textbox.pack(side=BOTTOM, fill=X)
	chat = Text(chatWindow, state=DISABLED)	# Non ho bisogno di width e height perché ho expand in pack
	bar = Scrollbar(chatWindow, width=16, command=chat.yview)		# Scrollbar, chat window
	chat.bind("<1>", lambda event: chat.focus_set())	# Permette di copiare il testo, nonostante sia DISABLED
	chat.config(yscrollcommand=bar.set)
	bar.pack(side=RIGHT, fill=Y)
	chat.pack(expand=True, side=LEFT, fill=BOTH)

def login(userField, pwField, loginWindow):
	global username, password, clientSocket		# Non so perché qua metto userField e in getMessage self, ma funziona
	username = userField.get()
	password = pwField.get()	# Svolge tutto il login in questa funzione
	userField.delete(0, 'end')

	if not checkUsername(username):
		loginWindow.quit()		# Con destroy non funziona
		loginWindow.mainloop()
		return
	
	try:	# Il client invia un BrokenPipeError quando si connette dopo il popup di ban
		clientSocket = socket(AF_INET, SOCK_STREAM)
		clientSocket.connect((serverName, serverPort))	# Connessione al server
		clientSocket.send(username.encode('utf-8'))		# Dentro o fuori dal try?
	except Exception as e:
		print(e)
		popup('Cannot connect to server', e)	# Quit?
	
	status = clientSocket.recv(16).decode('utf-8')

	if status == 'BANNED':							# Manca ADMIN, OK
		popup('Banned', 'This user has been banned.')
		clientSocket.shutdown(SHUT_RDWR)
		clientSocket.close()
		loginWindow.quit()
		loginWindow.mainloop()
		return
		
	elif status == 'DUPLICATE':
		popup('Login failed', 'This user is already connected to the server')
		loginWindow.quit()
		loginWindow.mainloop()
		return
	
	loginWindow.destroy()

def getMessage(self):			# Finalmente funziona... Ma solo con "self". Nei tutorial non c'è
	message = textbox.get()
	textbox.delete(0, 'end')	# Svuota la barra di input
	
	if message == '':		# Controlla che il messaggio non sia vuoto
		print('Empty string, not sent')
	
	elif len(message) > 512:	# Dovrei controllare dopo encoding, ma forse non cambia
		print('Message is too long (< 512 chars)')

	elif message == '!quit':		# Potrei aggiungere risposte ad altri comandi
		buildQuitWindow()
		quitWindow.mainloop()
		#print('ora passa a sigint')		# Perché lo stampa quando chiudo la chatWindow?
		quit(0, 0)

	else:
		clientSocket.send(message.encode('utf-8'))
	
def listen():
	
	while True:

		response = clientSocket.recv(512).decode('utf-8')	# Fare funzione per distinguere tra comando e risposta
		
		if response == 'GOODBYE':		# Fare una funzione per controllare la risposta?
			popup('Disconnected', 'The server has shut down')
			break

		chat.config(state=NORMAL)
		chat.insert(END, response + '\n')
		chat.see('end')
		chat.config(state=DISABLED)
	# Chiudere, tornare al login? è possibile eseguire una funzione quando termina un thread?

def main():
	global serverPort, serverName

	signal.signal(signal.SIGINT, quit)

	config = ConfigParser()

	try:
		config.read('client_config.ini')
		serverName = config.get('Settings', 'ip')
		serverPort = int(config.get('Settings', 'port'))
	except:
		print('client_config.ini is either missing, unreadable or badly set-up')
		quit(0, 0)

	buildLoginWindow()
	loginWindow.mainloop()
	buildChatWindow()								# Costruisco la finestra prima del thread perché altrimenti quando
	listenThread = Thread(target=listen)			# arriva il messaggio di login la chat non è ancora stata creata e dà errore
	listenThread.daemon = True		# Per far chiudere il programma con sys.exit(), altrimenti si blocca
	listenThread.start()
	chatWindow.mainloop()		# Fino a che non si chiude la GUI lo script non procede
	
	quit(0, 0)		  # 0, 0 perché non so cosa fanno signum e frame

if __name__ == '__main__':
	main()