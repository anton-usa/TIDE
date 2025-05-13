from tkinter import *;
from tkinter import ttk;
import random;

class Shell:
	def __init__(self, root):
		self.root = root;
	
	def frame(self, parent):
		f = ttk.Frame(parent);
		f.rowconfigure(0, weight=1);
		f.columnconfigure(0, weight=1);
		
		Label(f, text="Shell "+str(random.random()), background="#00f").grid(row=0,column=0,sticky=(N, E, S, W));

		return f;
