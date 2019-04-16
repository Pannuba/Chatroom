#!/usr/bin/env python3

'''TODO:	* Thread per inviare comandi dal server (o accettare connessioni, uno dei due)
			* Controllare i comandi inviati dai client (!ban, poi non saprei...)
			* Sistema di login con utente e password
			* Mostrare i contenuti nella chat in una finestra, input di username (e poi password) in una GUI
'''

from socket import *
from threading import Thread
from time import strftime
from configparser import *
import signal

def sigint_handler(signum, frame):		# Eseguito quando viene premuto CTRL + C
	log('Quitting...')
	logfile.close()
	for i in socketList:
		i.send('GOODBYE'.encode('utf-8'))
		i.close()
	quit()

def log(logMessage):	# Mostra un messaggio nel terminale e lo aggiunge a chat.log
	print(logMessage)
	logfile.write(logMessage + '\n')

def sendToAll(message):
	for i in socketList:
		i.send(message.encode('utf-8'))

def checkUser(user, socket):		# Apro e chiudo ogni volta o li lascio sempre aperti? try/except se non esistono?
	admins = open('admins.txt', 'r')
	banned = open('banned.txt', 'r')

	if user in admins.read():
		log(user + ' is an admin')
		return 'admin'
	
	if user in banned.read():
		log(user + ' is banned')
		socket.send('BANNED'.encode('utf-8'))
		return 'banned'

def handler(connectionSocket, user):

		while True:
			message = connectionSocket.recv(512)	# Attende la ricezione di un messaggio
			message = message.decode('utf-8')	# Funzione checkmessage?

			if message == '!quit':		# Controllare per altri comandi (funzione?)
				break

			response = user + ": " + message
			log(strftime('%Y-%m-%d %H:%M:%S') + ' Message from ' + response)
			sendToAll(response)
		
		log(user + ' has left the server')		# Si termina il thread per un client connesso
		sendToAll(user + ' has left the server')
		connectionSocket.close()				# Se non rimuovo il client disconnesso dall'array, quando
		socketList.remove(connectionSocket)		# distribuisco il messaggio a tutti si impalla

def main():
	signal.signal(signal.SIGINT, sigint_handler)

	config = ConfigParser()
	config.read('config.ini')
	serverPort = int(config.get('Settings', 'port'))

	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	serverSocket.bind(('', serverPort))
	serverSocket.listen(1)
	global socketList
	socketList = []

	global logfile
	logfile = open('chat.log', 'a')
	log('\n' + strftime('%Y-%m-%d %H:%M:%S') + ' Server booted')

	while True:
		newSocket, clientAddress = serverSocket.accept()		# l'esecuzione torna all'inizio del while e si mette in "pausa" a serversocket.accept()
		
		user = newSocket.recv(64)
		user = user.decode('utf-8')
		
		if checkUser(user, newSocket) == 'banned':		# Trovare un modo più efficiente senza ripetere. While? Bool?
			newSocket, clientAddress = serverSocket.accept()
			user = newSocket.recv(64)
			user = user.decode('utf-8')

		socketList.append(newSocket)
		log('{} has joined the server as {}'.format(clientAddress, user))	# Devo usare format() perché clientAddress è una tuple e lo manda in palla boh
		
		thread = Thread(target=handler, args=(newSocket, user))
		thread.daemon = True		# Sennò quit() si blocca
		thread.start()

if __name__ == '__main__':
	main()