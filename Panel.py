from tkinter import *;
from tkinter import ttk;

class Panel:
	def __init__(self, root, body):
		self.root = root;
		self.body = body;
		
		self.frame = self._createFrame();
	
	def _createFrame(self):
		f = ttk.Frame(self.body);
		f.columnconfigure(0, weight=1);
		f.rowconfigure(0, weight=1);
		
		self.notebook = ttk.Notebook(f);
		self.notebook.grid(row=0,column=0,sticky=(N, E, S, W));
		
		return f;
	
	def add(self, widget, *args, **kwargs):
		self.notebook.add(widget, *args, **kwargs);
	
	def forget(self, widget, *args, **kwargs):
		self.notebook.forget(widget, *args, **kwargs);