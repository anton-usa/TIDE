from tkinter import *;
from tkinter import ttk;
from tkinter.font import Font;
import random;
from createWindow import createWindow;
from tkinter import messagebox;
import config;
import theme;

class TextEditor:
	def __init__(self, master=".", file=None):
		self.text = "";
		self.filename = file;
		self.saved = True;
		self.encoding = "utf-8";
		self.err = "strict";
		isGood = True;
		
		try:
			self._putText();
		except FileNotFoundError:
			isGood = False;
			messagebox.showerror(title="File not found", message=self.filename+" cannot be found");
		except UnicodeDecodeError:
			messagebox.showerror(title="Error decoding file", message=self.filename+" cannot be properly decoded. Unknown characters will be replaced");
			self._putText(err="replace");
		
		if isGood:
			self.window = Toplevel();
			self.name = "file-id-"+str(random.random()).replace(".", "");
			master = str(master) if str(master).endswith(".") else str(master) + ".";
			self.path = master+self.name;
			
			currentTheme = config.get("editor", "theme");
			px = self.window.tk.call("font", "measure", self._getFont(), "-displayof", self.window, " "*int(config.get("editor", "tab")));
			
			kargs = {
				"undo": True,
				"font": self._getFont(),
				"highlightthickness": 0,
				"borderwidth": 0,
				"padx": 5,
				"pady": 5,
				"wrap": "word" if config.get("view", "wrap") == "true" else "none",
				"tabstyle": "wordprocessor",
				"exportselection": True,
				"tabs": px,
			};
			
			self.textarea = Text(self.window, **kargs);
			self.textarea.insert("1.0", self.text);
			self.textarea.edit_reset();
			self.textarea.grid();
			self.savedText = hash(self.textarea.get("1.0", "end - 1 char"));
			self.textarea.peer_create(self.path, **kargs);
			self.textarea.bind("<<Modified>>", lambda e: self._modified());
			
			self.window.state("withdrawn");
	
	def close(self):
		self.window.destroy();
	
	def _modified(self):
		if self.savedText != hash(self.textarea.get("1.0", "end - 1 char")):
			self.saved = False;
	
	def _getFont(self):
		font = config.get("editor", "font");
		textFont = ();
		if font == "TkFixedFont":
			f = Font(name="TkFixedFont", exists=True);
			actual = Font.actual(f);
			font = actual["family"];
			config.set("editor", "font", actual["family"]);
			config.set("editor", "size", str(max(abs(actual["size"]), 11)));
			config.set("editor", "weight", actual["weight"]);

		return (font, config.get("editor", "size"), config.get("editor", "weight"));
	
	def _putText(self, num=0, err="strict"):
		if self.filename:
			encodings = ("utf_8", "utf_16", "utf_32", "utf_7", "utf_8_sig", "utf_16_be", "utf_16_le", "utf_32_be", "utf_32_le");
			
			self.encoding = encodings[num];
			self.err = err;
			if num == len(encodings):
				# all major encodings have been tried
				raise UnicodeDecodeError("", b"", 1, 0, "");
			
			try:
				with open(self.filename, encoding=encodings[num], errors=err) as f:
					self.text = f.read();
				
			except UnicodeDecodeError:
				self._putText(num+1, err);

if __name__ == "__main__":
	root = Tk();
	
	t = TextEditor(root);
	t.window.state("normal");
	
	root.mainloop();
