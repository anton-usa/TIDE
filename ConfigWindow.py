from tkinter import *;
from tkinter import ttk;
from tkinter import colorchooser;
from tkinter import filedialog;
from tkinter import messagebox;
import config;
import theme;
import createWindow;
from tkinter import font;
import __main__;
import glob;
from directory import DIRECTORY;
try:
	import ttkthemes;
	EXISTS_TTK_THEMES = True;
except ImportError:
	EXISTS_TTK_THEMES = False

class ConfigWindow:
	def __init__(self, root):
		self.root = root;
		self.window = None;
	
	def open(self):
		self.window = createWindow.createWindow(self.root);
		self.window.title("TIDE Configuration");
		self.window.rowconfigure(0, weight=1);
		self.window.columnconfigure(0, weight=1);
		
		body = ttk.Frame(self.window, padding=5);
		body.grid(row=0,column=0,sticky=(N, E, S, W));
		body.rowconfigure(0, weight=1);
		body.columnconfigure(0, weight=1);
		
		self.notebook = ttk.Notebook(body,width=600,height=650);
		self.notebook.grid(row=0,column=0,sticky=(N, E, S, W));
		self.notebook.grid_propagate(False);
		
		self.generalTab = self.general();
		self.fontTab = self.font();
		self.editorTab = self.editor();
		self.systemTab = self.system();
		
		self.notebook.add(self.generalTab, text="General");
		self.notebook.add(self.fontTab, text="Font");
		self.notebook.add(self.editorTab, text="Editor Theme");
		self.notebook.add(self.systemTab, text="System Theme");
		
		footer = ttk.Frame(body, padding=(0, 10, 0, 0));
		footer.grid(row=1,column=0);
		
		close = ttk.Button(footer, text="Close", command=self.window.destroy);
		close.bind("<Return>", lambda e: close.invoke());
		close.grid(row=0,column=0);
		
		self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.setFontSelection(), True);

		self.window.wait_window();
	
	def general(self):
		def setTabs():
			config.set("editor", "tab", tabWidth.get());
		self.root.event_generate("<<UpdateTabWidth>>");
		
		def setNumbers():
			config.set("editor", "numbers", numbersValue.get());
			self.root.event_generate("<<ToggleLineNumbers>>");
		
		frame = ttk.Frame(self.notebook, padding=5);
		frame.columnconfigure(0, weight=1);
		
		# Tab width
		ttk.Label(frame, text="Tab Width: ").grid(row=0,column=0,stick=W);
		initTabValue = StringVar(value=config.get("editor", "tab"));
		tabWidth = Spinbox(frame, increment=1, from_=2, to=8, state="readonly", width=2, justify="center", command=setTabs, readonlybackground="#eeeeee", highlightthickness=0, borderwidth=1, textvariable=initTabValue);
		tabWidth.grid(row=0,column=1);
		
		ttk.Label(frame, text="Python Standard is 4").grid(row=0,column=2,sticky=W);
		
		# Tab spaces
		spaceValue = StringVar(value=config.get("editor", "spaces"));
		spaces = ttk.Checkbutton(frame, text="Use Spaces", onvalue="true", offvalue="false", variable=spaceValue, command=lambda: config.set("editor", "spaces", spaceValue.get()));
		spaces.grid(row=1,column=0,sticky=W);
		
		ttk.Separator(frame, orient=HORIZONTAL).grid(row=2,column=0,columnspan=3,sticky=(W, E),pady=10);
		
		# Autosave
		ttk.Label(frame, text="Save File Every: ").grid(row=3,column=0,stick=W);
		initSaveValue = StringVar(value=config.get("editor", "save"));
		save = Spinbox(frame, increment=0.1, from_=0.1, to=99.9, state="readonly", width=4, justify="center", command=lambda: config.set("editor", "save", save.get()), readonlybackground="#eeeeee", highlightthickness=0, borderwidth=1, textvariable=initSaveValue);
		save.grid(row=3,column=1,sticky=W);
		ttk.Label(frame, text="minute(s)").grid(row=3,column=2,sticky=W);

		# Backup copy
		backupValue = StringVar(value=config.get("editor", "backup"));
		backup = ttk.Checkbutton(frame, text="Save a backup copy", onvalue="true", offvalue="false", variable=backupValue, command=lambda: config.set("editor", "backup", backupValue.get()));
		backup.grid(row=4,column=0,sticky=W);

		ttk.Separator(frame, orient=HORIZONTAL).grid(row=5,column=0,columnspan=3,sticky=(W, E),pady=10);
		
		# Display line numbers
		numbersValue = StringVar(value=config.get("editor", "numbers"));
		numbers = ttk.Checkbutton(frame, text="Display Line Numbers", onvalue="true", offvalue="false", variable=numbersValue, command=setNumbers);
		numbers.grid(row=6,column=0,sticky=W);

		return frame;
	
	def font(self):
		def updateFont():
			view["font"] = (self._fontsList[int(self._families.curselection()[0])], initSizeValue.get(), initBoldValue.get());
			self.root.event_generate("<<UpdateFont>>");
			
		def setFont():
			if len(self._families.curselection()) > 0:
				f = self._fontsList[int(self._families.curselection()[0])];
				config.set("editor", "font", f);
				updateFont();
		
		def setSize():
			config.set("editor", "size", initSizeValue.get());
			updateFont();
		
		def setWeight():
			config.set("editor", "weight", initBoldValue.get());
			updateFont();
		
		def removeDuplicates(l):
			d = {};
			for i in l:
				d[i] = None;
			
			return tuple(sorted(tuple(d)));
		
		frame = ttk.Frame(self.notebook, padding=5);
		frame.rowconfigure(0, weight=1);
		frame.columnconfigure(0, weight=1);
		frame.columnconfigure(1, weight=1);
		
		configFrame = ttk.Frame(frame,padding=(0, 0, 10, 0));
		configFrame.grid(row=0,column=0,sticky=(N, S, W, E));
		configFrame.rowconfigure(0, weight=1);
		configFrame.columnconfigure(0, weight=1);
		
		self._fontsList = removeDuplicates(font.families());
		fonts = StringVar(value=self._fontsList);
		self._families = Listbox(configFrame, highlightthickness=0, borderwidth=0, relief="flat", listvariable=fonts);
		self.setFontSelection();
		self._families.see(self._families.curselection());
		self._families.grid(row=0,column=0,sticky=(N, S, W, E));
		self._families.bind("<<ListboxSelect>>", lambda e: setFont());
		
		scroll = ttk.Scrollbar(configFrame, orient=VERTICAL, command=self._families.yview);
		self._families["yscrollcommand"] = scroll.set;
		scroll.grid(row=0,column=1,sticky=(N, S));
		
		extras = ttk.Frame(configFrame, padding=(5, 5, 5, 0));
		extras.columnconfigure(2, weight=1);
		extras.grid(row=1,column=0,columnspan=2,sticky=(W, E));
		
		ttk.Label(extras, text="Size: ").grid(row=0,column=0);
		
		initSizeValue = StringVar(value=config.get("editor", "size"));
		size = Spinbox(extras, increment=1, from_=1, to=99, state="readonly", width=3, justify="center", readonlybackground="#eeeeee", highlightthickness=0, borderwidth=1, textvariable=initSizeValue, command=setSize);
		size.grid(row=0,column=1);
		
		initBoldValue = StringVar(value=config.get("editor", "weight"));
		bold = ttk.Checkbutton(extras, text="Bold", variable=initBoldValue, offvalue="normal", onvalue="bold", command=setWeight);
		bold.grid(row=0,column=2,sticky=E);
		
		resultFrame = ttk.Frame(frame);
		resultFrame.grid(row=0,column=1,sticky=(N, E, S, W));
		resultFrame.rowconfigure(0, weight=1);
		resultFrame.columnconfigure(0, weight=1);
		
		view = Text(resultFrame, font=(config.get("editor", "font"), config.get("editor", "size"), config.get("editor", "weight")), relief="flat", wrap="none", width=10, height=1);
		view.insert("1.0", "AaBbCcDdEeFfGgHhIiJj\nKkLlMmNnOoPpQqRrSsTt\nUuVvWwXxYyZz\n0123456789\n~!@#$%^&*()`_+-=[]\\\n{}|;':\",./<>?");
		view["state"] = "disabled";

		view.grid(row=0,column=0,sticky=(N, E, S, W));
		
		sy = ttk.Scrollbar(resultFrame, orient=VERTICAL, command=view.yview);
		sy.grid(row=0,column=1,sticky=(N, S));
		
		sx = ttk.Scrollbar(resultFrame, orient=HORIZONTAL, command=view.xview);
		sx.grid(row=1,column=0,sticky=(W, E));
		
		view["yscrollcommand"] = sy.set;
		view["xscrollcommand"] = sx.set;
		
		return frame;
	
	def editor(self):
		def addEvents():
			lineNumbers.bind("<1>", lambda e: changeStyleFor("linenumbers"));
			
			editorTags = ("comment", "bool", "keyword", "builtin", "string", "func", "number", "exception", "stdout", "stderr", "error", "found", "text", "selected");
			for tag in editorTags:
				editor.tag_bind(tag, "<1>", lambda e, t=tag: changeStyleFor(t));
			
			tabsTags = ("tabbar", "tabactive", "tabactive-text", "tabnormal", "tabnormal-text");
			for tag in tabsTags:
				tabsCanvas.tag_bind(tag, "<1>", lambda e, t=tag: changeStyleFor(t));
				
		
		def changeStyleFor(tag):
			selected.set(tag);
			translate = {
				"comment": "Comment",
				"bool": "Booleans",
				"keyword": "Keywords",
				"builtin": "Builtin Functions",
				"string": "Strings",
				"func": "Function Definitions",
				"number": "Numbers",
				"exception": "Exception Errors",
				"stdout": "Standard Output",
				"stderr": "Standard Error",
				"error": "Python Error",
				"found": "Search Phrase Found",
				"text": "Plain Text",
				"selected": "Selected Text",
				"linenumbers": "Side Bar",
				"tabbar": "Tab Bar",
				"tabactive": "Active Tab",
				"tabactive-text": "Active Tab Text",
				"tabnormal": "Normal Tab",
				"tabnormal-text": "Normal Tab Text"
			};
			currentTheme = config.get("editor", "theme");
			selectedLabel["text"] = translate[tag];
			
			if "tab" not in tag:
				backcolor, forecolor, fontweight = theme.get(currentTheme, tag).split(" ");
				for t, c in ((background, backcolor), (foreground, forecolor)):
					t["state"] = "normal";
					t["text"] = c;
					t["background"] = c;
					t["foreground"] = getOppositeLightness(c);
					t["activebackground"] = c;
					t["activeforeground"] = getOppositeLightness(c);

				if tag == "text" or tag == "linenumbers" or tag == "selected":
					weight.set(config.get("editor", "weight"));
					normal["state"] = "disabled";
					italic["state"] = "disabled";
					bold["state"] = "disabled";
				else:
					normal["state"] = "normal";
					italic["state"] = "normal";
					bold["state"] = "normal";
					weight.set(fontweight);
			else:
				color = theme.get(currentTheme, tag);
				background["state"] = "disabled";
				foreground["state"] = "disabled";
				background["background"] = "#eeeeee";
				foreground["background"] = "#eeeeee";
				background["text"] = "------";
				foreground["text"] = "------";
				weight.set("normal");
				normal["state"] = "disabled";
				italic["state"] = "disabled";
				bold["state"] = "disabled";
				styleAvailable = None;
				
				if tag in ("tabbar", "tabactive", "tabnormal"):
					styleAvailable = background;
				else:
					styleAvailable = foreground;
				
				styleAvailable["state"] = "normal";
				styleAvailable["text"] = color;
				styleAvailable["background"] = color;
				styleAvailable["foreground"] = getOppositeLightness(color);
				styleAvailable["activebackground"] = color;
				styleAvailable["activeforeground"] = getOppositeLightness(color);
				
		
		def getOppositeLightness(color):
			red = eval("0x"+color[1:3])/255;
			green = eval("0x"+color[3:5])/255;
			blue = eval("0x"+color[5:])/255;
			lightness = (min(red, green, blue) + max(red, green, blue))/2;
			
			return "#000000" if lightness >= 0.45 else "#ffffff";
		
		def updateStyles():
			try:
				normal = (config.get("editor", "font"), config.get("editor", "size"), "normal");
				italic = (config.get("editor", "font"), config.get("editor", "size"), "italic");
				bold = (config.get("editor", "font"), config.get("editor", "size"), "bold");
				currentTheme = config.get("editor", "theme");
				tags = ("comment", "bool", "keyword", "builtin", "string", "func", "number", "exception", "stdout", "stderr", "error", "found", "text", "selected", "linenumbers");
			
				for tag in tags:
					back, fore, font = theme.get(currentTheme, tag).split(" ");
					font = italic if font == "italic" else bold if font == "bold" else normal if font == "normal" else None;

					if tag == "text":
						f = (config.get("editor", "font"), config.get("editor", "size"), config.get("editor", "weight"));
						editor.configure(background=back, foreground=fore, font=f);
					elif tag == "selected":
						editor.configure(selectbackground=back, selectforeground=fore, insertbackground=fore);
					elif tag == "linenumbers":
						f = (config.get("editor", "font"), config.get("editor", "size"), config.get("editor", "weight"));
						lineNumbers.configure(background=back, foreground=fore, font=f);
					else:
						editor.tag_configure(tag, background=back, foreground=fore, font=font);
				
			
				editor.tag_configure("selected", background=editor["selectbackground"], foreground=editor["selectforeground"]);
				editor.tag_raise("sel");
			
				tabsCanvas.itemconfigure("tabbar", fill=theme.get(currentTheme, "tabbar"));
				tabsCanvas.itemconfigure("tabactive", fill=theme.get(currentTheme, "tabactive"));
				tabsCanvas.itemconfigure("tabactive-text", fill=theme.get(currentTheme, "tabactive-text"));
				tabsCanvas.itemconfigure("tabnormal", fill=theme.get(currentTheme, "tabnormal"));
				tabsCanvas.itemconfigure("tabnormal-text", fill=theme.get(currentTheme, "tabnormal-text"));
			except: # I don't know where an exception is being thrown. I don't see any visible effects
				pass;
		
		def changeColor(colorType):
			currentTheme = config.get("editor", "theme");
			n = 1 if colorType == foreground else 0;
			if "tab" not in selected.get():
				styles = theme.get(currentTheme, selected.get()).split(" ");
			else:
				styles = [None]*3;
				styles[n] = theme.get(currentTheme, selected.get());

			color = colorchooser.askcolor(styles[n], parent=self.window, title="Pick Text Color" if colorType == foreground else "Pick Background Color");
			if color[1] != None:
				styles[n] = color[1];
				styleStr = styles[n] if "tab" in selected.get() else " ".join(map(str, styles));
				theme.set(currentTheme, selected.get(), styleStr);
				colorType["text"] = color[1];
				colorType["background"] = color[1];
				colorType["foreground"] = getOppositeLightness(color[1]);
				colorType["activebackground"] = color[1];
				colorType["activeforeground"] = getOppositeLightness(color[1]);
				updateStyles();
			
			self.root.event_generate("<<UpdateTheme>>");
		
		def changeFont():
			currentTheme = config.get("editor", "theme");
			styles = theme.get(currentTheme, selected.get()).split(" ");
			styles[2] = weight.get();
			theme.set(currentTheme, selected.get(), " ".join(styles));
			updateStyles();
			self.root.event_generate("<<UpdateTheme>>");
		
		def changeTheme():
			themesSelect.selection_clear();
			config.set("editor", "theme", themesSelect.get());
			updateStyles();
			self.root.event_generate("<<UpdateTheme>>");
			changeStyleFor("text");
		
		def newTheme(themesTuple, themesSelect, path=DIRECTORY+"/config/default-theme.ini"):
			def createTheme(themesTuple, themesSelect, path):
				def r():
					try: error.grid_remove();
					except: pass;
				
				if name.get() in theme.get():
					error.grid();
					self.root.after(5000, r);
				else:
					with open(DIRECTORY+"/config/themes.ini", "a") as f:
						defaultThemeSettings = open(path);
						f.write("\n["+name.get()+"]\n"+defaultThemeSettings.read());
						defaultThemeSettings.close();
						
					themesTuple.append(name.get());
					themesSelect.configure(values=tuple(themesTuple));
					themesSelect.current(len(themesTuple)-1);
					themesSelect.event_generate("<<ComboboxSelected>>");
					nameWindow.destroy();
			
			nameWindow = createWindow.createWindow(self.window);
			nameWindow.title("Theme Name");
			
			body = ttk.Frame(nameWindow, padding=5);
			body.grid(row=0,column=0);
			
			ttk.Label(body, text="Type in your theme name:").grid(row=0,column=0,pady=5,sticky=W);
			
			error = ttk.Label(body, text="Theme name taken", foreground="#ff0000");
			error.grid(row=1,column=0,sticky=W);
			error.grid_remove();
			
			name = ttk.Entry(body);
			name.focus_set();
			name.bind("<Return>", lambda e: ok.invoke());
			name.grid(row=2,column=0,sticky=(W, E));
			
			btnGroup = ttk.Frame(body, padding=(0, 10, 0, 0));
			btnGroup.grid(row=3,column=0);
			
			ok = ttk.Button(btnGroup, text="Ok", command=lambda: createTheme(themesTuple, themesSelect, path));
			ok.bind("<Return>", lambda e: ok.invoke());
			ok.grid(row=0,column=0,padx=5);
			
			cancel = ttk.Button(btnGroup, text="Cancel", command=nameWindow.destroy);
			cancel.bind("<Return>", lambda e: cancel.invoke());
			cancel.grid(row=0,column=1,padx=5);
			
			nameWindow.wait_window();
		
		def installTheme():
			path = filedialog.askopenfilename(parent=self.window, filetypes=[("Config Files", "*.ini")]);
			if path:
				newTheme(themesTuple, themesSelect, path);
		
		def removeTheme():
			if len(themesTuple) > 1:
				currentTheme = config.get("editor", "theme");
			
				if messagebox.askyesno(title="Remove Theme", message="Are you sure you want to remove the theme \""+currentTheme+"\"?", icon="warning", parent=self.window):
					theme.delete(currentTheme);
					themesTuple.remove(currentTheme);
					themesSelect.configure(values=tuple(themesTuple));
					themesSelect.current(0);
					themesSelect.event_generate("<<ComboboxSelected>>");
					
			else:
				messagebox.showerror(title="Unable to remove", message="You're not allowed to remove your only theme", parent=self.window);
		
		def yview(*args):
			editor.yview(*args);
			lineNumbers.yview(*args);
			
		def sySet(*args):
			sy.set(*args);
			yview(MOVETO, args[0]);
		
		frame = ttk.Frame(self.notebook, padding=5);
		frame.columnconfigure(0, weight=1);
		frame.rowconfigure(2, weight=1);
		
		# THEME SELECTING
		themesTuple = list(theme.get())[1:];
		themesSelect = ttk.Combobox(frame, values=tuple(themesTuple), state="readonly", font="TkDefaultFont 11");
		themesSelect.current(themesTuple.index(config.get("editor", "theme")));
		themesSelect.bind("<<ComboboxSelected>>", lambda e: changeTheme());
		themesSelect.grid(row=0,column=0,sticky=(W, E));
		
		# THEME EDITING
		themeEditFrame = ttk.Frame(frame);
		themeEditFrame.grid(row=1,column=0,sticky=(E, W));
		themeEditFrame.columnconfigure(0, weight=1);
		
		selected = StringVar();
		selectedLabel = ttk.Label(themeEditFrame, text="Side Bar", font="TkDefaultFont 10 bold", anchor="center");
		selectedLabel.grid(row=0,column=0,sticky=(W, E),columnspan=2);
		
		ttk.Label(themeEditFrame, text="Color:").grid(row=1,column=0,sticky=W);
		foreground = Button(themeEditFrame, relief="flat", borderwidth=0, highlightthickness=0, command=lambda: changeColor(foreground));
		foreground.bind("<Return>", lambda e: foreground.invoke());
		foreground.grid(row=1, column=1, sticky=(W, E), pady=5);
		
		ttk.Label(themeEditFrame, text="Background:").grid(row=2,column=0,sticky=W);
		background = Button(themeEditFrame, relief="flat", borderwidth=0, highlightthickness=0, command=lambda: changeColor(background));
		background.bind("<Return>", lambda e: background.invoke());
		background.grid(row=2, column=1, sticky=(W, E), pady=5);
		
		
		weightFrame = ttk.Frame(themeEditFrame, padding=(0, 5));
		weightFrame.grid(row=3,column=0,columnspan=2,sticky=(W, E));
		weightFrame.columnconfigure(0, weight=1);
		weightFrame.columnconfigure(1, weight=1);
		weightFrame.columnconfigure(2, weight=1);
		weight = StringVar(value="normal");
		
		normal = ttk.Radiobutton(weightFrame, text="Normal", variable=weight, value="normal", command=changeFont);
		normal.grid(row=0,column=0);
		
		bold = ttk.Radiobutton(weightFrame, text="Bold", variable=weight, value="bold", command=changeFont);
		bold.grid(row=0,column=1);
		
		italic = ttk.Radiobutton(weightFrame, text="Italic", variable=weight, value="italic", command=changeFont);
		italic.grid(row=0,column=2);
		
		# EDITOR FRAME
		editorFrame = ttk.Frame(frame, padding=(0, 0, 0, 5));
		editorFrame.grid(row=2, column=0, sticky=(N, E, S, W));
		editorFrame.columnconfigure(1, weight=1);
		editorFrame.rowconfigure(2, weight=1);
		
		# Tabs
		tabsCanvas = Canvas(editorFrame, highlightthickness=0, borderwidth=0, relief="flat", height=30, width=301, cursor=__main__.CURSOR_POINTER);
		tabsCanvas.grid(row=0,column=0,columnspan=3,sticky=(W, E));
		
		tabsCanvas.create_rectangle(0, 0, 10000, 30, tags=("tabbar"), width=0);
		tabsCanvas.create_rectangle(0, 0, 150, 30, tags=("tabactive"), outline="#bbbbbb");
		tabsCanvas.create_rectangle(150, 0, 300, 30, tags=("tabnormal"), outline="#bbbbbb");
		tabsCanvas.create_text(75, 15, text="Active Tab", tags=("tabactive-text"));
		tabsCanvas.create_text(225, 15, text="Normal Tab", tags=("tabnormal-text"));
		tabsCanvas.create_text(145, 15, anchor="e", text="×", fill="#aaaaaa");
		tabsCanvas.create_text(295, 15, anchor="e", text="×", fill="#aaaaaa");

		ttk.Separator(editorFrame, orient=HORIZONTAL).grid(row=1,column=0,columnspan=2,sticky=(W, E));
		
		# Line numbers
		lineNumbers = Text(editorFrame, width=3, highlightthickness=0, borderwidth=0, font=(config.get("editor", "font"), config.get("editor", "size"), config.get("editor", "weight")), padx=2, pady=2, cursor=__main__.CURSOR_POINTER, relief="flat");
		lineNumbers.insert("1.0", "\n".join(map(str, range(1, 14))), "numbers");
		lineNumbers.tag_configure("numbers", justify="right");
		lineNumbers.grid(row=2,column=0,sticky=(N, S));
		lineNumbers["state"] = "disabled";
		
		# Editor
		editor = Text(editorFrame, background="#ffffff", highlightthickness=0, borderwidth=0, foreground="#000000", font=(config.get("editor", "font"), config.get("editor", "size"), config.get("editor", "weight")), padx=2, pady=2, wrap="word", cursor=__main__.CURSOR_POINTER, relief="flat");
		tab = " " * int(config.get("editor", "tab"));
		editor.grid(row=2,column=1,sticky=(N, E, W, S));
		
		px = editor.tk.call("font", "measure", editor["font"], "-displayof", editor.master, tab);
		editor.configure(tabs=px);

		editor.insert("insert", "# Click to change theme\n", "comment");
		editor.insert("insert", "def", "keyword");
		editor.insert("insert", " ", "text");
		editor.insert("insert", "main", "func");
		editor.insert("insert", "():\n\t", "text");
		editor.insert("insert", "boolean = ", "text");
		editor.insert("insert", "True", "bool");
		editor.insert("insert", "\n\t", "text");
		editor.insert("insert", "string = ", "text");
		editor.insert("insert", "\"Hello World\"", "string");
		editor.insert("insert", "\n\t", "text");
		editor.insert("insert", "num = ", "text");
		editor.insert("insert", "1.0", "number");
		editor.insert("insert", "\n\t", "text");
		editor.insert("insert", "print", "builtin");
		editor.insert("insert", "(string)\n\n", "text");
		editor.insert("insert", "try", "keyword");
		editor.insert("insert", ":\n\tmain()\n", "text");
		editor.insert("insert", "except", "keyword");
		editor.insert("insert", " ", "text");
		editor.insert("insert", "KeyboardInterrupt", "exception");
		editor.insert("insert", ":\n\t", "text");
		editor.insert("insert", "pass", "keyword");
		editor.insert("insert", "\n\n", "text");
		editor.insert("insert", "found", "found");
		editor.insert("insert", " ", "text");
		editor.insert("insert", "selected", "selected");
		editor["state"] = "disabled";
		updateStyles();
		addEvents();
		changeStyleFor("text");
		
		sy = ttk.Scrollbar(editorFrame, orient=VERTICAL, command=yview);
		sy.grid(row=2,column=2,sticky=(N, S));
		editor["yscrollcommand"] = sySet;
		lineNumbers["yscrollcommand"] = sySet;
		
		# THEME BUTTONS
		btnsFrame = ttk.Frame(frame);
		btnsFrame.grid(row=3,column=0);
		
		newBtn = ttk.Button(btnsFrame, text="New", command=lambda: newTheme(themesTuple, themesSelect));
		newBtn.bind("<Return>", lambda e: newBtn.invoke());
		newBtn.grid(row=0,column=0);
		
		installBtn = ttk.Button(btnsFrame, text="Install", command=installTheme);
		installBtn.bind("<Return>", lambda e: installBtn.invoke());
		installBtn.grid(row=0,column=1,padx=5);

		removeBtn = ttk.Button(btnsFrame, text="Remove", command=removeTheme);
		removeBtn.bind("<Return>", lambda e: removeBtn.invoke());
		removeBtn.grid(row=0,column=2);
		
		self.root.bind("<<UpdateFont>>", lambda e: updateStyles(), True);
		
		return frame;
	
	def system(self):
		def selectTheme():
			themeSelect.selection_clear();
			theme = allThemes[themeSelect.current()];
			config.set("window", "theme", theme);
			ttk.Style().theme_use(theme);
			allCustomThemes = glob.glob(DIRECTORY+"/themes/*");
			
		frame = ttk.Frame(self.notebook, padding=5);
		frame.columnconfigure(0, weight=1);
		
		allThemes = sorted(ttk.Style().theme_names());
		if EXISTS_TTK_THEMES:
			t = [t for t in ttkthemes.THEMES if t not in allThemes];
			allThemes = sorted(allThemes + t);
		
		themeSelect = ttk.Combobox(frame, values=allThemes, font="TkDefaultFont 11", state="readonly");
		themeSelect.set(ttk.Style().theme_use());
		themeSelect.bind("<<ComboboxSelected>>", lambda e: selectTheme());
		themeSelect.grid(row=0,column=0,sticky=(W, E));
		
		selectTheme();
		
		return frame;
	
	def setFontSelection(self):
		idx = self._fontsList.index(config.get("editor", "font"));
		self._families.activate(idx);
		self._families.selection_set(idx);
