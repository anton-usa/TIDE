"""
This is where all of the main components of the program are assemble together.
These components are:
	MenuBar
	Editor

Some event bindings are placed here mostly because its more logical to place, they are:
	Quit - quites the main program
	Full - fullscreen the main program
"""
from tkinter import *;
from tkinter import ttk;
from MenuBar import *;
from Debugger import *;
from Editor import *;
from Shell import *;
from Panel import *;
import config;
import sys;
from directory import DIRECTORY;
from tkinter import messagebox;
import __main__;
try:
	from ttkthemes import ThemedTk;
	EXISTS_TTK_THEMES = True;
except ImportError:
	EXISTS_TTK_THEMES = False

class Window:
	def __init__(self):
		# create the window
		if sys.platform == "win32":
			import ctypes;
			ctypes.windll.shcore.SetProcessDpiAwareness(2);

		if EXISTS_TTK_THEMES:
			self.root = ThemedTk();
		else:
			self.root = Tk();		

		self.root.protocol("WM_DELETE_WINDOW", self.quit);
		width = config.get("window", "width");
		height = config.get("window", "height");
		self.root.geometry(width+"x"+height+"+0+0");
		try:
			if sys.platform == "win32":
				self.root.iconbitmap(default=f"{DIRECTORY}/icons/logo.ico");
			else:
				logo = PhotoImage(file=f"{DIRECTORY}/icons/logo.gif");
				self.root.tk.call("wm", "iconphoto", self.root._w, logo);
		except:
			pass;
		self.root.title("TIDE v"+__main__.__version__);
		self.root.rowconfigure(0, weight=1);
		self.root.columnconfigure(0, weight=1);
		
		# system theme
		ttkStyle = ttk.Style();
		if config.get("window", "theme") == "-":
			config.set("window", "theme", "vista" if sys.platform == "win32" else "aqua" if sys.platform == "darwin" else "clam");

		ttkStyle.theme_use(config.get("window", "theme"));
		
		# breaking my own rules a bit, but I'm changing some 
		# style configs because I need to make the background white
		ttkStyle.configure("White.TCheckbutton", background="#ffffff");

		# add the menu bar, MUST BE LAST
		self.menu = MenuBar(self.root);
		self.root["menu"] = self.menu.menubar;
		
		# add the main components into paned windows
		self.body = ttk.PanedWindow(self.root, orient=HORIZONTAL);
		self.body.rowconfigure(0, weight=1);
		self.body.columnconfigure(0, weight=1);
		self.body.grid(row=0,column=0,sticky=(N, E, S, W));
		
		# side pane
		self.sidepanel = Panel(self.root, self.body);
		
		
		# bottom pane
#		self.bottompanel = Panel(self.root, self.body);
		
		# the editor
		self.editor = Editor(self.root, self.body);
		self.body.add(self.editor.frame);
		
		# focus on the editor upon start up
		self.editor.textarea.mark_set("insert", "1.0");
		
		# some global event bindings
		self.root.event_add("<<Quit>>", "<Control-q>");
		self.root.event_add("<<Full>>", "<KeyPress-F11>");
		self.root.event_add("<<Side>>", "<KeyPress-F10>");
#		self.root.event_add("<<Bottom>>", "<KeyPress-F9>");
		self.root.bind("<<Quit>>", self.quit);
		self.root.bind("<<Full>>", self.toggleFull);
		self.root.bind("<<Side>>", self.toggleSide);
#		self.root.bind("<<Bottom>>", self.toggleBottom);
		self.root.bind("<Configure>", lambda e: self.windowConfig(), True);
		self.root.bind("<<UpdateWrapMenu>>", lambda e: self.updateWrapMenu());
		
		# automatic calling
		if config.get("view", "fullscreen") == "true":
			self.root.attributes("-fullscreen", 1);
		
		if config.get("view", "side") == "true":
			self.body.insert(0, self.sidepanel.frame);
		
	def toggleFull(self, e=None):
		"""Make the program fullscreen and unfullscreen"""
		isFull = config.get("view", "fullscreen") == "true";
		self.root.attributes("-fullscreen", int(not isFull));
		
		fullscreen = str(not isFull).lower();
		config.set("view", "fullscreen", fullscreen);
		self.menu.displayFull.set(fullscreen);
	
#	def toggleBottom(self, e=None):
#		"""Make the bottom panel show/unshow"""
#		isShowing = config.get("view", "bottom") == "true";
#		
#		show = str(not isShowing).lower();
#		config.set("view", "bottom", show);
#		self.menu.showBottomPanel.set(show);
	
	def toggleSide(self, e=None):
		"""Make the side panel show/unshow"""
		isShowing = config.get("view", "side") == "true";
		if isShowing:
			self.body.forget(self.sidepanel.frame);
		else:
			self.body.insert(0, self.sidepanel.frame);
		
		show = str(not isShowing).lower();
		config.set("view", "side", show);
		self.menu.showSidePanel.set(show);
	
	def updateWrapMenu(self):
		self.menu.wrapWords.set(config.get("view", "wrap"));
	
	def windowConfig(self):
		"""Updates the window section in config.ini"""
		config.set("window", "width", str(self.root.winfo_width()));
		config.set("window", "height", str(self.root.winfo_height()));
		
	def quit(self, e=None):
		"""Closes the program safely"""
		files = self.editor.files;
		close = True;
		for file in files:
			if not file.saved:
				close = messagebox.askyesno("Unsaved Files!", "There are unsaved files! Are you sure you want to quit?", icon="warning");
				break;
		
		if close:
			try: self.root.destroy();
			except: pass;
