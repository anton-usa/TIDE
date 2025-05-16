"""This is where the whole program is started :)"""
from tkinter import *;
from tkinter import ttk;
from Window import *;
from Plugins import *;
import os;
import sys;
from directory import HOME_PATH;

__version__ = "0.1.1";
CURSOR_POINTER = "pointinghand" if sys.platform == "darwin" else "hand2";

def main():
	# create the TIDE config directory
	if not os.path.isdir(HOME_PATH+"/.tide"):
		os.mkdir(HOME_PATH+"/.tide");
		f = open(HOME_PATH+"/.tide/recent.txt", "w");
		f.close();
	
	# start the program window
	window = Window();
	if len(sys.argv) > 1:
		window.editor.openFile(sys.argv[1:]);
	else:
		window.editor.newFile();
	
	plugins = Plugins(window);
	plugins.start();
	
	window.root.mainloop();

def restart(root):
	root.destroy();
	main();
	

# run the program
if __name__ == "__main__":
	try: main();
	except: pass;