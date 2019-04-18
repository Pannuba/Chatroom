#!/usr/bin/env python3

'''TODO:	* Thread per inviare comandi dal server (o accettare connessioni, uno dei due)
			* Controllare utente e password, ripetere controllo se non vanno bene
			* Controllare i comandi inviati dai client (!ban, poi non saprei...)
			* Sistema di login con utente e password
			* Fare funzione per distinguere tra comando e risposta
			* Convertire l'username in lowercase per il login
			* Fare una lista con tutti gli utenti per evitare doppi login
			* Cronologia dei messaggi mandati, accessibile con la freccia su
			* Colori custom in file config
			* GUI per server
'''

from socket import *
from threading import Thread
from time import strftime
from configparser import *
import signal
import sys

helpmessage =	'\nSERVER: Welcome to SuperChat 9000! Here\'s a list of available commands:\n\
				\n!quit: you quit\n!help: shows this message\n\nHave fun, or something.'.encode('utf-8')

def quit(signum, frame):		# Eseguito quando viene premuto CTRL + C
	log('Quitting...')
	logfile.close()
	for i in socketList:
		i.send('GOODBYE'.encode('utf-8'))
		i.close()
	sys.exit()

def log(logMessage):	# Mostra un messaggio nel terminale e lo aggiunge a chat.log
	print(logMessage)
	logfile.write(logMessage + '\n')

def sendToAll(message):
	for i in socketList:
		i.send(message.encode('utf-8'))

def checkUser(user, socket, ip):		# Apro e chiudo ogni volta o li lascio sempre aperti? try/except se non esistono?
	
	for i in usersList:
		if user.lower() == i:
			log(strftime('%Y-%m-%d %H:%M:%S') + ' ' + user + ' (' + ip + ') has attempted to join the server, but is already logged in')
			socket.send('DUPLICATE'.encode('utf-8'))
			return 'duplicate'

	try:
		admins = open('admins.txt', 'r')
		banned = open('banned.txt', 'r')
	except:
		log('admins.txt or banned.txt not found')
		quit(0, 0)

	for i in admins:
		if user == i.rstrip('\n'):		# I file devono terminare con una linea vuota
			log(user + ' is an admin')
			admins.close()
			banned.close()
			return 'admin'
	
	for i in banned:
		if user == i.rstrip('\n'):		# Senza rstrip conta gli \n come linee indipendenti
			log(strftime('%Y-%m-%d %H:%M:%S') + ' ' + user + ' (' + ip + ') has attempted to join the server, but is banned')
			socket.send('BANNED'.encode('utf-8'))
			admins.close()
			banned.close()
			return 'banned'

def handler(connectionSocket, user):

		while True:
			message = connectionSocket.recv(512)	# Attende la ricezione di un messaggio
			message = message.decode('utf-8')	# Funzione checkmessage?

			if message == '!quit':		# Controllare per altri comandi (fare funzione). Posso fare che se il primo 
				break					# carattere è un ! controlla il comando, se non lo trova consiglia di fare !help
			
			if message == '!help':
				connectionSocket.send(helpmessage)
			
			else:
				response = user + ": " + message
				log(strftime('%Y-%m-%d %H:%M:%S') + ' Message from ' + response)
				sendToAll(response)
		
		connectionSocket.close()				# Se non rimuovo il client disconnesso dall'array, quando
		socketList.remove(connectionSocket)		# distribuisco il messaggio a tutti si impalla
		usersList.remove(user.lower())
		log(strftime('%Y-%m-%d %H:%M:%S') + ' ' + user + ' has left the server')		# Si termina il thread per un client connesso
		sendToAll(user + ' has left the server')

def main():
	global socketList, usersList, logfile
	socketList = []
	usersList = []

	signal.signal(signal.SIGINT, quit)

	logfile = open('chat.log', 'a')
	log('\n' + strftime('%Y-%m-%d %H:%M:%S') + ' Server started')

	config = ConfigParser()

	try:
		config.read('server_config.ini')
		serverPort = int(config.get('Settings', 'port'))
	except:
		log('server_config.ini not found')
		quit(0, 0)

	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

	try:
		serverSocket.bind(('', serverPort))
	except:
		log('Port ' + str(serverPort) + ' already in use')
		quit(0, 0)

	serverSocket.listen(True)

	while True:
		newSocket, (ip, port) = serverSocket.accept()		# l'esecuzione torna all'inizio del while e si mette in "pausa" a serversocket.accept()
		user = newSocket.recv(16)							# Modificato clientAddress in ip, port per ottenere l'IP in una variabile
		user = user.decode('utf-8')

		while (checkUser(user, newSocket, ip) == 'duplicate') or (checkUser(user, newSocket, ip) == 'banned'):		# Trovare un modo più efficiente senza ripetere. While? Bool?
			newSocket, clientAddress = serverSocket.accept()
			user = newSocket.recv(16)
			user = user.decode('utf-8')

		socketList.append(newSocket)
		usersList.append(user.lower())
		log(ip + ' has joined the server as ' + user)	# Dovevo usare format() perché clientAddress è una tuple e lo manda in palla
		sendToAll(user + ' has joined the server')
		thread = Thread(target=handler, args=(newSocket, user))
		thread.daemon = True		# Sennò quit() si blocca
		thread.start()

if __name__ == '__main__':
	main()