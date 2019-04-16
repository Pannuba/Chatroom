#!/usr/bin/env python3

'''TODO:	* Thread per inviare comandi dal server (o accettare connessioni, uno dei due)
			* Controllare i comandi inviati dai client (!ban, poi non saprei...)
			* File di configurazione con la lista degli admin, IP/porta, MOTD, passsword?...
			* Sistema di login con utente e password
			* Mostrare i contenuti nella chat in una finestra
'''

from socket import *
from threading import Thread
from time import strftime
import signal

def sigint_handler(signum, frame):		# Eseguito quando viene premuto CTRL + C
	log('\nQuitting...')
	logfile.close()
	for i in socketList:
		i.send('__#@*^GOODBYE^*@#__'.encode('utf-8'))
		i.close()
	quit()

def log(logMessage):	# Mostra un messaggio nel terminale e lo aggiunge a chat.log
	print(logMessage)
	logfile.write(logMessage + '\n')

def sendToAll(message):
	for i in socketList:
		i.send(message.encode('utf-8'))

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

	serverPort = 12000
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	serverSocket.bind(('', serverPort))
	serverSocket.listen(1)
	global socketList
	socketList = []

	global logfile
	logfile = open('chat.log', 'w')
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

if __name__ == '__main__':
	main()