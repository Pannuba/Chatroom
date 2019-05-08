#!/usr/bin/env python3

'''TODO:	* BUG: trying to login twice as banned throws errors
			* BUG: string index out of range in client when server quits
			* Creare comando per listare gli utenti loggati
			* Sistema di login con utente e password
			* Fare funzione per distinguere tra comando e risposta
			* Colori custom in file config
			* Inviare file, evidenziare link... magari...
'''

from socket import *
from threading import Thread
from time import strftime
from configparser import *
import signal, sys, os
from tkinter import *

helpmessage =	'\nSERVER: Welcome to SuperChat 9000! Here\'s a list of available commands:\n\
				\n!quit: you quit\n!help: shows this message\n\nHave fun, or something.\n'.encode('utf-8')


class Window:

	def __init__(self, master):
		self.master = master
		self.index = -1
		self.buffer = []
		self.master.protocol("WM_DELETE_WINDOW", self.master.quit)
		self.master.geometry('640x480')
		self.master.minsize(width=160, height=120)
		self.master.title('Server lol')
		self.textbox = Entry(self.master)
		self.textbox.bind('<Return>', self.getMessage)
		self.textbox.bind('<Up>', self.scrollBufferUp)
		self.textbox.bind('<Down>', self.scrollBufferDown)
		self.textbox.pack(side='bottom', fill='x')
		self.textbox.focus()
		self.chat = Text(self.master, state='disabled')
		self.bar = Scrollbar(self.master, width=16, command=self.chat.yview)
		self.chat.bind('<1>', lambda event: self.chat.focus_set())
		self.chat.config(yscrollcommand=self.bar.set)
		self.bar.pack(side='right', fill='y')
		self.chat.pack(expand=True, side='left', fill='both')

	def scrollBufferUp(self, *args):
		self.index += 1

		if self.index > (len(self.buffer) - 1):
			self.index -= 1
			return

		self.textbox.delete(0, 'end')
		self.textbox.insert('end', self.buffer[self.index])

	def scrollBufferDown(self, *args):
		self.index -= 1

		if self.index < 0:
			self.index = -1
			self.textbox.delete(0, 'end')
			return

		self.textbox.delete(0, 'end')
		self.textbox.insert('end', self.buffer[self.index])

	def getMessage(self, *args):			# Finalmente funziona... Ma solo con "self". Nei tutorial non c'è
		message = self.textbox.get()
		message = '!' + message
		self.textbox.delete(0, 'end')	# Svuota la barra di input
		
		if len(message) > 512:	# Dovrei controllare dopo encoding, ma forse non cambia
			print('Message is too long (< 512 chars)')

		elif message == '!shutdown':		# Potrei aggiungere risposte ad altri comandi
			#buildQuitWindow(self.master)
			self.master.quit()					# Devo aggiungere quitwindow

		elif message != '':
			sendToAll(message)
			self.index = -1		# Controllare che il messaggio inviato non è già stato mandato
			self.buffer.insert(0, message)


def quit(signum, frame):		# Eseguito quando viene premuto CTRL + C
	log('Quitting...')

	for i in socketList:
		i.send('!disconnect'.encode('utf-8'))
		i.close()
		
	sys.exit()


def log(logMessage):	# Mostra un messaggio nel terminale, nella finestra e lo aggiunge a chat.log
	print(logMessage)
	try:
		app.chat.config(state='normal')
		app.chat.insert('end', logMessage + '\n')
		app.chat.see('end')
		app.chat.config(state='disabled')
	except:		# Per quando non è ancora stata creata la finestra in main
		pass
	with open(path + '/chat.log', 'a') as logfile:
		logfile.write(logMessage + '\n')


def sendToAll(message):

	try:
		for i in socketList:
			i.send(message.encode('utf-8'))
	except Exception as e:
		print(e)	# Cercare di renderla loggabile per quando è un broken pipe
		quit(0,0)


def checkUser(user, socket, ip):
	status = 'OK'

	try:
		admins = open(path + '/admins.txt', 'r')
		banned = open(path + '/banned.txt', 'r')
	except Exception as e:
		log(e)
		quit(0, 0)

	for i in admins:
		if user == i.rstrip('\n'):		# I file devono terminare con una linea vuota
			log(user + ' is an admin')
			status = 'ADMIN'
	
	for i in banned:
		if user == i.rstrip('\n'):		# Senza rstrip conta gli \n come linee indipendenti
			log(strftime('%Y-%m-%d %H:%M:%S') + ' ' + user + ' (' + ip + ') has attempted to join the server, but is banned')
			status = 'BANNED'

	for i in usersList:
		if user == i:
			log(strftime('%Y-%m-%d %H:%M:%S') + ' ' + user + ' (' + ip + ') has attempted to join the server, but is already logged in')
			status = 'DUPLICATE'	
	
	admins.close()
	banned.close()
	socket.send(status.encode('utf-8'))
	return status


def clientHandler(connectionSocket, user):		# Thread che legge i messaggi dei client lasciare separato o integrare in classe gui??? funzione log come accede a gui?? devo mettere tutto

	while True:
		message = connectionSocket.recv(512).decode('utf-8')	# Attende la ricezione di un messaggio

		if message == '!quit':		# Controllare per altri comandi (fare funzione). Posso fare che se il primo 
			break					# carattere è un ! controlla il comando, se non lo trova consiglia di fare !help
		
		if message == '!help':							# Funzione checkmessage?
			connectionSocket.send(helpmessage)
		
		if message == '!users':
			connectionSocket.send(('Currently logged in users: ' + ', '.join(usersList)).encode('utf-8'))
		
		else:
			response = user + ': ' + message
			log(strftime('%Y-%m-%d %H:%M:%S') + ' Message from ' + response)
			sendToAll(strftime('%H:%M') + ' ' + response)

	connectionSocket.close()				# Se non rimuovo il client disconnesso dall'array, quando
	socketList.remove(connectionSocket)		# distribuisco il messaggio a tutti si impalla						# AGGIUNGERE GUI A LOG
	usersList.remove(user.lower())
	log(strftime('%Y-%m-%d %H:%M:%S') + ' ' + user + ' has left the server')		# Si termina il thread per un client connesso
	sendToAll(user + ' has left the server')


def acceptConnetions(serverSocket):			# Thread che accetta nuove connessioni
	global socketList, usersList
	
	while True:
		newSocket, (ip, port) = serverSocket.accept()		# l'esecuzione torna all'inizio del while e si mette in "pausa" a serversocket.accept()
		user = newSocket.recv(16).decode('utf-8')			# Modificato clientAddress in ip, port per ottenere l'IP in una variabile

		while (checkUser(user.lower(), newSocket, ip)) != 'OK':		# Trovare un modo più efficiente senza ripetere. While? Bool?
			#newSocket.close() serve??
			newSocket, (ip, port) = serverSocket.accept()		# Con questi il server non manda due cose di fila, così il client non ha problemi
			user = newSocket.recv(16).decode('utf-8')				# con l'OK il client deve inviare un "ACK" ricevuto dal server in handler o qua

		socketList.append(newSocket)
		usersList.append(user.lower())
		log(ip + ' has joined the server as ' + user)	# Dovevo usare format() perché clientAddress è una tuple e lo manda in palla
		sendToAll(user + ' has joined the server')
		clientThread = Thread(target=clientHandler, args=(newSocket, user))
		clientThread.daemon = True		# Sennò quit() si blocca
		clientThread.start()


def main():
	global socketList, usersList, logfile, path, app
	socketList = []
	usersList = []

	signal.signal(signal.SIGINT, quit)

	path = os.path.dirname(os.path.realpath(__file__))

	log('\n' + strftime('%Y-%m-%d %H:%M:%S') + ' Server started')

	config = ConfigParser()

	try:
		config.read(path + '/server_config.ini')
		serverPort = int(config.get('Settings', 'port'))
	except:
		log('server_config.ini is either missing, unreadable or badly set-up')
		quit(0, 0)

	serverSocket = socket(AF_INET, SOCK_STREAM)	# Lascio qua o metto in acceptConnections?
	serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	serverSocket.settimeout(None)
	
	try:
		serverSocket.bind(('', serverPort))
	except:
		log('Port ' + str(serverPort) + ' already in use')
		quit(0, 0)

	serverSocket.listen(True)

	acceptThread = Thread(target=acceptConnetions, args=(serverSocket,))
	acceptThread.daemon = True
	acceptThread.start()
	
	root = Tk()
	app = Window(root)
	root.mainloop()
	quit(0, 0)


if __name__ == '__main__':
	main()