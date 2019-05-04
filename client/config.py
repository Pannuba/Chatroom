import sys, os
from tkinter import Tk
from configparser import ConfigParser
from socket import *

global root, serverPort, serverName, clientSocket

root = Tk()
configFile = ConfigParser()
clientSocket = socket(AF_INET, SOCK_STREAM)

# Se il programma è lanciato da un'altra cartella non trova il file di configurazione
path = os.path.dirname(os.path.realpath(__file__))

try:
	configFile.read(path + '/client_config.ini')
	serverName = configFile.get('Settings', 'ip')
	serverPort = int(configFile.get('Settings', 'port'))
except:
	print('client_config.ini is either missing, unreadable or badly set-up')	# Popup o lascio in terminale? error.log?
	sys.exit()