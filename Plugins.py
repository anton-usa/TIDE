"""
This is where much of the plugin stuff happens.
FYI: MenuBar.py lists the plugins that can be run from the menu

Event bindings created here:
	AllPlugins - shows a window that lists all plugins allowing you to remove, disable, see more info
	InstallPlugin - creates a window that allows you to install a plugin
	[module]Start - runs the start(window) for [module]
	[module]Main - runs the main(window) for [module]
	[module]End - runs the end(window) for [module]

Event bindings used that are created elsewhere:
	[module]EDToggle - MenuBar.py
"""
import importlib;
import glob;
import os;
import json;
from tkinter import *;
from tkinter import ttk;
from tkinter import filedialog;
from tkinter import messagebox;
from zipfile import ZipFile;
import time;
from directory import DIRECTORY;
import __main__;
import shutil;

class Plugins:
	def __init__(self, window):
		self.window = window;
		
		# event bindings
		self.window.root.bind("<<InstallPlugin>>", lambda e: self.installPlugin());
		self.window.root.bind("<<AllPlugins>>", lambda e: self.pluginsWindow());
	
	def installPlugin(self):
		"""Installs a plugin that is in a .zip archive"""
		filename = filedialog.askopenfilename(filetypes=[("ZIP Archive", "*.zip")], title="Please select the plugin to install");
		if filename != "":
			with ZipFile(filename, "r") as zipPlugin:
				# install the plugin
				pluginsAmount = len(glob.glob(DIRECTORY+"/plugins/plugin*"));
				os.mkdir(DIRECTORY+"/plugins/plugin"+str(pluginsAmount));
				zipPlugin.extractall(DIRECTORY+"/plugins/plugin"+str(pluginsAmount));

				# TODO: Verify that the plugin has all required components

			if messagebox.askyesno("Plugin Installed", "The plugin has been installed!\nRestart the editor to enable it?", icon="question"):
				__main__.restart(self.window.root);
	
	def pluginsWindow(self):
		root = self.window.root;
		DISABLED_COLOR = "#aaaaaa";
		ENABLED_COLOR = "#000000";
		madeChanges = BooleanVar(value=False);
		
		def toggleEnable(img, name, description, value, plugin, manifest):
			"""Disable and enable plugins"""
			madeChanges.set(True);
			shouldDisable = not bool(value.get());
			module = os.path.basename(plugin);
			
			if shouldDisable:
				# disable plugin
				content.itemconfig(img, state=HIDDEN);
				content.itemconfig(name, state=DISABLED);
				content.itemconfig(description, state=DISABLED);
				root.event_generate("<<"+module+"End>>");
			else:
				# enable plugin
				content.itemconfig(img, state=NORMAL);
				content.itemconfig(name, state=NORMAL);
				content.itemconfig(description, state=NORMAL);
				root.event_generate("<<"+module+"Start>>");

			manifest["disabled"] = shouldDisable;
			manifestStr = json.dumps(manifest);
			root.event_generate("<<"+module+"EDToggle>>");
			with open(plugin+"/manifest.json", "w") as f:
				f.write(manifestStr);
		
		def uninstallPlugin(check, img, name, description, button, plugin, value):
			"""Uninstalls plugins"""
			if messagebox.askyesno("Uninstall Plugin", "Are you sure you want to uninstall the plugin?\nThis action cannot be undone.", icon="warning", parent=window):
				# remove plugin
				shutil.rmtree(plugin);
				
				# disable stuff
				module = os.path.basename(plugin);
				enabled = bool(value.get());
				if enabled: root.event_generate("<<"+module+"EDToggle>>");
				content.itemconfig(img, state=HIDDEN);
				content.itemconfig(name, state=DISABLED);
				content.itemconfig(description, state=DISABLED);
				root.event_generate("<<"+module+"End>>");
				
				# remove some things
				content.delete(check);
				content.delete(button);
				
				madeChanges.set(True);

		def quit(window):
			"""Close the about dialog"""
			destroyed = False;
			if madeChanges.get():
				if messagebox.askyesno("Confirm Changes", "It's a good idea to restart the program to ensure changes.\nRestart program?", icon="question", parent=window):
					window.grab_release();
					window.destroy();
					destroyed = True;
					__main__.restart(root);
			
			if not destroyed:
				window.grab_release();
				window.destroy();
			

		window = Toplevel(root);
		window.title("Plugins Menu");
		window.protocol("WM_DELETE_WINDOW", lambda: quit(window));
		window.transient(root);
		window.wait_visibility();
		window.grab_set();
		window.resizable(False, False);
		window.rowconfigure(0, weight=1);
		window.columnconfigure(0, weight=1);
		window.bind("<Control-w>", lambda e: quit(window));
		
		# Show list of all plugins
		body = ttk.Frame(window, padding=5);
		body.grid(row=0,column=0);
		
		mainFrame = ttk.LabelFrame(body);
		mainFrame["labelwidget"] = ttk.Label(mainFrame, text="Installed Plugins", font="TkDefaultFont 10 bold");
		mainFrame.grid(row=0, column=0);
		
		# everything is being put into a canvas
		content = Canvas(mainFrame, background="#ffffff", borderwidth=0, highlightthickness=0);
		content.grid(row=0,column=0);
		
		scroll = ttk.Scrollbar(mainFrame, orient=VERTICAL, command=content.yview);
		scroll.grid(row=0,column=1,sticky=(N, S));
		content["yscrollcommand"] = scroll.set;
		content.bind("<Button-4>", lambda e: content.yview_scroll(-1, "units"));
		content.bind("<Button-5>", lambda e: content.yview_scroll(1, "units"));
		
		# get all the plugins
		plugins = sorted(glob.glob(DIRECTORY+"/plugins/plugin*"));
		y = 0;
		
		# get all the icons that will be used and put them into
		# a list. For some reason this is the only way to get
		# all of the images to be displayed
		defaultIcon = PhotoImage(file=DIRECTORY+"/icons/plugin.gif");
		icons = [];
		for plugin in plugins:
			if not os.path.isfile(plugin+"/manifest.json"): continue;
			
			with open(plugin+"/manifest.json", "r") as f:
				manifest = json.loads(f.read().strip());
				
				if "img" in manifest:
					icons.append(PhotoImage(file=plugin+"/"+manifest["img"]));
				else:
					icons.append(defaultIcon);
		
		# now put the plugins into the canvas
		padding = 5;
		largestWidth = 0;
		uninstallButtons = [];
		for plugin, icon, i in zip(plugins, icons, range(len(plugins))):
			if not os.path.isfile(plugin+"/manifest.json"): continue;
			
			with open(plugin+"/manifest.json", "r") as f:
				# put the plugin info
				manifest = json.loads(f.read().strip());
				enabled = not manifest["disabled"];
				
				width = 0;
				value = IntVar(value=int(enabled));
				check = ttk.Checkbutton(content, style="White.TCheckbutton", variable=value);
				chkWin = content.create_window(padding, y + 16 - check.winfo_reqheight()/2 + padding, window=check, anchor="nw");
				width += padding+check.winfo_reqwidth();

				img = content.create_image(width+padding, y + padding, image=icon, anchor="nw");
				imgBB = list(content.bbox(img));
				if (imgBB[2] - imgBB[0]) < 48:
					imgBB[2] = imgBB[0] + 48;
				
				if (imgBB[3] - imgBB[1]) < 48:
					imgBB[3] = imgBB[1] + 48;
				
				content.itemconfig(img, state=NORMAL if enabled else HIDDEN);
				width += padding + (imgBB[2] - imgBB[0]);
				
				name = content.create_text(width + padding, y + padding, text=manifest["name"], font="TkHeadingFont 10 bold", anchor="nw", fill=ENABLED_COLOR, disabledfill=DISABLED_COLOR, state=NORMAL if enabled else DISABLED);
				nameBB = content.bbox(name);
				newWidth = width + padding*2 + (nameBB[2] - nameBB[0]);
				
				description = content.create_text(width + padding, y + padding + (nameBB[3] - nameBB[1] + padding), text=manifest["description"], font="TkCaptionFont 9", anchor="nw", fill=ENABLED_COLOR, disabledfill=DISABLED_COLOR, state=NORMAL if enabled else DISABLED);
				descriptionBB = content.bbox(description);
				newWidth2 = width + padding*2 + (descriptionBB[2] - descriptionBB[0]);
				width = max(newWidth, newWidth2);
				
				uninstall = ttk.Button(content, text="Uninstall", width=7);
				btnWin = content.create_window(width+padding, y+padding+2, window=uninstall, anchor="nw");
				uninstallButtons.append((btnWin,width+padding,uninstall.winfo_reqwidth()));
				uninstall["command"] = lambda c=chkWin, i=img, n=name, d=description, p=plugin, b=btnWin, v=value: uninstallPlugin(c, i, n, d, b, p, v);
				uninstall.bind("<Return>", lambda e: uninstall.invoke());
				width += uninstall.winfo_reqwidth() + padding*2;
				
				largestWidth = largestWidth if largestWidth > width else width;
				y += imgBB[3] - imgBB[1] + padding*2;
				check["command"] = lambda i=img, n=name, d=description, v=value, p=plugin, m=manifest: toggleEnable(i, n, d, v, p, m);
			
		if len(plugins) > 0:
			# set the size and scroll region of the canvas
			content["height"] = y if y < 300 else 300;
			content["width"] = largestWidth;
			content["scrollregion"] = (0, 0, 0, y);
			if y < 300:
				scroll.grid_remove();
			else:
				scroll.grid();
		else:
			content["height"] = 100;
			content["width"] = 200;
			content.create_text(100, 0, text="You have no plugins installed", anchor="n");
			scroll.grid_remove();
		
		for btn, x, w in uninstallButtons:
			content.move(btn, int(content["width"]) - (int(x) + int(w) + padding), 0);
		
		# footer
		footer = ttk.Frame(body, padding=5);
		footer.grid(row=1,column=0);
		
		close = ttk.Button(footer, text="Close", command=lambda: quit(window));
		close.bind("<Return>", lambda e: close.invoke());
		close.grid(row=0,column=0);
		
		# center the window on the root
		window.update_idletasks();
		midX = str(int(root.winfo_width()/2 - window.winfo_width()/2 + root.winfo_x()));
		midY = str(int(root.winfo_height()/2 - window.winfo_height()/2 + root.winfo_y()));
		window.geometry(str(window.winfo_width())+"x"+str(window.winfo_height())+"+"+midX+"+"+midY);
		
		# start the window
		window.wait_window();	
		
	def start(self):
		"""
		Run start() for all plugins
		Create a virutal event for running plugins in the menu
		"""
		plugins = glob.glob(DIRECTORY+"/plugins/*");
		for plugin in plugins:
			if not os.path.isfile(plugin+"/manifest.json"): continue;
			with open(plugin+"/manifest.json", "r") as f:
				manifest = json.loads(f.read().strip());
				moduleName = os.path.basename(plugin);
				module = importlib.import_module("plugins."+moduleName);
				self.window.root.bind("<<"+moduleName+"Start>>", lambda e, m=module: m.start(self.window));
				self.window.root.bind("<<"+moduleName+"Main>>", lambda e, m=module: m.main(self.window));
				self.window.root.bind("<<"+moduleName+"End>>", lambda e, m=module: m.end(self.window));
				if not manifest["disabled"]:
					module.start(self.window);

