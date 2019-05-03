#!/usr/bin/env python3

import signal
from loginwindow import LoginWindow	# Implica tutti i moduli che vengono importati esplicitamente in loginwindow
from config import root, clientSocket, sys

def quit(signum, frame):		# Eseguito quando viene premuto CTRL + C
	print('Quitting...')
	try:					# Solo qui il ; per concatenare metodi sullo stesso oggetto funziona...
		clientSocket.send('!quit'.encode('utf-8')); shutdown(); close()
	except:
		pass		# Per quando non si è ancora connesso al server
	sys.exit()


def main():

	signal.signal(signal.SIGINT, quit)

	app = LoginWindow(root)
	root.mainloop()
	
	quit(0, 0)		  # 0, 0 perché non so cosa fanno signum e frame


if __name__ == '__main__':
	main()