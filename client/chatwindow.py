from tkinter import Text, Entry, Scrollbar
from threading import Thread
from config import username, clientSocket, socket
from quitwindow import *
from popup import *

class ChatWindow:

	def __init__(self, master):
		self.master = master
		self.index = -1
		self.buffer = []
		self.master.protocol("WM_DELETE_WINDOW", self.master.quit)		# E non destroy (era self.master.quit)
		self.master.geometry('640x480')
		self.master.minsize(width=160, height=120)
		self.master.title('SuperChat 9000 - logged in as ' + username)
		self.textbox = Entry(self.master)
		self.textbox.bind('<Return>', self.getMessage)
		self.textbox.bind('<Up>', self.scrollBufferUp)
		self.textbox.bind('<Down>', self.scrollBufferDown)
		self.textbox.pack(side='bottom', fill='x')
		self.chat = Text(self.master, state='disabled')	# Non ho bisogno di width e height perché ho expand in pack
		self.bar = Scrollbar(self.master, width=16, command=self.chat.yview)		# Scrollbar, chat window
		self.chat.bind('<1>', lambda event: self.chat.focus_set())	# Permette di copiare il testo, nonostante sia DISABLED
		self.chat.config(yscrollcommand=self.bar.set)
		self.bar.pack(side='right', fill='y')
		self.chat.pack(expand=True, side='left', fill='both')
		listenThread = Thread(target=self.listen)			# arriva il messaggio di login la chat non è ancora stata creata e dà errore
		listenThread.daemon = True		# Per far chiudere il programma con sys.exit(), altrimenti si blocca
		listenThread.start()

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
		self.textbox.delete(0, 'end')	# Svuota la barra di input
		
		if len(message) > 512:	# Dovrei controllare dopo encoding, ma forse non cambia
			print('Message is too long (< 512 chars)')

		elif message == '!quit':		# Potrei aggiungere risposte ad altri comandi
			buildQuitWindow(self.master)

		elif message != '':
			clientSocket.send(message.encode('utf-8'))
			self.index = -1		# Controllare che il messaggio inviato non è già stato mandato
			self.buffer.insert(0, message)
		
	def listen(self):
		while True:

			response = clientSocket.recv(512).decode('utf-8')	# Fare funzione per distinguere tra comando e risposta
			
			if response == 'GOODBYE':		# Fare una funzione per controllare la risposta?
				buildPopup(self.master, 'Disconnected', 'The server has shut down')
				buildQuitWindow(self.master)
				break

			self.chat.config(state='normal')
			self.chat.insert('end', response + '\n')
			self.chat.see('end')
			self.chat.config(state='disabled') # Chiudere, tornare al login? è possibile eseguire una funzione quando termina un thread?