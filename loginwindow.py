from config import serverName, serverPort, sys
from chatwindow import *	# Comunque non importa socket perché è importato con una wildcard, credo

class LoginWindow:	# Non ho ben capito il ruolo di root e master, e le loro relazioni

	def __init__(self, master):
		self.master = master		# master = "LoginWindow"
		self.master.geometry('300x120')
		self.master.resizable(False, False)
		self.master.title('SuperChat 9000 - login')
		self.master.protocol("WM_DELETE_WINDOW", sys.exit)
		self.userLabel = Label(self.master, text='Username:')
		self.userLabel.pack()
		self.userField = Entry(self.master)
		self.userField.bind('<Return>', self.login)
		self.userField.pack(side='top')
		self.pwLabel = Label(self.master, text='Password:')
		self.pwLabel.pack()
		self.pwField = Entry(self.master, show='*')
		self.pwField.pack()
		self.button = Button(text='Login', command=self.login)	# Faccio userField globale?
		self.button.pack(side='bottom')
		
	def login(self):
		global username, password	# Non so perché qua metto userField e in getMessage self, ma funziona
		username = self.userField.get()
		password = self.pwField.get()	# Svolge tutto il login in questa funzione
		self.userField.delete(0, 'end')

		if self.checkUsername(username) == False:
			self.master.quit()		# Con destroy non funziona
			self.master.mainloop()
			return
		
		try:
			
			clientSocket.connect((serverName, serverPort))	# Connessione al server
			clientSocket.send(username.encode('utf-8'))		# Dentro o fuori dal try?
		except Exception as e:
			print(e)
			buildPopup(self.master, "Cannot connect to server", e)
		
		status = clientSocket.recv(16).decode('utf-8')

		if status == 'BANNED':							# Manca ADMIN, OK
			buildPopup(self.master, 'Banned', 'This user has been banned.')
			clientSocket.shutdown(SHUT_RDWR)
			clientSocket.close()
			return
			
		elif status == 'DUPLICATE':
			buildPopup(self.master, 'Login failed', 'This user is already connected to the server')
			return
			
		self.master.withdraw()
		self.newWindow = Toplevel(self.master)	# Toplevel è simile a Tk()
		self.app = ChatWindow(self.newWindow)

	def checkUsername(self, username):
		boolean = False

		if username == '':
			buildPopup(self.master, 'Login failed', 'Username field cannot be empty')

		elif len(username) > 16:
			buildPopup(self.master, 'Login failed', 'Username can\'t be longer than 16 characters')

		elif username.strip() != username:
			buildPopup(self.master, 'Login failed', 'Username cannot start or end with spaces')
		
		else:
			boolean = True

		return boolean