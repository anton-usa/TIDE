import keyword;
import builtins;
import re;
from tkinter import *;
from tkinter import ttk;
import time;

bindId = None;
keyreleaseId = None;
initSpace = False;
isOpen = False;
pythonWords = keyword.kwlist + list(builtins.__dict__);
wordStart = None;
downId = None;
upId = None;

def unique(l):
	d = {};
	for e in l:
		d[e] = None;
	
	return d;

def start(window):
	bindId = window.editor.bind("<Control-space>", lambda e: main(window), True);

def end(window):
	window.editor.unbind("<Control-space>", bindId);
	window.editor.unbind("<KeyRelease>", keyreleaseId);
	window.editor.unbind("<Up>", upId);
	window.editor.unbind("<Down>", downId);

def binsearch(l, t):
	start = 0;
	end = len(l);
	t = str(t);
	if t == "": return None;
	
	while start != end:
		mid = (start+end)//2;
		e = str(l[mid]);

		if e.find(t) == 0:
			idx = mid;
			while str(l[idx-1]).find(t) == 0: idx -= 1;
			
			return idx;
		else:
			if e < t:
				if start == mid: break;
				start = mid;
			elif e > t:
				if end == mid: break;
				end = mid;
	
	return None;

def removeTypes(li):
	l = len(li);
	for i in range(l):
		if li[0].isnumeric() or len(li[0]) == 1:
			li.pop(0);
		else:
			li.append(li.pop(0));

def putWord(textarea, curselect, allWords, extraChar=0):
	global wordStart;
	idx = curselect[0] if len(curselect) > 0 else 0;
	selectedWord = allWords[idx];
	textarea.delete(wordStart, wordStart + " wordend + "+str(extraChar)+" char");
	textarea.insert(wordStart, selectedWord);

def getWord(e, window, textarea, frame, allWords, listbox):
	global isOpen, keyreleaseId, initSpace, wordStart, upId, downId;
	curselect = listbox.curselection();
	
	if len(curselect) > 0 and e.keysym == "Tab":
		putWord(textarea, curselect, allWords, 1);
	
	if e.keysym == "Down" or e.keysym == "Up":
		if e.keysym == "Down":
			idx = curselect[0]+1 if len(curselect) > 0 else 0;
			listbox.selection_clear(idx-1);
		else:
			idx = curselect[0]-1 if len(curselect) > 0 else len(allWords)-1;
			listbox.selection_clear(idx+1);

		listbox.selection_set(idx);
		listbox.see(idx);
		putWord(textarea, (idx,), allWords);
		return;

	exception = ("BackSpace", "Control_L", "Control_R", "ISO_Next_Group", "Caps_Lock", "underscore", "Shift_L");
	wordStart = textarea.index("insert - 1 char wordstart");
	word = re.sub(r"\W", "", textarea.get("insert - 1 char wordstart", "insert wordend").strip());
	if len(e.keysym) > 1 and (e.keysym not in exception or (e.keysym == "BackSpace" and word == "")) and not (initSpace and e.keysym == "space"):
		isOpen = False;
		window.editor.unbind("<KeyRelease>", keyreleaseId);
		window.editor.unbind("<Down>", downId);
		window.editor.unbind("<Up>", upId);
		keyreleaseId = None;
		downId = None;
		upId = None;
		frame.destroy();
		return;
	
	initSpace = False;
	idx = binsearch(allWords, word);
	
	if len(curselect) > 0:
		listbox.selection_clear(curselect[0]);

	if idx != None and word != "":
		listbox.selection_set(idx);
		listbox.see(idx);
	
	bbox = textarea.bbox("insert");
	frame.place(x=bbox[0]-textarea["padx"]);

def main(window):
	global isOpen, keyreleaseId, initSpace, downId, upId;
	if isOpen: return;
	isOpen = True;
	initSpace = True;

	textarea = window.editor.textarea;
	inTextWords = re.split(r"\W+", textarea.get("1.0", "end"));
	removeTypes(inTextWords);
	allWords = sorted(unique(pythonWords + inTextWords))[1:];
	
	frame = ttk.Frame(window.root, padding=2);
	textarea.see("insert");
	
	l = StringVar(value=tuple(allWords));
	listbox = Listbox(frame, listvariable=l, height=10, relief="flat", borderwidth=0);
	listbox.bind("<<ListboxSelect>>", lambda e: putWord(textarea, listbox.curselection(), allWords));
	listbox.grid(row=0,column=0);
	
	scroll = ttk.Scrollbar(frame, orient=VERTICAL, command=listbox.yview);
	listbox["yscrollcommand"] = scroll.set;
	scroll.grid(row=0,column=1,sticky=(N, S));
	
	bbox = textarea.bbox("insert");
	yPos = bbox[1]+bbox[3];
	frame.lower();
	frame.place(in_=textarea, x=bbox[0]-textarea["padx"], y=bbox[1]+bbox[3]);
	frame.update_idletasks();
	
	if frame.winfo_rooty() + frame.winfo_height() > window.root.winfo_height():
		frame.place(y=bbox[1] - frame.winfo_height());

	frame.lift();

	
	keyreleaseId = window.editor.bind("<KeyRelease>", lambda e: getWord(e, window, textarea, frame, allWords, listbox), True);
	downId = window.editor.bind("<Down>", lambda e: "break", True);
	upId = window.editor.bind("<Up>", lambda e: "break", True);
	
	return "break";