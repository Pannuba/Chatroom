#!/usr/bin/env python3

from socket import *
from threading import Thread
from tkinter import *
from configparser import *
import signal, sys, time
from gui import *
from config import *

def quit(signum, frame):		# Eseguito quando viene premuto CTRL + C
	print('Quitting...')
	try:					# Solo qui il ; per concatenare metodi sullo stesso oggetto funziona...
		clientSocket.send('!quit'.encode('utf-8')); shutdown(); close()
	except:
		pass		# Per quando non si è ancora connesso al server
	sys.exit()


class LoginWindow:	# Non ho ben capito il ruolo di root e master, e le loro relazioni

	def __init__(self, master):
		self.master = master		# master = "LoginWindow"
		self.master.geometry('300x120')
		self.master.resizable(False, False)
		self.master.title('SuperChat 9000 - login')
		self.master.protocol("WM_DELETE_WINDOW", sys.exit)
		self.userLabel = Label(self.master, text='Username:')
		self.userLabel.pack()
		self.userField = Entry(self.master)
		self.userField.bind('<Return>', self.login)
		self.userField.pack(side=TOP)
		self.pwLabel = Label(self.master, text='Password:')
		self.pwLabel.pack()
		self.pwField = Entry(self.master, show='*')
		self.pwField.pack()
		self.button = Button(text='Login', command=self.login)	# Faccio userField globale?
		self.button.pack(side=BOTTOM)
		
	def login(self):
		global username, password, clientSocket		# Non so perché qua metto userField e in getMessage self, ma funziona
		username = self.userField.get()
		password = self.pwField.get()	# Svolge tutto il login in questa funzione
		self.userField.delete(0, 'end')

		if self.checkUsername(username) == False:
			self.master.quit()		# Con destroy non funziona
			self.master.mainloop()
			return
		
		try:
			clientSocket = socket(AF_INET, SOCK_STREAM)
			clientSocket.connect((serverName, serverPort))	# Connessione al server
			clientSocket.send(username.encode('utf-8'))		# Dentro o fuori dal try?
		except Exception as e:
			print(e)
			buildPopup(self.master, "Cannot connect to server", e)
		
		status = clientSocket.recv(16).decode('utf-8')

		if status == 'BANNED':							# Manca ADMIN, OK
			buildPopup(self.master, 'Banned', 'This user has been banned.')
			clientSocket.shutdown(SHUT_RDWR)
			clientSocket.close()
			return
			
		elif status == 'DUPLICATE':
			buildPopup(self.master, 'Login failed', 'This user is already connected to the server')
			return
			
		self.master.withdraw()
		self.newWindow = Toplevel(self.master)	# Toplevel è simile a Tk()
		self.app = ChatWindow(self.newWindow)

	def checkUsername(self, username):
		boolean = False

		if username == '':
			buildPopup(self.master, 'Login failed', 'Username field cannot be empty')

		elif len(username) > 16:
			buildPopup(self.master, 'Login failed', 'Username can\'t be longer than 16 characters')

		elif username.strip() != username:
			buildPopup(self.master, 'Login failed', 'Username cannot start or end with spaces')
		
		else:
			boolean = True

		return boolean


class ChatWindow:

	def __init__(self, master):
		self.master = master
		self.index = -1
		self.buffer = []
		self.master.protocol("WM_DELETE_WINDOW", self.master.quit)		# E non destroy (era self.master.quit)
		self.master.geometry('640x480')
		self.master.minsize(width=160, height=120)
		self.master.title('SuperChat 9000 - logged in as ' + username)
		self.textbox = Entry(self.master)
		self.textbox.bind('<Return>', self.getMessage)
		self.textbox.bind('<Up>', self.scrollBufferUp)
		self.textbox.bind('<Down>', self.scrollBufferDown)
		self.textbox.pack(side=BOTTOM, fill=X)
		self.chat = Text(self.master, state=DISABLED)	# Non ho bisogno di width e height perché ho expand in pack
		self.bar = Scrollbar(self.master, width=16, command=self.chat.yview)		# Scrollbar, chat window
		self.chat.bind('<1>', lambda event: self.chat.focus_set())	# Permette di copiare il testo, nonostante sia DISABLED
		self.chat.config(yscrollcommand=self.bar.set)
		self.bar.pack(side=RIGHT, fill=Y)
		self.chat.pack(expand=True, side=LEFT, fill=BOTH)
		listenThread = Thread(target=self.listen)			# arriva il messaggio di login la chat non è ancora stata creata e dà errore
		listenThread.daemon = True		# Per far chiudere il programma con sys.exit(), altrimenti si blocca
		listenThread.start()

	def scrollBufferUp(self, ciao):		# Prima o poi dovrò sistemare questi ciao
		self.index += 1

		if self.index > (len(self.buffer) - 1):
			self.index -= 1
			return

		self.textbox.delete(0, 'end')
		self.textbox.insert(END, self.buffer[self.index])

	def scrollBufferDown(self, ciao):
		self.index -= 1

		if self.index < 0:
			self.index = -1
			self.textbox.delete(0, 'end')
			return

		self.textbox.delete(0, 'end')
		self.textbox.insert(END, self.buffer[self.index])

	def getMessage(self, ciao):			# Finalmente funziona... Ma solo con "self". Nei tutorial non c'è
		message = self.textbox.get()
		self.textbox.delete(0, 'end')	# Svuota la barra di input
		
		if len(message) > 512:	# Dovrei controllare dopo encoding, ma forse non cambia
			print('Message is too long (< 512 chars)')

		elif message == '!quit':		# Potrei aggiungere risposte ad altri comandi
			buildQuitWindow(self.master)

		elif message != '':
			clientSocket.send(message.encode('utf-8'))
			self.index = -1		# Controllare che il messaggio inviato non è già stato mandato
			self.buffer.insert(0, message)
		
	def listen(self):
		while True:

			response = clientSocket.recv(512).decode('utf-8')	# Fare funzione per distinguere tra comando e risposta
			
			if response == 'GOODBYE':		# Fare una funzione per controllare la risposta?
				buildPopup(self.master, 'Disconnected', 'The server has shut down')
				buildQuitWindow(self.master)
				break

			self.chat.config(state=NORMAL)
			self.chat.insert(END, response + '\n')
			self.chat.see('end')
			self.chat.config(state=DISABLED) # Chiudere, tornare al login? è possibile eseguire una funzione quando termina un thread?


def main():
	global serverPort, serverName

	signal.signal(signal.SIGINT, quit)

	configFile = ConfigParser()

	try:
		configFile.read('client_config.ini')
		serverName = configFile.get('Settings', 'ip')
		serverPort = int(configFile.get('Settings', 'port'))
	except:
		print('client_config.ini is either missing, unreadable or badly set-up')
		quit(0, 0)

	app = LoginWindow(root)
	root.mainloop()
	
	quit(0, 0)		  # 0, 0 perché non so cosa fanno signum e frame


if __name__ == '__main__':
	main()