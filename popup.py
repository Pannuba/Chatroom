from tkinter import *

class Popup:
	def __init__(self, master, title, message):
		self.master = master
		self.master.geometry('320x80')
		self.master.resizable(False, False)
		self.master.title(title)
		self.master.focus()
		self.master.protocol("WM_DELETE_WINDOW", self.master.destroy)
		self.popupMessage = Label(self.master, text=message, pady=10)#, width=20, height=20)
		self.popupMessage.pack(side=TOP, fill=BOTH)		# Forse fill non va
		self.popupButton = Button(self.master, text='OK', command=self.master.destroy)
		self.popupButton.pack(side=BOTTOM, pady=10)
	
def buildPopup(master, title, message):
	newWindow = Toplevel(master)
	app = Popup(newWindow, title, message)