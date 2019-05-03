import sys
from tkinter import Tk
from configparser import ConfigParser

global root, serverPort, serverName

root = Tk()

configFile = ConfigParser()

try:
	configFile.read('client_config.ini')
	serverName = configFile.get('Settings', 'ip')
	serverPort = int(configFile.get('Settings', 'port'))
except:
	print('client_config.ini is either missing, unreadable or badly set-up')	# Popup o lascio in terminale? error.log?
	sys.exit()