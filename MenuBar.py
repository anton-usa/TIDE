"""
This is where the menu bar for the program is created and assembled.
The menu contains these items:
	File
		New File (ctrl+n)
		Open File (ctrl+o)
		Open Module (ctrl+m)
		Recent Files >
			last 10 files
		--------------------
		Save (ctrl+s)
		Save As (ctrl+shift+s)
		--------------------
		Close (ctrl+w)
		Quit (ctrl+q)
	Edit
		Undo (ctrl+z)
		Redo (ctrl+shift+z)
		--------------------
		Select All (ctrl+a)
		Cut (ctrl+x)
		Copy (ctrl+c)
		Paste (ctrl+v)
		Delete (del)
		--------------------
		Go to Line (ctrl+l)
		Find (ctrl+f)
		Replace (ctrl+h)
		--------------------
		Toggle Comment Code (ctrl+3)
		Indent Region (tab)
		Outdent Region (shift+tab)
	View
		Full Screen (f11)
		--------------------
		Text Wrapping (f8)
		--------------------
		Configuration
	Documents
		Next Tab (ctrl+pgdn)
		Previous Tab (ctrl+pgup)
		First Tab (ctrl+home)
		Last Tab (ctrl+end)
		--------------------
		list of all open documents
	Plugins
		All Plugins
		Install Plugin
		Run Plugin >
			all plugins that need to be run through the menu (plugin key shortcut)
	Help
		About
		Help (f1)
		--------------------
		Python Tutorial
		Python Docs (f2)
		--------------------
		Tkinter Tutorial
		Tkinter Docs (f3)
	
This class does create some event bindings, they are:
	PyTut - opens the python tutorial
	PyDocs - open the python docs
	TkTut - opens the tkinter tutorial
	TkDocs - opens the tkinter docs
	[module]EDToggle - toggles enable/disable for a plugin in the menu
	[entry] Enable - enables menu entry [entry]
	[entry] Disable - disabled menu entry [entry]

Some events are bound in different classes, they are:
	Quit - found in Window.py
	About - found in About.py
	Full - found in Window.py
	SelectAll - found in Editor.py
	[module]Main - found in Plugins.py
"""
from tkinter import *;
from tkinter import ttk;
from tkinter import font;
import os;
import glob;
import json;
import webbrowser;
import sys;
import __main__;
import parse_markdown;
import config;
import re;
from directory import DIRECTORY, HOME_PATH;
from createWindow import createWindow;
from ConfigWindow import ConfigWindow;

README = DIRECTORY+"/README.md";
CREDITS = DIRECTORY+"/CREDITS";
LICENSE = DIRECTORY+"/LICENSE";

def getPluginManifests(plugins):
	info = [];
	for pluginPath in plugins:
		if not os.path.isfile(pluginPath+"/manifest.json"): continue;
		with open(pluginPath+"/manifest.json", "r", encoding="utf_8") as f:
			manifest = json.loads(f.read().strip());
			info.append([pluginPath, manifest]);
	
	return info;

class MenuBar:
	def __init__(self, root):
		# create the menu bar
		self.root = root;
		self.menubar = Menu(self.root);
		self.menubar.bind("<1>", lambda e: self.root.focus_set());
		self.root.option_add("*tearOff", False);
		
		# the file menu
		self.fileMenu = self.file();
		self.menubar.add_cascade(menu=self.fileMenu, label="File", underline=0);
		
		# the edit menu
		self.editMenu = self.edit();
		self.menubar.add_cascade(menu=self.editMenu, label="Edit", underline=0);
		
		# the view menu
		self.showSidePanel = StringVar();
		self.showBottomPanel = StringVar();
		self.displayFull = StringVar();
		self.wrapWords = StringVar();
		self.viewMenu = self.view();
		self.configWindow = ConfigWindow(self.root);
		self.menubar.add_cascade(menu=self.viewMenu, label="View", underline=0);
		
		# the documents menu
		self.documentsMenu = self.documents();
		self.menubar.add_cascade(menu=self.documentsMenu, label="Documents", underline=0);
		
		# the plugins menu
		self.pluginsMenu = self.plugins();
		self.menubar.add_cascade(menu=self.pluginsMenu, label="Plugins", underline=0);
		
		# the help menu
		self.helpMenu = self.help();
		self.menubar.add_cascade(menu=self.helpMenu, label="Help", underline=0);
		
	def file(self):
		"""This creates the file menu and all of its options"""

		def addRecent(menu, recent):
			"""Adds all of the files listed in .tide/recent.txt"""
			
			# make sure .tide/recent.txt exists before opening
			if os.path.isfile(HOME_PATH+"/.tide/recent.txt"):
				with open(HOME_PATH+"/.tide/recent.txt", "r", encoding="utf_8") as f:
					# list the file paths
					content = f.read().strip();
					if content != "":
						menu.entryconfigure("Recent Files", state=ACTIVE);
						paths = content.split("\n");
						for path, i in zip(paths, range(len(paths))):
							recent.add_command(label=str(i)+" "+path, command=lambda n=i: self.root.event_generate("<<OpenRecent"+str(n)+">>"), underline=0);
		
		def updateRecent(menu, recent):
			recent.delete(0, 9);
			addRecent(menu, recent);
		
		# create the menu and add all the items
		menu = Menu(self.menubar);
		menu.add_command(label="New File", command=lambda: self.root.event_generate("<<NewFile>>"), accelerator="Ctrl+N", underline=0);
		menu.add_command(label="Open File", command=lambda: self.root.event_generate("<<OpenFile>>"), accelerator="Ctrl+O", underline=0);
		menu.add_command(label="Open Module", command=lambda: self.root.event_generate("<<OpenModule>>"), accelerator="Ctrl+M", underline=5);

		recent = Menu(menu);
		menu.add_cascade(menu=recent, label="Recent Files", underline=0);
		addRecent(menu, recent);
		
		menu.add_separator();
		
		menu.add_command(label="Save", command=lambda: self.root.event_generate("<<Save>>"), accelerator="Ctrl+S", underline=0, state=DISABLED);
		menu.add_command(label="Save As", command=lambda: self.root.event_generate("<<SaveAs>>"), accelerator="Ctrl+Shift+S", underline=5, state=DISABLED);
		
		menu.add_separator();
		
		menu.add_command(label="Close", command=lambda: self.root.event_generate("<<Close>>"), accelerator="Ctrl+W", underline=0, state=DISABLED);
		menu.add_command(label="Quit", command=lambda: self.root.event_generate("<<Quit>>"), accelerator="Ctrl+Q", underline=0);
		for i in range(13):
			if menu.type(i) != SEPARATOR:
				name = menu.entrycget(i, "label");
				self.root.bind("<<"+name+" Enable>>", lambda e, n=name: menu.entryconfigure(n, state=NORMAL));
				self.root.bind("<<"+name+" Disable>>", lambda e, n=name: menu.entryconfigure(n, state=DISABLED));
		
		self.root.bind("<<UpdateRecent>>", lambda e: updateRecent(menu, recent));
		
		return menu;
	
	def edit(self):
		"""This creates the edit menu and all of its options"""
		
		# create the menu and add all the items
		menu = Menu(self.menubar);
		menu.add_command(label="Undo", command=lambda: self.root.event_generate("<<Undo>>"), accelerator="Ctrl+Z", underline=0, state=DISABLED);
		menu.add_command(label="Redo", command=lambda: self.root.event_generate("<<Redo>>"), accelerator="Ctrl+Shift+Z", underline=0, state=DISABLED);
		
		menu.add_separator();
		
		menu.add_command(label="Select All", command=lambda: self.root.event_generate("<<SelectAll>>"), accelerator="Ctrl+A", underline=7, state=DISABLED);
		menu.add_command(label="Cut", command=lambda: self.root.event_generate("<<CutText>>"), accelerator="Ctrl+X", underline=0, state=DISABLED);
		menu.add_command(label="Copy", command=lambda: self.root.event_generate("<<CopyText>>"), accelerator="Ctrl+C", underline=1, state=DISABLED);
		menu.add_command(label="Paste", command=lambda: self.root.event_generate("<<PasteText>>"), accelerator="Ctrl+V", underline=0, state=DISABLED);
		menu.add_command(label="Delete", command=lambda: self.root.event_generate("<<DeleteText>>"), accelerator="Del", underline=0, state=DISABLED);
		
		menu.add_separator();
		
		menu.add_command(label="Go to Line", command=lambda: self.root.event_generate("<<GoToLine>>"), accelerator="Ctrl+L", underline=6, state=DISABLED);
		menu.add_command(label="Find", command=lambda: self.root.event_generate("<<Find>>"), accelerator="Ctrl+F", underline=0, state=DISABLED);
		menu.add_command(label="Replace", command=lambda: self.root.event_generate("<<Replace>>"), accelerator="Ctrl+H", underline=1, state=DISABLED);
		
		menu.add_separator();
		
		menu.add_command(label="Comment Code", command=lambda: self.root.event_generate("<<Comment>>"), accelerator="Ctrl+3", underline=3, state=DISABLED);
		menu.add_command(label="Uncomment Code", command=lambda: self.root.event_generate("<<Uncomment>>"), accelerator="Ctrl+Shift+3", underline=7, state=DISABLED);
		menu.add_command(label="Indent Region", command=lambda: self.root.event_generate("<<Indent>>"), accelerator="Tab", underline=0, state=DISABLED);
		menu.add_command(label="Outdent Region", command=lambda: self.root.event_generate("<<Outdent>>"), accelerator="Shift+Tab", underline=0, state=DISABLED);
		
		for i in range(18):
			if menu.type(i) != SEPARATOR:
				name = menu.entrycget(i, "label");
				self.root.bind("<<"+name+" Enable>>", lambda e, n=name: menu.entryconfigure(n, state=NORMAL));
				self.root.bind("<<"+name+" Disable>>", lambda e, n=name: menu.entryconfigure(n, state=DISABLED));

		return menu;
	
	def view(self):
		"""This creates the view menu and all of its options"""
		
		# configurations
		viewConfig = [
			config.get("view", "side"),
			config.get("view", "bottom"),
			config.get("view", "fullscreen"),
			config.get("view", "wrap")
		];

		# create the menu and add all the items
		menu = Menu(self.menubar);
		
		self.displayFull.set(viewConfig[2]);
		menu.add_checkbutton(label="Full Screen", command=lambda: self.root.event_generate("<<Full>>"), accelerator="F11", underline=0, onvalue="true", offvalue="false", variable=self.displayFull);

		self.wrapWords.set(viewConfig[3]);
		menu.add_checkbutton(label="Text Wrapping", command=lambda: self.root.event_generate("<<Wrap>>"), accelerator="F8", underline=0, onvalue="true", offvalue="false", variable=self.wrapWords);
		
		menu.add_separator();
		
		menu.add_command(label="Configuration", command=lambda: self.configWindow.open(), underline=0);
		
		return menu;
	
	def documents(self):
		"""Creates the documents menu"""
		menu = Menu(self.menubar);
		
		menu.add_command(label="Previous File", command=lambda: self.root.event_generate("<<PreviousTab>>"), accelerator="Ctrl+PgUp", underline=0);
		menu.add_command(label="Next File", command=lambda: self.root.event_generate("<<NextTab>>"), accelerator="Ctrl+PgDn", underline=0);
		menu.add_command(label="First File", command=lambda: self.root.event_generate("<<FirstTab>>"), accelerator="Ctrl+Home", underline=0);
		menu.add_command(label="Last File", command=lambda: self.root.event_generate("<<LastTab>>"), accelerator="Ctrl+End", underline=0);
		
		return menu;
	
	def plugins(self):
		"""This creates the plugins menu and all of its options"""
		
		def runMenu(run):
			i = 0;
			for pluginPath, manifest in getPluginManifests(sorted(glob.glob(DIRECTORY+"/plugins/*"))):
				if manifest["menu"]:
					module = os.path.basename(pluginPath);
					shortcut = manifest["shortcut"] if "shortcut" in manifest else "";
					state = DISABLED if manifest["disabled"] else NORMAL;
					self.root.bind("<<"+module+"EDToggle>>", lambda e, n=i: run.entryconfigure(n, state=(DISABLED if run.entrycget(n, "state") == NORMAL else NORMAL)));
					run.add_command(label=manifest["name"], command=lambda: self.root.event_generate("<<"+module+"Main>>"), accelerator=shortcut, state=state);
					i += 1;
		
		# create the menu and add all the items
		menu = Menu(self.menubar);
		run = Menu(menu);
		
		menu.add_command(label="All Plugins", command=lambda: self.root.event_generate("<<AllPlugins>>"), underline=0);
		menu.add_command(label="Install Plugin", command=lambda: self.root.event_generate("<<InstallPlugin>>"), underline=0);
		menu.add_cascade(menu=run, label="Run Plugin", underline=0);
		runMenu(run);
		
		return menu;
	
	def help(self):
		"""This creates the help menu and all of its options, along with some key bindings"""
		
		# URL constants
		v = sys.version_info;
		PY_TUTORIAL = "docs.python.org/"+str(v.major)+"."+str(v.minor)+"/tutorial";
		PY_DOCS = "docs.python.org/"+str(v.major)+"."+str(v.minor);
		TK_TUTORIAL = "http://tkdocs.com/tutorial/index.html";
		TK_DOCS = "http://tkdocs.com/pyref/index.html";
		
		# create the menu and add all the items
		menu = Menu(self.menubar, name="help");
		
		menu.add_command(label="About", command=lambda: self.root.event_generate("<<About>>"), underline=0);
		menu.add_command(label="Help", command=lambda: self.root.event_generate("<<Help>>"), accelerator="F1", underline=0);
		
		menu.add_separator();
		
		menu.add_command(label="Python Tutorial", command=lambda: self.root.event_generate("<<PyTut>>"), underline=0);
		menu.add_command(label="Python Docs", command=lambda: self.root.event_generate("<<PyDocs>>"), accelerator="F2", underline=1);
		
		menu.add_separator();
		
		menu.add_command(label="Tkinter Tutorial", command=lambda: self.root.event_generate("<<TkTut>>"), underline=0);
		menu.add_command(label="Tkinter Docs", command=lambda: self.root.event_generate("<<TkDocs>>"), accelerator="F3", underline=1);
		
		# event bindings
		self.root.bind("<<About>>", lambda e: self.aboutDialog());
		self.root.bind("<<Help>>", lambda e: self.helpDialog());
		self.root.bind("<KeyPress-F1>", lambda e: self.root.event_generate("<<Help>>"));
		
		self.root.bind("<<PyTut>>", lambda e: webbrowser.open(PY_TUTORIAL));
		self.root.bind("<<PyDocs>>", lambda e: webbrowser.open(PY_DOCS));
		self.root.bind("<KeyPress-F2>", lambda e: self.root.event_generate("<<PyDocs>>"));
		
		self.root.bind("<<TkTut>>", lambda e: webbrowser.open(TK_TUTORIAL));
		self.root.bind("<<TkDocs>>", lambda e: webbrowser.open(TK_DOCS));
		self.root.bind("<KeyPress-F3>", lambda e: self.root.event_generate("<<TkDocs>>"));
		
		return menu;
	
	def aboutDialog(self):
		"""Display the about dialog"""
		
		def showFile(showing, file, button, useparse_markdown):
			"""Put's [file] into the textarea extra info"""
			
			# release both buttons
			credits.state(["!pressed"]);
			license.state(["!pressed"]);
			
			if textareaShowing.get() != showing:
				# display the textarea and the file
				with open(file, "r", encoding="utf_8") as f:
					textarea["state"] = NORMAL;
					textarea.delete("0.0", "end");
					if useparse_markdown:
						parse_markdown.tkText(textarea, f.read());
					else:
						textarea.insert("0.0", f.read());
	
					textarea["state"] = DISABLED;
					textareaFrame.grid();
					button.state(["pressed"]);
					textareaShowing.set(showing);
			else:
				# remove the textarea
				textareaShowing.set("");
				textareaFrame.grid_remove();
		
		# set up the window
		window = createWindow(self.root, "About TIDE");
		
		# set up the body frame
		body = ttk.Frame(window, padding=5);
		body.rowconfigure(0, weight=1);
		body.columnconfigure(0, weight=1);
		body.grid(row=0,column=0);
		
		# the summary info frame
		infoFrame = ttk.Frame(body);
		infoFrame.grid(row=0,column=0);
		
		# logo
		img = PhotoImage(file=DIRECTORY+"/icons/logo.gif");
		ttk.Label(infoFrame, image=img).grid(row=0,column=0,rowspan=5,sticky=E);

		# summary info
		ttk.Label(infoFrame, text="TIDE", font=("courier", 24, "bold")).grid(row=0,column=1,sticky=W);
		ttk.Label(infoFrame, text="Tkinter Integrated Development Environment", font="TkDefaultFont").grid(row=1,column=1,sticky=W);

		vinfo = sys.version_info;
		pyversion = "%d.%d.%d %s" % (vinfo.major, vinfo.minor, vinfo.micro, vinfo.releaselevel);
		ttk.Label(infoFrame, text="Version "+__main__.__version__, font="TkDefaultFont").grid(row=2,column=1,sticky=W);
		ttk.Label(infoFrame, text="Using Python v"+pyversion+" (with Tk v"+str(TkVersion)+")", font="TkDefaultFont").grid(row=3,column=1,sticky=W);
		
		link = "http://github.com/anton-usa/TIDE";
		linkLabel = ttk.Label(infoFrame, text=link, foreground="#00aaff", font="TkDefaultFont 10 underline", cursor=__main__.CURSOR_POINTER);
		linkLabel.grid(row=4,column=1,sticky=W,pady=10);
		linkLabel.bind("<1>", lambda e: webbrowser.open(link));
		
		ttk.Label(infoFrame, text="Copyright © 2024 Anton Shapovalov", font="TkDefaultFont 7").grid(row=5,column=1,sticky=W);
		
		# textarea extra info
		textareaFrame = ttk.Frame(body, padding=(0, 5, 0, 0));
		textareaFrame.grid(column=0,row=1,sticky=(W, E));
		textareaFrame.grid_remove();
		
		textareaShowing = StringVar(value="");
		textarea = Text(textareaFrame, width=60, height=15, font="TkFixedFont 11", highlightbackground="#888888", highlightthickness=1, relief=FLAT, state=DISABLED, wrap="word");
		textarea.grid(column=0,row=0);
		
		scrollbar = ttk.Scrollbar(textareaFrame, orient=VERTICAL, command=textarea.yview);
		textarea.configure(yscrollcommand=scrollbar.set);
		scrollbar.grid(column=1,row=0,sticky=(N, S));
		
		# footer buttons
		buttonGroup = ttk.Frame(body, padding=(0, 20, 0, 0));
		buttonGroup.grid(column=0,row=2,sticky=(W, E));
		buttonGroup.columnconfigure(0, weight=1);
		
		leftGroup = ttk.Frame(buttonGroup);
		leftGroup.grid(column=0,row=0,sticky=W);
		
		credits = ttk.Button(leftGroup, text="Credits", command=lambda: showFile("credits", CREDITS, credits, True));
		credits.bind("<Return>", lambda e: credits.invoke());
		credits.grid(column=0,row=0,padx=5);
		
		license = ttk.Button(leftGroup, text="License", command=lambda: showFile("license", LICENSE, license, False));
		license.bind("<Return>", lambda e: license.invoke());
		license.grid(column=1,row=0,padx=5);
		
		close = ttk.Button(buttonGroup, text="Close", command=lambda: window.destroy(), takefocus=True);
		close.bind("<Return>", lambda e: close.invoke());
		close.grid(column=2,row=0,padx=5);

		# make window the only active window in the program
		window.wait_window();
	
	def helpDialog(self):
		"""Display the help browser"""
		
		def getReadme():
			"""Finds all README.md files for plugins and TIDE and returns info about them"""
			helpList = ["TIDE Help"]
			helpMap = {"TIDE Help": README};
			
			for pluginPath, manifest in getPluginManifests(sorted(glob.glob(DIRECTORY+"/plugins/*"))):
				helpList.append(manifest["name"]);
				helpMap[manifest["name"]] = pluginPath + "/README.md";
			
			return helpList, helpMap;
		
		def showReadme():
			"""Get the README.md file and display it"""
			def longest(l):
				w = 0;
				s = "";
				for i in l:
					if len(i) > w:
						w = len(i);
						s = i;
				
				return s;
			
			# more visually appealing
			helpBox.selection_clear();
			
			contents.column("#0", width=200);
			with open(helpMap[helpSelect.get()], "r", encoding="utf_8") as f:
				# put the styled parse_markdown text
				parse_markdownTxt = f.read();
				textarea["state"] = "normal";
				textarea.delete("0.0", "end");
				while len(headingLines) > 0: headingLines.pop();
				headingLines.append(parse_markdown.tkText(textarea, parse_markdownTxt));
				textarea["state"] = "disabled";
				
				# put the table of contents
				children = contents.get_children();
				if len(children) > 0:
					contents.delete(children);

				table = createTableOfContents(parse_markdownTxt);
				putIn = [];
				insertIntoTree(contents, [""], 0, table, putIn);
				f = font.Font(name="TkDefaultFont", exists=True);
				l = longest(putIn);
				w = f.measure(l.strip("\t"));
				mw = w+(len(l) - len(l.strip("\t")) + 1)*20 + 5;
				contents.column("#0", minwidth=mw if mw > 200 else 200);
		
		def createTableOfContents(txt):
			"""Create the table of contents array"""
			def createSection(parsed, n, lvl):
				"""Creates the children for each chapter"""
				chapter = [];
				i = n;
				while i < len(parsed):
					section = parsed[i];
					tag = section[0];
					name = section[1].strip();
					
					if tag == "h"+str(lvl):
						# append same header levels
						chapter.append(name);
						i += 1;
					else:
						groups = re.match("h([1-6])", tag);
						if groups:
							nextLvl = int(groups.group(1));
							
							if nextLvl > lvl:
								# create arrays for lower headers
								subChapter, i = createSection(parsed, i, nextLvl);
								chapter.append(subChapter);
							else:
								# don't create arrays for higher headers
								break;
						else:
							i += 1;
					
				
				return chapter, i;
			
			parsed = parse_markdown.parse(txt);
			table, _ = createSection(parsed, 0, 1);
			
			return table;
		
		def insertIntoTree(tree, ids, level, table, putIn):
			"""Inserts into the tree table of contents"""
			for heading in table:
				if type(heading) == str:
					# insert the chapter
					id = tree.insert(ids[level], "end", text=heading, open=True, tag=len(putIn));
					f = font.Font(self.root, name="TkDefaultFont", exists=True);
					width = f.measure(heading);
					putIn.append("\t"*level+heading);
					ids = ids[:level+1];
					if level < len(ids):
						ids.append(id);
					else:
						ids[level+1] = id;
					
				else:
					# a child chapter
					insertIntoTree(tree, ids, level+1, heading, putIn);
		
		def scrollTo(n):
			headingNum = int(contents.item(n[0], "tag")[0]);
			textarea.see(headingLines[0][headingNum]);
		
		# set up the window
		window = createWindow(self.root, "Help TIDE");
		
		# set up the body frame
		body = ttk.Frame(window, padding=5);
		body.grid(row=0,column=0);
		
		# help files list
		helpList, helpMap = getReadme();
		helpSelect = StringVar(value=helpList[0]);
		helpBox = ttk.Combobox(body, textvariable=helpSelect, values=helpList, state="readonly", font="TkDefaultFont 15");
		helpBox.bind("<<ComboboxSelected>>", lambda e: showReadme());
		helpBox.grid(column=0,row=0,columnspan=2,sticky=(W, E),ipady=2,ipadx=5);
		
		# table of contents
		contentsFrame = ttk.Frame(body);
		contentsFrame.grid(column=0,row=1,sticky=(N, S));
		contentsFrame.rowconfigure(0, weight=1);
		
		contents = ttk.Treeview(contentsFrame, selectmode="browse", show="tree headings");
		contents.column("#0", width=200, minwidth=200);
		contents.heading("#0", text="Table of Contents", anchor=W);
		contents.bind("<<TreeviewSelect>>", lambda e: scrollTo(contents.selection()));
		contents.grid(column=0, row=0, sticky=(N, S));
		
		contentsYScrollbar = ttk.Scrollbar(contentsFrame, orient=VERTICAL, command=contents.yview);
		contents["yscrollcommand"] = contentsYScrollbar.set;
		contentsYScrollbar.grid(column=1,row=0,sticky=(N, S));
		
		contentsXScrollbar = ttk.Scrollbar(contentsFrame, orient=HORIZONTAL, command=contents.xview);
		contents["xscrollcommand"] = contentsXScrollbar.set;
		contentsXScrollbar.grid(column=0,row=1,sticky=(W, E));
		
		# textarea help text
		headingLines = [];
		textareaFrame = ttk.Frame(body);
		textareaFrame.grid(column=1,row=1,sticky=(N, S));
		
		textarea = Text(textareaFrame, width=60, height=30, highlightbackground="#888888", highlightthickness=1, relief=FLAT, state=DISABLED, wrap="word", tabstyle="wordprocessor");
		px = textarea.tk.call("font", "measure", textarea["font"], "-displayof", textarea.master, "    ");
		textarea.configure(tabs=px)
		textarea.grid(column=0,row=0);
		
		textareaScrollbar = ttk.Scrollbar(textareaFrame, orient=VERTICAL, command=textarea.yview);
		textarea["yscrollcommand"] = textareaScrollbar.set;
		textareaScrollbar.grid(column=1,row=0,sticky=(N, S));
		
		# footer buttons
		footerFrame = ttk.Frame(body, padding=(0, 5, 0, 0));
		footerFrame.grid(row=2,column=0,columnspan=2);
		
		close = ttk.Button(footerFrame, text="Close", command=window.destroy);
		close.bind("<Return>", lambda e: close.invoke());
		close.grid(row=0,column=0);
		
		# automatically show the TIDE help
		showReadme();
		
		# center the window on the root
		window.update_idletasks();
		midX = str(int(self.root.winfo_width()/2 - window.winfo_width()/2 + self.root.winfo_x()));
		midY = str(int(self.root.winfo_height()/2 - window.winfo_height()/2 + self.root.winfo_y()));
		window.geometry(str(window.winfo_width())+"x"+str(window.winfo_height())+"+"+midX+"+"+midY);

		# make window the only active window in the program
		window.wait_window();

if __name__ == "__main__":
	root = Tk();
	menu = MenuBar(root);
	root["menu"] = menu.menubar;
	root.mainloop();
