from tkinter import *;
from tkinter import ttk;
from tkinter import filedialog;
from tkinter import messagebox;
from tkinter.font import Font;
from TextEditor import TextEditor;
import idle.Percolator;
import idle.ColorDelegator;
import config;
from createWindow import createWindow;
import sys;
import theme;
import os;
import __main__;
import re;
from directory import HOME_PATH;

class StatusBar:
	def __init__(self, root, parent):
		self.root = root;
		self.parent = parent;
		self.frame = self._createFrame();
	
	def _createFrame(self):
		body = ttk.Frame(self.parent, padding=5);
		body.columnconfigure(0, weight=1);
		
		self.infolabel = ttk.Label(body);
		self.infolabel.grid(row=0,column=0,sticky=W);
		
		self.insertpos = ttk.Label(body, text="Ln 1, Col 0");
		self.insertpos.grid(row=0,column=1,padx=25);

		self.encoding = ttk.Label(body, text="UTF 8");
		self.encoding.grid(row=0,column=2);
	
		return body;

BTN_WIDTH = 10;
WIDTH = 150 + BTN_WIDTH;
class Tab:
	def __init__(self, editor, canvas, container, title, num):
		self.editor = editor;
		self.canvas = canvas;
		self.title = title;
		self.container = container;
		self.width = WIDTH;
		self.height = self.canvas.winfo_reqheight();
		self.x = 0;
		self.y = 0;
		self.active = False;
		self.grabbing = False;
		self.activeBackgroundColor = None;
		self.activeForegroundColor = None;
		self.normalBackgroundColor = None;
		self.normalForegroundColor = None;
		self.number = num;
		
		self.tab = self.canvas.create_rectangle(self.x, self.y, self.x + self.width, self.height, width=0);
		self.tabTitle = self.canvas.create_text(self.x + self.width/2 - BTN_WIDTH/2, self.y + self.height/2, text=self._getTitle(title), font="TkDefaultFont 9");
		self.leftBorder = self.canvas.create_rectangle(self.x-1, self.y, self.x, self.height, width=0, fill="#bbbbbb");
		self.rightBorder = self.canvas.create_rectangle(self.x + self.width, self.y, self.x + self.width+1, self.height, width=0, fill="#bbbbbb");
		self.close = self.canvas.create_text(self.x + self.width - 5, self.y + self.height/2, text="×", font="TkDefaultFont 9", anchor="e", fill="#aaaaaa");
		
		self.canvas.tag_bind(self.close, "<Enter>", lambda e: self.canvas.itemconfigure(self.close, fill="#ff0000"));
		self.canvas.tag_bind(self.close, "<Leave>", lambda e: self.canvas.itemconfigure(self.close, fill="#aaaaaa"));
		self.canvas.tag_bind(self.close, "<1>", lambda e: self.closeTab());
		self.canvas.bind("<<DeactivateTabs>>", lambda e: self.deactivate(), True);
		for item in (self.tab, self.tabTitle, self.leftBorder, self.rightBorder):
			self.canvas.tag_bind(item, "<1>", lambda e: self.activate(), True);
			self.canvas.tag_bind(item, "<1>", lambda e: self.grab(True), True);
			self.canvas.tag_bind(item, "<ButtonRelease>", lambda e: self.grab(False), True);
			self.canvas.tag_bind(item, "<Motion>", lambda e: self.move(), True);
			self.canvas.tag_bind(item, "<2>", lambda e: self.closeTab(), True);
	
	def __str__(self):
		return "Tab(number="+str(self.number)+")";
	
	def grab(self, g):
		"""Grabs the tab and snaps it in position"""
		if g:
			self.grabbing = (self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()) - self.x;
		else:
			self.grabbing = g;
			self.container.repositionTabs();
	
	def move(self):
		"""Move the tab while grabbing"""
		if self.grabbing:
			mx = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx();
			
			scrollregion = self.canvas.cget("scrollregion").split(" ");
			edge = int(scrollregion[2]);
			x = min(max(mx - self.grabbing, 0), edge - self.width);
			self.setX(x);
			idx = self.container.tabs.index(self);
			if idx-1 > -1:
				other = self.container.tabs[idx-1];
				if self.x + self.width/2 < other.x + other.width:
					self.switchWith(idx, idx-1);
			
			if idx+1 < len(self.container.tabs):
				other = self.container.tabs[idx+1];
				if self.x + self.width/2 > other.x:
					self.switchWith(idx, idx+1);
			
			self.container.repositionTabs();
	
	def switchWith(self, meIdx, otherIdx):
		self.container.tabs[meIdx] = self.container.tabs[otherIdx];
		self.container.tabs[otherIdx] = self;
	
	def closeTab(self):
		if self.editor.close(self.number):
			self.canvas.delete(self.tab);
			self.canvas.delete(self.tabTitle);
			self.canvas.delete(self.leftBorder);
			self.canvas.delete(self.rightBorder);
			self.canvas.delete(self.close);
	
	def deactivate(self):
		"""Deactivates the tab"""
		self.active = False;
		self.canvas.itemconfigure(self.tab, fill=self.normalBackgroundColor);
		self.canvas.itemconfigure(self.tabTitle, fill=self.normalForegroundColor);
	
	def activate(self):
		"""Makes all tabs unactive and activates itself"""
		self.canvas.event_generate("<<DeactivateTabs>>");
		self.active = True;
		self.canvas.itemconfigure(self.tab, fill=self.activeBackgroundColor);
		self.canvas.itemconfigure(self.tabTitle, fill=self.activeForegroundColor);
		for item in (self.tab, self.tabTitle, self.leftBorder, self.rightBorder, self.close):
			self.canvas.tag_raise(item);
		
		self.editor.selectFile(self.number);
	
	def _getTitle(self, text):
		"""Adds the '...' if [text] is to long"""
		textWidth = self.canvas.tk.call("font", "measure", "TkDefaultFont 9", "-displayof", self.canvas.master, text);
		if textWidth > WIDTH-12 - BTN_WIDTH:
			dotWidth = self.canvas.tk.call("font", "measure", "TkDefaultFont 9", "-displayof", self.canvas.master, ".");
			extraWidth = textWidth - (WIDTH-10 - BTN_WIDTH);
			lMid = int(len(text)/2 - (extraWidth/dotWidth)/2)-2;
			gMid = int(len(text)/2 + (extraWidth/dotWidth)/2)+2;
			return text[:lMid] + "..." + text[gMid:];
		
		return text;
	
	def setX(self, x):
		moveAmount = x - self.x;
		self.x = x;
		for item in (self.tab, self.tabTitle, self.leftBorder, self.rightBorder, self.close):
			self.canvas.move(item, moveAmount, 0);
	
	def updateTheme(self):
		currentTheme = config.get("editor", "theme");
		self.activeBackgroundColor = theme.get(currentTheme, "tabactive");
		self.activeForegroundColor = theme.get(currentTheme, "tabactive-text");
		self.normalBackgroundColor = theme.get(currentTheme, "tabnormal");
		self.normalForegroundColor = theme.get(currentTheme, "tabnormal-text");
		
		if self.active:
			b = self.activeBackgroundColor;
			f = self.activeForegroundColor;
		else:
			b = self.normalBackgroundColor;
			f = self.normalForegroundColor;
	
		self.canvas.itemconfigure(self.tab, fill=b);
		self.canvas.itemconfigure(self.tabTitle, fill=f);

class TabContainer:
	def __init__(self, root, parent, editor):
		self.root = root;
		self.parent = parent;
		self.editor = editor;
		self.frame = self._createFrame();
		self.tabs = [];
	
	def _createFrame(self):
		body = ttk.Frame(self.parent);
		body.columnconfigure(0, weight=1);
		
		self.canvas = Canvas(body, height=30, borderwidth=0, highlightthickness=0, scrollregion=(0, 0, 0, 0));
		self.canvas.grid(row=0,column=0,sticky=(W, E));
		self.canvas.bind("<Configure>", lambda e: self.updateScrollbar());
		
		self.scrollX = ttk.Scrollbar(body, orient=HORIZONTAL, command=self.canvas.xview);
		self.scrollX.grid(row=1,column=0,sticky=(W, E));
		self.scrollX.grid_remove();
		self.canvas["xscrollcommand"] = self.scrollX.set;
		
		ttk.Separator(body, orient=HORIZONTAL).grid(row=2,column=0,sticky=(W, E));
		
		return body;
	
	def addTab(self, title, num):
		tab = Tab(self.editor, self.canvas, self, title, num);
		tab.setX(tab.width * len(self.tabs));
		tab.updateTheme();
		
		self.tabs.append(tab);
		self.updateScrollbar();
	
	def updateScrollbar(self):
		if len(self.tabs) > 0:
			allTabsWidth = len(self.tabs)*self.tabs[0].width;
		else:
			allTabsWidth = 0;
		
		self.canvas.configure(scrollregion=(0, 0, allTabsWidth, 0));
		
		if allTabsWidth > self.canvas.winfo_width():
			self.scrollX.grid();
		else:
			self.scrollX.grid_remove();
	
	def repositionTabs(self):
		for tab, i in zip(self.tabs, range(len(self.tabs))):
			if tab.grabbing: continue;
			
			tab.setX(tab.width * i);
	
	def updateTheme(self):
		self.canvas.configure(background=theme.get(config.get("editor", "theme"), "tabbar"));
		for t in self.tabs:
			t.updateTheme();
	
	def close(self, tab):
		self.tabs.pop(self.tabs.index(tab));
		self.updateScrollbar();

class LineNumbers:
	def __init__(self, root, parent):
		self.root = root;
		self.parent = parent;
		self._font = None;
		self._padx = 5;

		linenumbersStyles = theme.get(config.get("editor", "theme"), "linenumbers").split(" ");
		self.gutter = Canvas(self.parent, width=0, borderwidth=0, highlightthickness=0, background=linenumbersStyles[0]);
	
	def updateNumberTag(self):
		linenumbersStyles = theme.get(config.get("editor", "theme"), "linenumbers").split(" ");
		self.gutter.itemconfigure("number", justify="right", anchor="ne", font=self._font, fill=linenumbersStyles[1]);
	
	def updateGutterWidth(self, textareaConnect):
		fontInfo = Font(font=self._font);
		width = fontInfo.measure(" ");
		lastLine = str(int(float(textareaConnect.index("end - 1 char"))));
		self.gutter.configure(width=max(width*2, width*len(lastLine))+self._padx*2);
	
	def updateFont(self, textareaConnect):
		self._font = textareaConnect["font"];
		self.updateGutterWidth(textareaConnect);
		self.updateNumberTag();
	
	def updateTheme(self, textareaConnect):
		linenumbersStyles = theme.get(config.get("editor", "theme"), "linenumbers").split(" ");
		self.gutter.configure(background=linenumbersStyles[0]);
		self.updateFont(textareaConnect);
		self.updateNumberTag();
	
	def updateNumbers(self, textareaConnect):
		xviewNow = textareaConnect.xview();
		firstVisLine = int(float(textareaConnect.index("@0,0")));
		lastVisLine = int(float(textareaConnect.index(f"@0,{textareaConnect.winfo_height()}")));
		
		self.gutter.delete("number");
		preBbox = None;
		for i in range(firstVisLine, lastVisLine+1):
			textareaConnect.xview_moveto(0);
			bbox = textareaConnect.bbox(f"{i}.0");
			if bbox is not None:
				textareaConnect.xview_moveto(xviewNow[0]);
				self.gutter.create_text(self.gutter.winfo_width()-self._padx, bbox[1], text=str(i), tags=("number"));
	
		self.updateNumberTag();
		self.updateGutterWidth(textareaConnect);
		self.gutter.update_idletasks();
	
class Editor:
	def __init__(self, root, parent):
		self.root = root;
		self.parent = parent;
		self.frame = self._createFrame();
		self.files = [];
		self.insertPositions = [];
		self.activeFile = None;
		self.finds = [];
		self.findPos = -1;
		self.phrase = StringVar();
		self.replacement = StringVar();
		self.lineNumber = StringVar();
		self.phrase.trace("w", lambda *args: self.findAll());
		self.lineNumber.trace("w", lambda *args: self.setInsertLineNum());
		
		self.regexpValue = StringVar(value="false");
		self.caseValue = StringVar(value="false");
		self.replaceAllValue = StringVar(value="true");
		self._bindings = [];
	
	def bind(self, event, callback, addOn=False):
		userid = self.textarea.bind(event, callback, addOn);
		self._bindings.append([event, callback, addOn, userid, userid]);
		
		return userid;
	
	def unbind(self, event, userid):
		for e in self._bindings:
			if e[3] == userid:
				self._bindings.remove(e);
				return self.textarea.unbind(event, e[4]);

	
	def _createFrame(self):
		body = ttk.Frame(self.parent);
		body.rowconfigure(1, weight=1);
		body.columnconfigure(0, weight=1);
		
		self.tabsContainer = TabContainer(self.root, body, self);
		self.tabsContainer.frame.grid(row=0,column=0,sticky=(W, E));

		editor = ttk.Frame(body);
		editor.rowconfigure(0, weight=1);
		editor.columnconfigure(1, weight=1);
		editor.grid(row=1,column=0,sticky=(N, E, S, W));
		
		self.linenumbers = LineNumbers(self.root, editor);
		self.linenumbers.gutter.grid(row=0,column=0,sticky=(N, S));
		if config.get("editor", "numbers") == "false":
			self.linenumbers.gutter.grid_remove();

		self.modal = ttk.Frame(editor, padding=5);
		self.modalMode = None;

		self.textarea = Text(editor);
		
		self.scrollY = ttk.Scrollbar(editor, orient=VERTICAL);
		self.scrollY.grid(row=0,column=2,sticky=(N, S));
		
		self.scrollX = ttk.Scrollbar(editor, orient=HORIZONTAL);
		self.scrollX.grid(row=1,column=0,columnspan=3,sticky=(W, E));
		
		ttk.Separator(body, orient=HORIZONTAL).grid(row=2,column=0,columnspan=3,sticky=(W, E));
		
		self.statusbar = StatusBar(self.root, body);
		self.statusbar.frame.grid(row=3,column=0,columnspan=2,sticky=(W, E));
		
		self.root.event_add("<<Save>>", "<Control-s>");
		self.root.event_add("<<SaveAs>>", "<Shift-Control-S>");
		self.root.event_add("<<Wrap>>", "<F8>");
		self.root.event_add("<<OpenFile>>", "<Control-o>");
		self.root.event_add("<<OpenModule>>", "<Control-m>");
		self.root.event_add("<<NewFile>>", "<Control-n>");
		self.root.event_add("<<Close>>", "<Control-w>");
		self.root.event_add("<<GoToLine>>", "<Control-l>");
		self.root.event_add("<<Find>>", "<Control-f>");
		self.root.event_add("<<Replace>>", "<Control-h>");
		self.root.bind("<<UpdateTabWidth>>", lambda e: self.updateTabWidth());
		self.root.bind("<<ToggleLineNumbers>>", lambda e: self.toggleLineNumbers());
		self.root.bind("<<UpdateFont>>", lambda e: self.updateFont());
		self.root.bind("<<UpdateTheme>>", lambda e: self.updateTheme());
		self.root.bind("<<Wrap>>", lambda e: self.updateWrap());
		self.root.bind("<<Save>>", lambda e: self.updateTheme());
		self.root.bind("<<Save>>", lambda e: self.save());
		self.root.bind("<<SaveAs>>", lambda e: self.saveAs());
		self.root.bind("<<OpenFile>>", lambda e: self.openFile());
		self.root.bind("<<OpenModule>>", lambda e: self.openModule());
		self.root.bind("<<NewFile>>", lambda e: self.newFile());
		self.root.bind("<<Close>>", lambda e: self.closeCurrent());
		self.root.bind("<<SelectAll>>", lambda e: self.runEvent("<<Select>>"));
		self.root.bind("<<CutText>>", lambda e: self.runEvent("<<Cut>>"));
		self.root.bind("<<CopyText>>", lambda e: self.runEvent("<<Copy>>"));
		self.root.bind("<<PasteText>>", lambda e: self.runEvent("<<Paste>>"));
		self.root.bind("<<DeleteText>>", lambda e: self.runEvent("<<Delete>>"));
		self.root.bind("<<Indent>>", lambda e: self.runEvent("<<IndentText>>"));
		self.root.bind("<<Outdent>>", lambda e: self.runEvent("<<OutdentText>>"));
		self.root.bind("<<Comment>>", lambda e: self.runEvent("<<CommentText>>"));
		self.root.bind("<<Uncomment>>", lambda e: self.runEvent("<<UncommentText>>"));
		self.root.bind("<<GoToLine>>", lambda e: self.goToLine(), True);
		self.root.bind("<<Find>>", lambda e: self.find());
		self.root.bind("<<Replace>>", lambda e: self.replace());
		self.root.bind("<1>", lambda e: self.removeModal(e.widget), True);
		for i in range(10):
			self.root.bind("<<OpenRecent"+str(i)+">>", lambda e, n=i: self.openRecent(n));
		
		return body;
	
	def searchDir(self, direction):
		if self.findPos + direction == len(self.finds):
			self.findPos = 0;
		elif self.findPos + direction == -1:
			self.findPos = len(self.finds)-1;
		else:
			self.findPos += direction;
		
		self.textarea.tag_remove("highlight", "1.0", "end");
		
		start, end, _ = self.finds[self.findPos];
		self.textarea.tag_add("highlight", start, end);
		self.textarea.mark_set("insert", start);
		self.textarea.see("insert");
		
	def replacePhrase(self):
		if len(self.finds) == 0: return;
		
		replace = self.replacement.get();
		addOn = 0;
		line = 1;
		insert = self.textarea.index("insert");
		content = self.textarea.get("1.0", "end");
		phrase = self.phrase.get();
		useCase = self.caseValue.get() == "true";
		useRegexp = self.regexpValue.get() == "true";
		
		if self.replaceAllValue.get() == "true":
			startIdx = "1.0";
			lenFound = IntVar(value=0);
			margin = 0;
			while True:
				startIdx = self.textarea.search(phrase, startIdx+" + "+str(margin)+" char", regexp=useRegexp, nocase=(not useCase), count=lenFound, stopindex="end - 1 char");
				if startIdx != "":
					self.textarea.delete(startIdx, startIdx+" + "+str(lenFound.get())+" char");
					self.textarea.insert(startIdx, replace);
					margin = len(replace);
				else:
					break;
		else:
			start, end = self.textarea.tag_ranges("highlight");
			self.textarea.delete(start, end);
			self.textarea.insert(start, replace);
		
		self.textarea.edit_separator();
		self.findAll();
		
	def findAll(self):
		self.findPos = -1;
		phrase = self.phrase.get();
		useCase = self.caseValue.get() == "true";
		useRegexp = self.regexpValue.get() == "true";
		self.textarea.tag_remove("FOUND", "1.0", "end");
		self.textarea.tag_remove("highlight", "1.0", "end");
		while len(self.finds) > 0: self.finds.pop(0);
		
		if phrase != "":
			startIdx = "1.0";
			lenFound = IntVar(value=0);
			movedInsert = False;
			i = 0;
			
			# prevents infinite loops
			while i < 10000:
				i += 1;
				startIdx = self.textarea.search(phrase, startIdx+" + "+str(lenFound.get())+" char", regexp=useRegexp, nocase=(not useCase), count=lenFound, stopindex="end - 1 char");
				
				if startIdx != "":
					endIdx = startIdx+" + "+str(lenFound.get())+" char";
					if not movedInsert:
						if self.textarea.compare("insert", "<=", endIdx) == True:
							self.textarea.mark_set("insert", startIdx);
							movedInsert = True;
							self.findPos = i-1;
						
					self.textarea.tag_add("FOUND", startIdx, endIdx);
					self.finds.append((startIdx, endIdx, lenFound.get()));
				else:
					break;
			
			if len(self.finds) > 0:
				s, e, _ = self.finds[self.findPos];
				self.textarea.tag_add("highlight", s, e);
				
				if len(self.modal.winfo_children()) > 1:
					self.modal.winfo_children()[1].configure(foreground="#000000");
	
				if not movedInsert:
					self.textarea.mark_set("insert", self.finds[0][0]);
			else:
				if len(self.modal.winfo_children()) > 1:
					self.modal.winfo_children()[1].configure(foreground="#ff0000");
		
		self.textarea.see("insert");
		self.textarea.tag_raise("FOUND");
		self.textarea.tag_raise("highlight");
		self.textarea.tag_raise("sel");
	
	def setInsertLineNum(self):
		pos = self.lineNumber.get();
		
		if len(pos) > 0 and re.match(r"[0-9]+", pos):
			intpos = int(pos);
			pos += ".0";
			if intpos < 1 or int(float(self.textarea.index("end - 1 char"))) < intpos:
				if len(self.modal.winfo_children()) > 1:
					self.modal.winfo_children()[1].configure(foreground="#ff0000");
			else:
				self.textarea.mark_set("insert", pos);
				self.textarea.see("insert");
				self.textarea.tag_remove("highlight", "1.0", "end");
				self.textarea.tag_add("highlight", pos+" linestart", pos+" lineend + 1 char");

				if len(self.modal.winfo_children()) > 1:
					self.modal.winfo_children()[1].configure(foreground="#000000");
		else:
			if len(self.modal.winfo_children()) > 1:
				self.modal.winfo_children()[1].configure(foreground="#ff0000");
			
	def removeModal(self, widget):
		def isChildOf(parent):
			for ch in parent.winfo_children():
				if ch == widget:
					return True;
				elif len(ch.winfo_children()) > 0:
					if isChildOf(ch):
						return True;
			
			return False;
		
		if widget != self.modal and not isChildOf(self.modal):
			self.modalMode = None;
			self.textarea.tag_remove("highlight", "1.0", "end");
			self.textarea.tag_remove("FOUND", "1.0", "end");
			self.modal.place_forget();
	
	def find(self):
		if self.modalMode != "find":
			self.modalMode = "find";
			for ch in self.modal.winfo_children(): ch.destroy();
			
			ttk.Label(self.modal, text="Find:").grid(row=0,column=0,sticky=W);
			
			if len(self.textarea.tag_ranges("sel")) > 0:
				self.phrase.set(self.textarea.selection_get());
			
			pattern = ttk.Entry(self.modal, textvariable=self.phrase);
			pattern.bind("<Up>", lambda e: self.searchDir(-1));
			pattern.bind("<Down>", lambda e: self.searchDir(1));
			pattern.grid(row=1,column=0,sticky=(W, E));
			pattern.focus_set();
			pattern.select_range("0", "end");
			
			group = ttk.Frame(self.modal, padding=(0, 5, 0, 0));
			group.grid(row=2,column=0,sticky=W);
			
			case = ttk.Checkbutton(group, text="Match Case", onvalue="true", offvalue="false", variable=self.caseValue, command=lambda: self.findAll());
			case.grid(row=0,column=0);
			
			regex = ttk.Checkbutton(group, text="RegExp", onvalue="true", offvalue="false", variable=self.regexpValue, padding=(10, 0, 0, 0), command=lambda: self.findAll());
			regex.grid(row=0,column=1);
			
			self.modal.place(x=0, y=0);
			self.modal.update_idletasks();
			self.modal.place(x=self.frame.winfo_width() - self.modal.winfo_width() - self.scrollY.winfo_width(), y=0);
			self.modal.lift();
			self.findAll();
			
		return "break";
	
	def replace(self):
		if self.modalMode != "replace":
			self.modalMode = "replace";
			for ch in self.modal.winfo_children(): ch.destroy();
			
			ttk.Label(self.modal, text="Find:").grid(row=0,column=0,sticky=W);
			
			try: self.phrase.set(self.textarea.selection_get());
			except: pass;
			
			pattern = ttk.Entry(self.modal, textvariable=self.phrase);
			pattern.bind("<Up>", lambda e: self.searchDir(-1));
			pattern.bind("<Down>", lambda e: self.searchDir(1));
			pattern.grid(row=1,column=0,sticky=(W, E));
			pattern.focus_set();
			pattern.select_range("0", "end");
			
			ttk.Label(self.modal, text="Replace:").grid(row=2,column=0,sticky=W);
			
			replacement = ttk.Entry(self.modal, textvariable=self.replacement);
			replacement.grid(row=3,column=0,sticky=(W, E));
			
			group = ttk.Frame(self.modal, padding=(0, 5, 0, 0));
			group.grid(row=4,column=0,sticky=W);
			
			case = ttk.Checkbutton(group, text="Match Case", onvalue="true", offvalue="false", variable=self.caseValue, command=lambda: self.findAll());
			case.grid(row=0,column=0);
			
			regex = ttk.Checkbutton(group, text="RegExp", onvalue="true", offvalue="false", variable=self.regexpValue, padding=(10, 0), command=lambda: self.findAll());
			regex.grid(row=0,column=1);
			
			rall = ttk.Checkbutton(group, text="Replace All", onvalue="true", offvalue="false", variable=self.replaceAllValue);
			rall.grid(row=0,column=2,sticky=W);
			
			bgroup = ttk.Frame(self.modal, padding=(0, 10, 0, 0));
			bgroup.grid(row=5,column=0,sticky=W);

			rbtn = ttk.Button(bgroup, text="Replace", command=lambda: self.replacePhrase());
			rbtn.bind("<Return>", lambda e: rbtn.invoke());
			rbtn.grid(row=0,column=0);
			
			self.modal.place(x=0, y=0);
			self.modal.update_idletasks();
			self.modal.place(x=self.frame.winfo_width() - self.modal.winfo_width() - self.scrollY.winfo_width(), y=0);
			self.modal.lift();
			self.findAll();
			
		return "break";
	
	def goToLine(self):
		if self.modalMode != "gotoline":
			self.modalMode = "gotoline";
			for ch in self.modal.winfo_children(): ch.destroy();
			
			ttk.Label(self.modal, text="Go to line:").grid(row=0,column=0,sticky=W);
			
			self.lineNumber.set(int(float(self.textarea.index("insert"))));
			
			line = ttk.Entry(self.modal, textvariable=self.lineNumber);
			line.grid(row=1,column=0,sticky=(W, E));
			line.focus_set();
			line.select_range("0", "end");
			
			self.modal.place(x=0, y=0);
			self.modal.update_idletasks();
			self.modal.place(x=self.frame.winfo_width() - self.modal.winfo_width() - self.scrollY.winfo_width(), y=0);
			self.modal.lift();
			
		return "break";
	
	def runEvent(self, event):
		self.textarea.event_generate(event);
		self.disableSelectionMenuItems();
		
		return "break";
	
	def deleteSelection(self):
		ranges = self.textarea.tag_ranges("sel");
		if len(ranges) > 0:
			self.textarea.delete(ranges[0], ranges[1]);
		
		self.disableSelectionMenuItems();
	
	def _getSelectRanges(self):
		ranges = self.textarea.tag_ranges("sel");
		start = int(float(str(ranges[0])));
		end = str(ranges[1]);
		end = self.textarea.index("end - 1 char") if self.textarea.index("end") == end else end;
		end = int(float(end));
		
		return start, end;
	
	def outdent(self):
		ranges = self.textarea.tag_ranges("sel");
		tab = " "*int(config.get("editor", "tab")) if config.get("editor", "spaces") == "true" else "\t";
		if len(ranges) > 0:
			start, end = self._getSelectRanges();
			for line in range(start, end+1):
				if self.textarea.get(str(line)+".0").startswith(tab):
					self.textarea.delete(str(line)+".0", str(line)+".0 + "+str(len(tab))+" chars");
		else:
			if self.textarea.get("insert linestart").startswith(tab):
				self.textarea.delete("insert linestart", "insert linestart + "+str(len(tab))+" chars");
		
		self.disableSelectionMenuItems();
	
	def indent(self):
		ranges = self.textarea.tag_ranges("sel");
		tab = " "*int(config.get("editor", "tab")) if config.get("editor", "spaces") == "true" else "\t";
		if len(ranges) > 0:
			start, end = self._getSelectRanges();
			for line in range(start, end+1):
				self.textarea.insert(str(line)+".0", tab);
		else:
			self.textarea.insert("insert", tab);
		
		self.disableSelectionMenuItems();
	
	def comment(self):
		self.textarea.edit_separator();
		ranges = self.textarea.tag_ranges("sel");
		if len(ranges) > 0:
			start, end = self._getSelectRanges();
			for line in range(start, end+1):
				self.textarea.insert(str(line)+".0", "#");
		else:
			self.textarea.insert("insert linestart", "#");
		
		self.disableSelectionMenuItems();
		self.textarea.edit_separator();
	
	def uncomment(self):
		self.textarea.edit_separator();
		ranges = self.textarea.tag_ranges("sel");
		if len(ranges) > 0:
			start, end = self._getSelectRanges();
			for line in range(start, end+1):
				pos = str(line)+".0";
				if self.textarea.get(pos, pos+" lineend").strip().find("#") == 0:
					t = self.textarea.get(pos, pos+" lineend");
					self.textarea.delete(pos + " + " + str(t.find("#")) + " chars");
		else:
			if self.textarea.get("insert linestart", "insert lineend").strip().find("#") == 0:
				t = self.textarea.get("insert linestart", "insert lineend");
				self.textarea.delete("insert linestart + " + str(t.find("#")) + " chars");
		
		self.disableSelectionMenuItems();
		self.textarea.edit_separator();

	def selectWord(self, start, end, setAtStart):
		ranges = self.textarea.tag_ranges("sel");
		selected = len(ranges) > 0;
		removingSelect = False;
		if selected:
			startLessThanSelEnd = self.textarea.compare(start, "<", ranges[1]) == True;
			startMoreThanSelStart = self.textarea.compare(start, ">", ranges[0]) == True;
			endLessThanSelEnd = self.textarea.compare(end, "<", ranges[1]) == True;
			endMoreThanSelStart = self.textarea.compare(end, ">", ranges[0]) == True;
			removingSelect = (startLessThanSelEnd and startMoreThanSelStart and setAtStart) or (endLessThanSelEnd and endMoreThanSelStart and not setAtStart);
		
		if removingSelect:
			self.textarea.tag_remove("sel", start, end);
		else:
			self.textarea.tag_add("sel", start, end);

		self.textarea.mark_set("insert", start if setAtStart else end);
	
	def deleteLine(self):
		self.textarea.delete("insert linestart", "insert lineend + 1 char");
		
		return "break";

	def updateInsertPos(self):
		idx = self.files.index(self.activeFile);
		if idx < len(self.insertPositions):
			self.insertPositions[idx] = self.textarea.index("insert");
		else:
			self.insertPositions.append(self.textarea.index("insert"));
			
	def _createTextarea(self, file):
		def yscroll(*args):
			self.scrollY.set(*args);
			self.linenumbers.updateNumbers(self.textarea);
			
		
		self.textarea.destroy();
		if len(file.textarea.peer_names()) == 0:
			font = (config.get("editor", "font"), config.get("editor", "size"), config.get("editor", "weight"));
			px = self.root.tk.call("font", "measure", font, "-displayof", self.root, " "*int(config.get("editor", "tab")));
			kargs = {
				"undo": True,
				"font": font,
				"highlightthickness": 0,
				"borderwidth": 0,
				"padx": 5,
				"pady": 5,
				"wrap": "word" if config.get("view", "wrap") == "true" else "none",
				"tabstyle": "wordprocessor",
				"exportselection": True,
				"tabs": px,
			};
			file.textarea.peer_create(file.path, **kargs);
		
		BaseWidget._setup(self.textarea, self.textarea.master, {"name": file.name});
		
		self.scrollY.grid();
		self.scrollY["command"] = self.textarea.yview;
		self.scrollX["command"] = self.textarea.xview;
		self.textarea["yscrollcommand"] = yscroll;
		self.textarea["xscrollcommand"] = self.scrollX.set;
		
		if config.get("view", "wrap") == "true": self.scrollX.grid_remove();
		else: self.scrollX.grid();
		
		self.textarea.bind("<KeyRelease>", lambda e: self.checkSaved(), True);
		self.textarea.bind("<KeyPress>", lambda e: self.updateLnCol(), True);
		self.textarea.bind("<KeyRelease>", lambda e: self.updateLnCol(), True);
		self.textarea.bind("<ButtonRelease>", lambda e: self.updateLnCol(), True);
		self.textarea.bind("<KeyPress>", lambda e: self.linenumbers.updateNumbers(self.textarea), True);
		self.textarea.bind("<KeyRelease>", lambda e: self.linenumbers.updateNumbers(self.textarea), True);
		self.textarea.bind("<KeyRelease>", lambda e: self.updateInsertPos(), True);
		self.textarea.bind("<ButtonRelease>", lambda e: self.updateInsertPos(), True);
		self.textarea.bind("<<Selection>>", lambda e: self.enableSelectionMenuItems(), True);
		self.textarea.bind("<KeyRelease>", lambda e: self.disableSelectionMenuItems(), True);
		self.textarea.bind("<ButtonRelease>", lambda e: self.disableSelectionMenuItems(), True);
		self.textarea.bind("<Control-a>", lambda e: self.runEvent("<<Select>>"), True);
		self.textarea.bind("<Control-z>", lambda e: self.runEvent("<<Undo>>"), True);
		self.textarea.bind("<Shift-Control-Z>", lambda e: self.runEvent("<<Redo>>"), True);
		self.textarea.bind("<Control-x>", lambda e: self.runEvent("<<Cut>>"), True);
		self.textarea.bind("<Control-c>", lambda e: self.runEvent("<<Copy>>"), True);
		self.textarea.bind("<Control-v>", lambda e: self.runEvent("<<Paste>>"), True);
		self.textarea.bind("<Tab>", lambda e: self.runEvent("<<IndentText>>"), True);
		self.textarea.bind("<Shift-Key-Tab>", lambda e: self.runEvent("<<OutdentText>>"), True);
		self.textarea.bind("<Control-Key-3>", lambda e: self.runEvent("<<CommentText>>"), True);
		self.textarea.bind("<Shift-Control-Key-#>", lambda e: self.runEvent("<<UncommentText>>"), True);
		self.textarea.bind("<Control-BackSpace>", lambda e: self.textarea.delete("insert - 1 char wordstart", "insert"), True);
		self.textarea.bind("<Control-Delete>", lambda e: self.textarea.delete("insert", "insert wordend"), True);
		self.textarea.bind("<Control-Left>", lambda e: self.textarea.mark_set("insert", "insert - 1 char wordstart"), True);
		self.textarea.bind("<Control-Right>", lambda e: self.textarea.mark_set("insert", "insert wordend"), True);
		self.textarea.bind("<Shift-Control-Left>", lambda e: self.selectWord("insert - 1 char wordstart", "insert", True), True);
		self.textarea.bind("<Shift-Control-Right>", lambda e: self.selectWord("insert", "insert wordend", False), True);
		self.textarea.bind("<Control-d>", lambda e: self.deleteLine(), True);
		self.textarea.bind("<Control-BackSpace>", lambda e: "break", True);
		self.textarea.bind("<Control-Delete>", lambda e: "break", True);
		self.textarea.bind("<Control-Left>", lambda e: "break", True);
		self.textarea.bind("<Control-Right>", lambda e: "break", True);
		self.textarea.bind("<Shift-Control-Left>", lambda e: "break", True);
		self.textarea.bind("<Shift-Control-Right>", lambda e: "break", True);
		self.textarea.bind("<<Delete>>", lambda e: self.deleteSelection(), True);
		self.textarea.bind("<<Select>>", lambda e: self.textarea.tag_add("sel", "1.0", "end"));
		self.textarea.bind("<<IndentText>>", lambda e: self.indent(), True);
		self.textarea.bind("<<OutdentText>>", lambda e: self.outdent(), True);
		self.textarea.bind("<<CommentText>>", lambda e: self.comment(), True);
		self.textarea.bind("<<UncommentText>>", lambda e: self.uncomment(), True);
		
		separators = ("Tab", "grave", "asciitilde", "exclam", "at", "numbersign", "dollar", "percent", "asciicircum", "ampersand", "asterisk", "parenleft", "parenright", "minus", "equal", "underscore", "plus", "bracketleft", "bracketright", "braceleft", "braceright", "backslash", "bar", "semicolon", "apostrophe", "colon", "quotedbl", "comma", "period", "slash", "less", "greater", "question", "space", "Control-BackSpace");
		for keysym in separators:
			self.textarea.bind("<"+keysym+">", lambda e: self.textarea.edit_separator(), True);
		
		def s(idx):
			if idx < len(self.tabsContainer.tabs):
				self.tabsContainer.tabs[idx].activate();
		
		for n in range(1, 11):
			nu = n;
			if n == 10:
				n = 0;
				nu = 10;
			
			self.textarea.bind("<Alt-Key-"+str(n)+">", lambda e, num=nu: s(num-1));
		
		bindings = (("Control-s", "Save"), ("Shift-Control-S", "SaveAs"), ("Control-o", "OpenFile"), ("Control-m", "OpenModule"), ("Control-n", "NewFile"), ("Control-f", "Find"), ("Control-h", "Replace"), ("Control-l", "GoToLine"));
		for bind, callback in bindings:
			self.textarea.bind("<"+bind+">", lambda e, c=callback: self.root.event_generate("<<"+c+">>"), True);
			self.textarea.bind("<"+bind+">", lambda e: "break", True);
		
		for i in range(len(self._bindings)):
			event, callback, addOn, _, __ = self._bindings[i];
			id = self.textarea.bind(event, callback, addOn);
			self._bindings[i][4] = id;
		
		self.textarea.grid(row=0,column=1,sticky=(N, S, W, E));
		self.textarea.focus_set();
		self.textarea.mark_set("insert", self.insertPositions[self.files.index(self.activeFile)] if self.files.index(self.activeFile) < len(self.insertPositions) else "1.0");
		
		self.percolator = idle.Percolator.Percolator(self.textarea);
		self.percolator.insertfilter(idle.ColorDelegator.ColorDelegator());
		self.updateTheme();
		
		self.textarea.update_idletasks();
		self.linenumbers.updateNumbers(self.textarea);

	def enableSelectionMenuItems(self):
		enable = ("Cut", "Copy", "Delete", "Indent Region");
		for item in enable:
			self.root.event_generate("<<"+item+" Enable>>");

	def disableSelectionMenuItems(self):
		if len(self.textarea.tag_ranges("sel")) == 0:
			disable = ("Cut", "Copy", "Delete", "Indent Region");
			for item in disable:
				self.root.event_generate("<<"+item+" Disable>>");
			
	def closeCurrent(self):
		for tab in self.tabsContainer.tabs:
			if tab.active:
				tab.closeTab();
				break;
	
	def openModule(self):
		"""Imports modules found in sys.path"""
		def findModule():
			found = False;
			if module.get() != "":
				modulePath = "/".join(module.get().split("."));
				paths = [p for p in sys.path];
			
				if self.activeFile.filename:
					paths[0] = os.path.dirname(self.activeFile.filename);
				else:
					paths[0] = "";
			
				for path in paths:
					fullPath = path+"/"+modulePath;
					if os.path.isfile(fullPath+".py"):
						window.destroy();
						self.newFile(fullPath+".py", True);
						found = True;
					elif os.path.isfile(fullPath+"/__init__.py"):
						window.destroy();
						self.newFile(fullPath+"/__init__.py", True);
						found = True;
				
					if found:
						break;
			
			if not found:
				def r():
					"""Creates an error if module is opened while error is displayed"""
					try: errorLabel.grid_remove();
					except: pass;

				errorLabel.grid();
				self.root.after(5000, r);
		
		window = createWindow(self.root, "Open Module");
		destroyed = False;
		
		body = ttk.Frame(window, padding=5);
		body.grid(row=0,column=0);
		
		ttk.Label(body, text="Type in the python module you want to open:").grid(row=0,column=0);
		
		errorLabel = ttk.Label(body, text="Module not found", foreground="#ff0000");
		errorLabel.grid(row=1,column=0,sticky=W);
		errorLabel.grid_remove();
		
		module = ttk.Entry(body);
		module.bind("<Return>", lambda e: ok.invoke());
		module.focus_set();
		module.grid(row=2,column=0,sticky=(W, E),pady=5,ipady=1);
		
		footer = ttk.Frame(body, padding=(0, 5, 0, 0));
		footer.grid(row=3,column=0);
		
		ok = ttk.Button(footer, text="Ok", command=findModule);
		ok.bind("<Return>", lambda e: ok.invoke());
		ok.grid(row=0,column=0,padx=5);
		
		cancel = ttk.Button(footer, text="Cancel", command=window.destroy);
		cancel.bind("<Return>", lambda e: cancel.invoke());
		cancel.grid(row=0,column=1,padx=5);
		
		window.wait_window();
	
	def openFile(self, files=None):
		if files == None:
			files = filedialog.askopenfilenames(title="Open Python Scripts", filetypes=[("Python Script", ("*.py", "*.pyw"))]);

		if len(files) > 0:
			for f in files:
				self.newFile(f, True);
	
	def saveAs(self):
		f = filedialog.asksaveasfilename(title="Save Python Script", filetypes=[("Python Script", ("*.py", "*.pyw"))]);
		
		if len(f) > 0:
			self.activeFile.filename = f;
			self.save();

	def save(self, file=None):
		if file == None: file = self.activeFile;
		
		if not file.filename:
			self.saveAs();
		else:
			with open(file.filename, "w", encoding=file.encoding, errors=file.err) as f:
				t = file.textarea.get("1.0", "end - 1 char");
				file.savedText = hash(t);
				f.write(t);
			
			for tab in self.tabsContainer.tabs:
				if tab.number == self.files.index(file):
					tab.title = os.path.basename(file.filename);
					self.tabsContainer.canvas.itemconfigure(tab.tabTitle, text=tab._getTitle(tab.title));
					break;
			
			self.updateRecentFiles(file.filename);
			file.saved = True;
			file.textarea.edit_modified(False);
			self.root.title(file.filename+" - TIDE v"+__main__.__version__);
		
	def updateRecentFiles(self, file):
		if file != None:
			with open(HOME_PATH+"/.tide/recent.txt", "r") as f:
				files = f.read().strip().split("\n");
				if file not in files:
					files.insert(0, file);
					files = files[:10];
					f = open(HOME_PATH+"/.tide/recent.txt", "w");
					f.write("\n".join(files).strip());
					f.close();
					self.root.event_generate("<<UpdateRecent>>");
	
	def openRecent(self, n):
		with open(HOME_PATH+"/.tide/recent.txt", "r") as f:
			files = f.read().strip().split("\n");
			self.newFile(files[n], True);
	
	def newFile(self, file=None, opening=False):
		texteditor = TextEditor(self.textarea.master, file);
		
		if hasattr(texteditor, "window"):
			if len(self.files) > 0 and self.files[-1].filename == None and self.files[-1].saved and opening:
				for tab in self.tabsContainer.tabs:
					if tab.number == len(self.files)-1:
						tab.closeTab();
			
			self.updateRecentFiles(file);
			self.files.append(texteditor);
			self.selectFile(-1);
			title = os.path.basename(file) if file != None else "Untitled Python Script";
			num = len(self.files)-1;
			self.tabsContainer.addTab(title, num);
			self.tabsContainer.tabs[-1].activate();
			if opening:
				self.linenumbers.updateNumbers(self.textarea);
	
			disable = ("Cut", "Copy", "Delete", "Indent Region");
			enable = ("Undo", "Redo", "Select All", "Paste", "Go to Line", "Find", "Find in Files", "Replace", "Comment Code", "Uncomment Code", "Outdent Region", "Save", "Save As", "Close");
			for item in disable: self.root.event_generate("<<"+item+" Disable>>");
			for item in enable: self.root.event_generate("<<"+item+" Enable>>");
			
			# strange bug with the * in the tab, this fixes it.
			if opening:
				self.save();
	
	def selectFile(self, idx):
		if idx >= len(self.files): return;
		
		file = self.files[idx];
		self.activeFile = file;
		if file.filename:
			s = "" if file.saved else "* ";
			self.root.title(s+file.filename+" - TIDE v"+__main__.__version__);
			self.statusbar.encoding["text"] = file.encoding.replace("_", " ").upper();
		else:
			self.root.title("Untitled Python Script - TIDE v"+__main__.__version__);
		
		self._createTextarea(file);
		self.textarea.see("insert");
	
	def updateLnCol(self):
		l, c = self.textarea.index("insert").split(".");
		self.statusbar.insertpos["text"] = "Ln %d, Col %d" % (int(l), int(c));
	
	def checkSaved(self, file=None):
		if file == None: file = self.activeFile;

		if not file.saved:
			for tab in self.tabsContainer.tabs:
				if tab.number == self.files.index(file):
					self.tabsContainer.canvas.itemconfigure(tab.tabTitle, text=tab._getTitle("*"+tab.title));
					break;
			
			if file.filename:
				self.root.title("* "+file.filename+" - TIDE v"+__main__.__version__);
			else:
				self.root.title("* Untitled Python Script - TIDE v"+__main__.__version__);
	
	def updateTheme(self):
		colorizer = self.percolator.top;
		colorizer.LoadTagDefs();
		colorizer.config_colors();
		colorizer.notify_range("1.0", "end");
		
		currentTheme = config.get("editor", "theme");

		textStyles = theme.get(currentTheme, "text").split(" ");
		selStyles = theme.get(currentTheme, "selected").split(" ");
		self.textarea.configure(background=textStyles[0], foreground=textStyles[1], selectbackground=selStyles[0], selectforeground=selStyles[1], insertbackground=textStyles[1]);
		self.textarea.tag_configure("highlight", background=selStyles[0], foreground=selStyles[1]);
		self.tabsContainer.updateTheme();
		self.linenumbers.updateTheme(self.textarea);
	
	def updateTabWidth(self):
		tab = " " * int(config.get("editor", "tab"));
		px = self.textarea.tk.call("font", "measure", self.textarea["font"], "-displayof", self.textarea.master, tab);
		self.textarea.configure(tabs=px);
	
	def updateWrap(self):
		config.set("view", "wrap", str(not (config.get("view", "wrap") == "true")).lower());
		wrapping = config.get("view", "wrap") == "true";
		if wrapping:
			self.textarea["wrap"] = "word";
			self.scrollX.grid_remove();
		else:
			self.textarea["wrap"] = "none";
			self.scrollX.grid();
		
		self.linenumbers.updateNumbers(self.textarea);
		self.root.event_generate("<<UpdateWrapMenu>>");
	
	def close(self, num=None):
		if num == None:
			num = self.files.index(self.activeFile);
		
		file = self.files[num];
		if len(self.insertPositions) > 0:
			self.insertPositions.pop(num);

		if not file.saved:
			if not messagebox.askyesno("File Not Saved", "The file is not saved! Are you sure you want to close?", icon="warning", parent=self.root, default=messagebox.NO):
				return False;
		
		file.close();
		
		self.files.pop(num);
		for tab in self.tabsContainer.tabs:
			if tab.number > num:
				tab.number -= 1;
			elif tab.number == num:
				t = tab;
		
		idx = self.tabsContainer.tabs.index(t);
		isActive = t.active;
		self.tabsContainer.close(t);
		self.tabsContainer.repositionTabs();
		
		if isActive:
			if len(self.tabsContainer.tabs) > idx:
				self.tabsContainer.tabs[idx].activate();
			elif idx-1 > -1:
				self.tabsContainer.tabs[idx-1].activate();
		
		if len(self.tabsContainer.tabs) == 0:
			self.textarea.destroy();
			self.scrollY.grid_remove();
			self.scrollX.grid_remove();
			self.linenumbers.delete("number");
			disable = ("Undo", "Redo", "Select All", "Paste", "Go to Line", "Find", "Find in Files", "Replace", "Comment Code", "Uncomment Code", "Cut", "Copy", "Delete", "Indent Region", "Outdent Region", "Class Browser", "Path Browser", "Save", "Save As", "Close");
			for item in disable:
				self.root.event_generate("<<"+item+" Disable>>");
		
		return True;
	
	def toggleLineNumbers(self):
		if config.get("editor", "numbers") == "true":
			self.linenumbers.gutter.grid();
		else:
			self.linenumbers.gutter.grid_remove();
	
	def updateFont(self):
		self.textarea["font"] = (config.get("editor", "font"), config.get("editor", "size"), config.get("editor", "weight"));
		self.linenumbers.updateFont(self.textarea);
		self.updateTheme();
		self.updateTabWidth();
	
