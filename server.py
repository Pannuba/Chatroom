#!/usr/bin/env python3

from socket import *
from threading import Thread
from time import strftime
import signal

def sigint_handler(signum, frame):
	log('\nQuitting...')
	logfile.close()
	for i in socketList:
		i.send('__#@*^GOODBYE^*@#__'.encode('utf-8'))
		i.close()
	quit()

def log(logMessage):	# Mostra un messaggio nel terminale e lo aggiunge a chat.log
	print(logMessage)
	logfile.write(logMessage + '\n')

def handler(connectionSocket, user):

		while True:
			message = connectionSocket.recv(512)	# Attende la ricezione di un messaggio
			message = message.decode('utf-8')	# Funzione checkmessage?

			if message == '!quit':
				break

			response = user + ": " + message
			log(strftime('%Y-%m-%d %H:%M:%S') + ' Message from ' + response)

			for i in socketList:
				i.send(response.encode('utf-8'))
		
		log(user + ' has left the server')		# Si termina il thread per un client connesso
		
		connectionSocket.close()				# Se non rimuovo il client disconnesso dall'array, quando
		socketList.remove(connectionSocket)		# distribuisco il messaggio a tutti si impalla

# Questo blocco viene eseguito solo all'avvio

signal.signal(signal.SIGINT, sigint_handler)

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
socketList = []

logfile = open('chat.log', 'a')
log(strftime('%Y-%m-%d %H:%M:%S') + ' Server booted')

while True:
	newSocket, clientAddress = serverSocket.accept()		# l'esecuzione torna all'inizio del while e si mette in "pausa" a serversocket.accept()
	socketList.append(newSocket)
	
	user = newSocket.recv(64)
	user = user.decode('utf-8')
	log('{} has joined the server as {}'.format(clientAddress, user))	# Devo usare format() perché clientAddress è una tuple e lo manda in palla boh
	
	thread = Thread(target=handler, args=(newSocket, user))
	thread.daemon = True		# Sennò quit() si blocca
	thread.start()