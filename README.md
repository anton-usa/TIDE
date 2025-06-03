# TIDE Help

## About
TIDE \(Tkinter Integrated Development Environment) was inspired by IDLE, python's "official" IDE. It follows the principle of strictly using *only* standard python packages. This means the `tkinter` module is used to build the GUI of the IDE.

TIDE is still in active development and will be coming with more features soon. Currently, an integrated shell is currently in the works, with plans to eventually add a debugger as well.

## How To Run
If you've discovered this `README.md`, but haven't yet discovered how to open the program, this is for you. First, install Python from [python.org](https://python.org/download), then run the file `tide` \(for Linux users) or `tide.bat` \(for Windows users)

## Menus

### File Menu

* New File (Ctrl+N)
	Creates an untitled python script that needs to be
	saved

* Open File (Ctrl+O)
	A window appears that allows you to select a
	python file and open it in the editor

* Open Module (Ctrl+M)
	A window appears that allows you to type in a
	module that is located in sys.path of the current
	viewing file

* Recent Files
	Shows the 10 most recent files that have been
	saved/opened

* Save (Ctrl+S)
	Saves the current viewing file. If the file already
	has a name, it will save it in that name. Otherwise
	a name will have to be provided.

* Save As (Ctrl+Shift+S)
	Saves the current viewing file. Will ask for a name
	regardless if the file is already saved or not

* Close (Ctrl+W)
	Closes the current viewing file, will ask before
	closing if the file isn't saved

* Quit (Ctrl+Q)
	Closes the whole program, will ask before closing
	if there is a file that isn't saved

### Edit
* Undo (Ctrl+Z)
	Go back in editing history for the current viewing
	file

* Redo (Ctrl+Shift+Z)
	Go forward in editing history for the current
	viewing file

* Select All (Ctrl+A)
	Will select all of the text in the current viewing
	file

* Cut (Ctrl+X)
	Will cut the currently selected text to the
	clipboard

* Copy (Ctrl+C)
	Will copy the currently selected text to the
	clipboard

* Paste (Ctrl+V)
	Will paste from the clipboard to where the text
	cursor is currently positioned

* Delete (Del)
	Will erase the currently selected text

* Go to Line (Ctrl+L)
	Will jump to a specified line in the code

* Find (Ctrl+F)
	Will highlight all text that matches a
	specified search pattern

* Replace (Ctrl+H)
	Will find and replace either one or all text
	that matches a specified search pattern with
	a replacement string

* Toggle Comment Code (Ctrl+3)
	Will uncomment/comment the current line or
	selected lines

* Indent Region (Tab)
	Will indent all selected lines

* Outdent Region (Shift+Tab)
	Will outdent the current line or all
	selected lines

### View
* Full Screen (F11)
	Will make the editor full screen and unfull
	screen

* Text Wrapping (F8)
	Will enable/disable text wrapping

* Configuration
	Will open the IDE configuration window

### Documents
* Previous File (Ctrl+PgUp)
	Will open the tab that is located to the
	left of the currently opened tab

* Next File (Ctrl+PgDn)
	Will open the tab that is located to the
	right of the currently opened tab

* First File (Ctrl+Home)
	Will open the left most tab

* Last File (Ctrl+End)
	Will open the right most tab

### Plugins
* All Plugins
	Will open the plugins menu that shows all of
	the plugins that are currently installed

* Install Plugin
	Will allow you to select a zip file that
	contains a plugin that is meant for the IDE

* Run Plugin
	Will show a list of plugins that require you
	to manually run it

### Help
* About
	Will show more information about the IDE

* Help (F1)
	Will show this help window that allows you
	to read the README.md files for this IDE and
	all plugins

* Python Tutorial
	Will open the tutorial found in the python
	documentation website for your specific
	python version found at:
	`http://docs.python.org/[version]/tutorial`

* Python Docs (F2)
	Will open the documentation website for your
	specific python version found at:
	`http://docs.python.org/[version]`

* Tkinter Tutorial
	Will open a tutorial for learning tkinter
	the website is [tkdocs.com](http://tkdocs.com/tutorial/index.html)

* Tkinter Docs
	Will open an API refrence from the website
	[tkdocs.com](http://tkdocs.com/pyref/index.html)

## Configuration
Under the view menu, is a configuration opeion.
This opens a window that allows you to change many
different settings in the IDE. Here is a list of
all the things you can change

### General
Contains these settings:
	* Change tab width
	* Use spaces for tabs
	* Save the file every n seconds
	* Save a backup copy every time you save
	* Display the line numbers

### Font
* Contains these settings:
	* Change font family
	* Change font size
	* Toggle bold text

### Editor Theme
* Contains these settings:
	* Change theme
	* Create custom theme
	* Remove themes
	* Install ready made themes

#### Creating custom themes
* Click on the components in the mini-editor
    to select which component you want to
    customize
* Click on the "Color" button to change the
    text color of the component
* Click on the "Background" button to change
    the background color of the component
* You can also select the font style to be:
	* Normal
	* Italic
	* Bold
	
#### Creating installable themes
* Create the theme in the theme editor
* Go to the file location of the
    program
* Go to config/themes.ini
* Find your theme section
* Copy everything in the section, but not
    the section title
* Paste the contents in a .ini file

### System Theme
You can change the general look and feel of the program with pre-installed OS themes

Running the command `pip install ttkthemes` will add more system themes that are available through this package. If that doesn't work, try running `py -m pip install ttkthemes` for Windows, or `python3 -m pip install ttkthemes` for Mac and Linux

## Plugins
### Default plugins
The IDE does come with some default plugins, they are:

* Bracket Match
* Word Completion (Ctrl+Space)
* File Browser
* And more!

You can read their `README.md` files to know how to use them


### How to create a plugin
Your plugin must have these 3 files:
* \_\_init\_\_.py
* manifest.json
* README.md

**These files must be put in a .zip archive to be installable**

The `__init__.py` file must contain these 3 functions:
* start([window])
	This function is executed when the IDE starts
	or is enabled
* main([window])
	This function is executed when the user
	manually runs it in the plugins menu
* end([window])
	This function is executed when the plugin is
	disabled or uninstalled

The `manifest.json` file must contain have:
* "name": "[The name of the plugin]"
	This is the name of the plugin that will be
	displayed to the user
	
* "description": "[Description of the plugin]"
	This is a small description of the plugin that
	will be displayed to the user
	
* "menu": [boolean]
	will add the plugin to the "Run Plugin" menu
	if set to true

* "disabled": [boolean]
	will disable the plugin if set to true

The `manifest.json` file may also contain:
* "img": "[path to image file]"
	An icon that will be shown to the user in the
	plugins window. Only .gif and .png allowed.
	Please use a 48px × 48px image for best display
	**Note:** .png isn't supported by Tk version older
			  than 8.6

* "shortcut": "[shortcut text]"
	Will display a keyboard shortcut text in the
	"Run Plugin" menu if the plugin is added there
	**The shortcut must be implemented by you**

The `README.md` file is shown in this help menu. It doesn't have to contain anything, but if you want the user to know how to use the plugin, it is encouraged to place all instructions in this file
