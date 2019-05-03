import sys
from tkinter import Tk
from configparser import ConfigParser
from socket import *

global root, serverPort, serverName, username, clientSocket

root = Tk()

username = ''

configFile = ConfigParser()

clientSocket = socket(AF_INET, SOCK_STREAM)

try:
	configFile.read('client_config.ini')
	serverName = configFile.get('Settings', 'ip')
	serverPort = int(configFile.get('Settings', 'port'))
except:
	print('client_config.ini is either missing, unreadable or badly set-up')	# Popup o lascio in terminale? error.log?
	sys.exit()