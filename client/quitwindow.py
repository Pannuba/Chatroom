from tkinter import Button, Toplevel
from config import root

class QuitWindow:
	def __init__(self, master):
		self.master = master
		self.master.geometry('300x100')
		self.master.resizable(False, False)
		self.master.title('Are you sure you want to quit?')
		self.master.focus()
		self.yesButton = Button(self.master, text='Yes', command=root.destroy)
		self.yesButton.pack(side='left')
		self.noButton = Button(self.master, text='No', command=self.master.destroy)
		self.noButton.pack(side='right')

def buildQuitWindow(master):
	newWindow = Toplevel(master)
	app = QuitWindow(newWindow)