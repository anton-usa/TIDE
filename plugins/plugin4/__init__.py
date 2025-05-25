from tkinter import *;
from tkinter import ttk;
from tkinter import font;
from tkinter import messagebox;
import os;
import glob;
import sys;
import re;
import shutil;
path = os.path.expanduser("~");
currentDir = os.path.dirname(__file__);
folderImg = PhotoImage(file=f"{currentDir}/folder.gif");
fileImg = PhotoImage(file=f"{currentDir}/file.gif");

def putInItems(tree, section, path, keepGoing=True):
	folders = [i for i in glob.glob(path+"/*") if os.path.isdir(i)];
	files = sorted(glob.glob(path+"/*.py")+glob.glob(path+"/*.pyw"));

	for folder in folders:
		try:
			tree.insert(section, "end", text=" "+folder[len(path)+1:], iid=folder, image=folderImg, open=False);
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
	elif os.path.isfile(item):
		window.editor.openFile([item]);

def getItem(tree, px, py, item=""):
	for child in tree.get_children(item):
		if tree.bbox(child) == None or len(tree.bbox(child)) == 0: continue;
		
		x, y, w, h = tree.bbox(child);
		if x <= px and x+w >= px and y <= py and y+h >= py:
			return child;
		
		if len(tree.get_children(child)) > 0:
			item = getItem(tree, px, py, child);
			if item:
				return item;
	
	return False;

createWindowStringVar = StringVar(value="");
def createWindow(window, title, label, btnLabel, callback, entryText=""):
	def quit():
		w.grab_release();
		w.destroy();
	
	def showError(text):
		def r():
			try: err.grid_remove();
			except: pass;
		
		err["text"] = text;
		err.grid();
		root.after(min(len(text)*250, 10000), r);
	
	root = window.root;
	w = Toplevel(root);
	w.title(title);
	w.protocol("WM_DELETE_WINDOW", quit);
	w.transient(root);
	w.wait_visibility();
	w.grab_set();
	w.resizable(False, False);
	w.rowconfigure(0, weight=1);
	w.columnconfigure(0, weight=1);
	w.bind("<Control-w>", lambda e: quit());
	
	body = ttk.Frame(w, padding=5);
	body.grid(row=0,column=0,sticky=(N, E, S, W));
	
	ttk.Label(body, text=label).grid(row=0, column=0, sticky=W);
	
	err = ttk.Label(body, text="Error:", foreground="#ff0000");
	err.grid(row=1, column=0, sticky=W);
	err.grid_remove();
	
	createWindowStringVar.set(entryText);
	name = ttk.Entry(body, textvariable=createWindowStringVar);
	name.bind("<Return>", lambda e: ok.invoke());
	name.grid(row=2,column=0,sticky=(W, E),pady=10);
	name.focus_set();
	
	btnGroup = ttk.Frame(body);
	btnGroup.grid(row=3,column=0);
	
	ok = ttk.Button(btnGroup, text=btnLabel, command=lambda: callback(name.get(), showError, quit));
	ok.grid(row=0,column=0,padx=2);
	
	cancel = ttk.Button(btnGroup, text="Cancel", command=quit);
	cancel.grid(row=0,column=1,padx=2);

def create(window, tree, item, what):
	def ok(text, error, quit):
		try:
			section = item if item != path else "";
			if what == "folder":
				os.mkdir(item+"/"+text);
				tree.insert(section, "end", text=text, iid=item+"/"+text, image=folderImg);
			else:
				f = open(item+"/"+text, "w");
				f.close();
				tree.insert(section, "end", text=text, iid=item+"/"+text, image=fileImg);
				tree.item(section, open=True);
			
			quit();
		except FileExistsError:
			error(what.title()+" already exists");
		except Exception as e:
			error(re.sub("(\[.*\])|(\: \'.*\')", "", str(e)).strip());
	
	createWindow(window, "Create new "+what, f"Type in the name of your {what}:", "Create", ok);

def rename(window, tree, item, what):
	def ok(text, error, quit):
		try:
			parentFolder = os.path.dirname(item);
			section = parentFolder if parentFolder != path else "";
			newName = parentFolder+"/"+text;
			os.replace(item, newName);
			tree.insert(section, tree.index(item), iid=newName, text=" "+text, image=folderImg if what == "folder" else fileImg);
			tree.delete(item);
			quit();
		except FileExistsError:
			error(what.title()+" already exists");
		except Exception as e:
			error(re.sub("(\[.*\])|(\: \'.*\')", "", str(e)).strip());
	
	createWindow(window, "Rename "+what, f"Type in new the name of your {what}:", "Rename", ok, os.path.basename(item));

def delete(window, tree, item, what):
	if messagebox.askyesno(title="Delete "+what, message=f"Are you sure you want to delete {item}?"):
		try:
			if what == "folder":
				shutil.rmtree(item);
			else:
				os.remove(item);
			
			tree.delete(item);
		except Exception as e:
			messagebox.showerror(title="Cannot Delete", message=re.sub("(\[.*\])|(\: \'.*\')", "", str(e)).strip());

def rightClickMenu(window, tree, event):
	treeX = tree.winfo_rootx();
	treeY = tree.winfo_rooty();1
	x = event.x_root;
	y = event.y_root;
	item = getItem(tree, x-treeX, y-treeY);
	
	if item != "up" and item:
		tree.focus(item);
		tree.selection_set(item);

		itemType = "file" if os.path.isfile(item) else "folder";
		menu = Menu(window.root);
		
		if itemType == "folder":
			menu.add_command(label="Create folder", command=lambda i=item: create(window, tree, i, "folder"));
			menu.add_command(label="Create file", command=lambda i=item: create(window, tree, i, "file"));

		menu.add_command(label="Rename "+itemType, command=lambda i=item, t=itemType: rename(window, tree, i, t));
		menu.add_command(label="Delete "+itemType, command=lambda i=item, t=itemType: delete(window, tree, i, t));
		menu.post(x, y);
	elif item == False:
		menu = Menu(window.root);
		menu.add_command(label="Create folder", command=lambda i=path: create(window, tree, i, "folder"));
		menu.add_command(label="Create file", command=lambda i=path: create(window, tree, i, "file"));
		menu.post(x, y);
	
def start(window):
	panel = window.sidepanel.notebook;
	body = ttk.Frame(panel, padding=5);
	body.columnconfigure(0, weight=1);
	body.rowconfigure(1, weight=1);
	panel.add(body, text="File Manager");
	
	refresh = ttk.Button(body, text="⟳ Refresh", command=lambda: showFolder(tree, path));
	refresh.grid(row=0,column=0,columnspan=2,sticky=(W, E));
	
	tree = ttk.Treeview(body, selectmode="browse", show="tree headings");
	tree.column("#0", width=0);
	tree.heading("#0", text="Location: "+path, anchor=W);
	tree.bind("<<TreeviewOpen>>", lambda e: openItem(tree));
	tree.bind("<Double-Button-1>", lambda e: selectItem(window, tree));
	
	if sys.platform == "darwin":
		tree.bind("<2>", lambda e: rightClickMenu(window, tree, e));
		tree.bind("<Control-1>", lambda e: rightClickMenu(window, tree, e));
	else:
		tree.bind("<3>", lambda e: rightClickMenu(window, tree, e));
	
	tree.grid(column=0, row=1, sticky=(N, S, E, W));
	
	treeYScrollbar = ttk.Scrollbar(body, orient=VERTICAL, command=tree.yview);
	tree["yscrollcommand"] = treeYScrollbar.set;
	treeYScrollbar.grid(column=1,row=1,sticky=(N, S));

	treeXScrollbar = ttk.Scrollbar(body, orient=HORIZONTAL, command=tree.xview);
	tree["xscrollcommand"] = treeXScrollbar.set;
	treeXScrollbar.grid(column=0,row=2,sticky=(W, E));
	
	showFolder(tree, path);

def main(window):
	pass;

def end(window):
	pass;
