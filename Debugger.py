from tkinter import *;
from tkinter import ttk;
import random;

class Debugger:
	def __init__(self, root):
		self.root = root;
	
	def frame(self, parent):
		f = ttk.Frame(parent);
		f.rowconfigure(0, weight=1);
		f.columnconfigure(0, weight=1);
		
		Label(f, text="Debugger "+str(random.random()), background="#f00").grid(row=0,column=0,sticky=(N, E, S, W));

		return f;
