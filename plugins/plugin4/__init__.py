from tkinter import *;
from tkinter import ttk;
from tkinter import font;
import os;
import glob;
path = os.path.expanduser("~");
currentDir = os.path.dirname(__file__);
folderImg = PhotoImage(file=f"{currentDir}/folder.gif");
fileImg = PhotoImage(file=f"{currentDir}/file.gif");

def putInItems(tree, section, path, keepGoing=True):
	folders = [i for i in glob.glob(path+"/*") if os.path.isdir(i)];
	files = sorted(glob.glob(path+"/*.py")+glob.glob(path+"/*.pyw"));

	for folder in folders:
		try:
			tree.insert(section, "end", text=" "+folder[len(path)+1:], iid=folder, image=folderImg);
			if keepGoing:
				putInItems(tree, folder, folder, False);
		except:
			pass;
	
	for file in files:
		try:
			tree.insert(section, "end", text=" "+file[len(path)+1:], image=fileImg, iid=file);
		except:
			pass;

def calcWidthForItems(tree, iid, indent=1):
	f = font.Font(tree, name="TkDefaultFont", exists=True);
	text = tree.item(iid, "text");
	w = f.measure(text);
	return w+(len("\t"*indent+text) - len(text) + 1)*20 + 20;

def showFolder(tree, newPath):
	global path;
	for child in tree.get_children():
		tree.delete(child);
	
	tree.insert("", "end", text=" ../", iid="up", image=folderImg);
	putInItems(tree, "", newPath);
	path = newPath;
	
	f = font.Font(tree, name="TkDefaultFont", exists=True);
	width = f.measure(newPath);
	
	for child in tree.get_children():
		twidth = calcWidthForItems(tree, child);
		if twidth > width:
			width = twidth;
	
	tree.column("#0", minwidth=width);
	tree.heading("#0", text=newPath, anchor=W);

def openItem(tree):
	for child in tree.get_children(tree.focus()):
		if os.path.isdir(child):
			putInItems(tree, child, child, True);

	f = font.Font(tree, name="TkDefaultFont", exists=True);
	p = tree.focus()[len(path):];
	indent = max(p.count("/"), p.count("\\"))+1;
	width = tree.column("#0")["width"];
	
	for child in tree.get_children(tree.focus()):
		twidth = calcWidthForItems(tree, child, indent);
		if twidth > width:
			width = twidth;
	
	tree.column("#0", minwidth=width);


def selectItem(window, tree):
	item = tree.focus();
	if item == "up":
		showFolder(tree, path[:-len(os.path.basename(path))-1]);
	elif os.path.isdir(item):
		showFolder(tree, item);
	else:
		window.editor.openFile([item]);

def start(window):
	panel = window.sidepanel.notebook;
	body = ttk.Frame(panel, padding=5);
	body.columnconfigure(0, weight=1);
	body.rowconfigure(0, weight=1);
	panel.add(body, text="File Manager");
	
	tree = ttk.Treeview(body, selectmode="browse", show="tree headings");
	tree.column("#0", width=0);
	tree.heading("#0", text="Location: "+path, anchor=W);
	tree.bind("<<TreeviewOpen>>", lambda e: openItem(tree));
	tree.bind("<Double-Button-1>", lambda e: selectItem(window, tree));
	tree.grid(column=0, row=0, sticky=(N, S, E, W));
	
	treeYScrollbar = ttk.Scrollbar(body, orient=VERTICAL, command=tree.yview);
	tree["yscrollcommand"] = treeYScrollbar.set;
	treeYScrollbar.grid(column=1,row=0,sticky=(N, S));

	treeXScrollbar = ttk.Scrollbar(body, orient=HORIZONTAL, command=tree.xview);
	tree["xscrollcommand"] = treeXScrollbar.set;
	treeXScrollbar.grid(column=0,row=1,sticky=(W, E));
	
	showFolder(tree, path);

def main(window):
	pass;

def end(window):
	pass;
