from tkinter import Toplevel;

def createWindow(root, title=""):
	def quit(window):
		"""Close the about dialog"""
		window.grab_release();
		window.destroy();

	window = Toplevel(root);
	window.title(title);
	window.protocol("WM_DELETE_WINDOW", lambda: quit(window));
	window.transient(root);
	window.wait_visibility();
	window.grab_set();
	window.resizable(False, False);
	window.rowconfigure(0, weight=1);
	window.columnconfigure(0, weight=1);
	window.bind("<Control-w>", lambda e: quit(window));
	
	return window;
