#!/usr/bin/env python3

'''TODO:	* BUG: trying to login twice as banned throws errors
			* Thread per inviare comandi dal server (o accettare connessioni, uno dei due)
			* Controllare i comandi inviati dai client (!ban, poi non saprei...)
			* Sistema di login con utente e password
			* Fare funzione per distinguere tra comando e risposta
			* Colori custom in file config
			* Inviare file, evidenziare link
'''

from socket import *
from threading import Thread
from time import strftime
from configparser import *
import signal, sys, os

helpmessage =	'\nSERVER: Welcome to SuperChat 9000! Here\'s a list of available commands:\n\
				\n!quit: you quit\n!help: shows this message\n\nHave fun, or something.\n'.encode('utf-8')


def quit(signum, frame):		# Eseguito quando viene premuto CTRL + C
	log('Quitting...')

	for i in socketList:
		i.send('!disconnect'.encode('utf-8'))
		i.close()
		
	sys.exit()


def log(logMessage):	# Mostra un messaggio nel terminale e lo aggiunge a chat.log
	print(logMessage)
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


def clientHandler(connectionSocket, user):		# Thread che legge i messaggi dei client

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
		socketList.remove(connectionSocket)		# distribuisco il messaggio a tutti si impalla
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
	global socketList, usersList, logfile, path
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

	while True:		# Invia comandi ai client, mandare solo a x?
		command = '!' + input()
		sendToAll(command)
		

if __name__ == '__main__':
	main()