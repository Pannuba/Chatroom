from tkinter import *
import config

class QuitWindow:
	def __init__(self, master):
		self.master = master
		self.master.geometry('400x100')
		self.master.resizable(False, False)
		self.master.title('Are you sure you want to quit?')
		self.master.focus()
		self.yesButton = Button(self.master, text='Yes', command=config.root.destroy)	# root.destroy va ma deve essere globale. Usare quit con *args?
		self.yesButton.pack(side=LEFT)
		self.noButton = Button(self.master, text='No', command=self.master.destroy)
		self.noButton.pack(side=RIGHT)

def buildQuitWindow(master):
	newWindow = Toplevel(master)
	app = QuitWindow(newWindow)