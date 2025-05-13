keypressId = None;
keyreleaseId = None;
buttonreleaseId = None;
focusoutId = None;
focusinId = None;

def start(window):
	global keypressId, focusinId, focusoutId;
	keypressId = window.editor.bind("<KeyPress>", lambda e: addHighlight(window), True);
	keyreleaseId = window.editor.bind("<KeyRelease>", lambda e: addHighlight(window), True);
	buttonreleaseId = window.editor.bind("<ButtonRelease>", lambda e: addHighlight(window), True);
	focusinId = window.editor.bind("<FocusIn>", lambda e: addHighlight(window), True);
	focusoutId = window.editor.bind("<FocusOut>", lambda e: window.editor.textarea.tag_remove("highlight-line", "1.0", "end"), True);

def getBackground(color):
	red = eval("0x"+color[1:3])/255;
	green = eval("0x"+color[3:5])/255;
	blue = eval("0x"+color[5:])/255;
	lightness = (min(red, green, blue) + max(red, green, blue))/2;
	num = 0.075;
	amount = -num if lightness >= 0.5 else num;
	
	return "#"+hex(int((red+amount)*255))[2:]+hex(int((green+amount)*255))[2:]+hex(int((blue+amount)*255))[2:];

def addHighlight(window):
	textarea = window.editor.textarea;
	
	textarea.tag_remove("highlight-line", "1.0", "end");
	textarea.tag_add("highlight-line", "insert linestart", "insert lineend + 1 char");
	b = getBackground(textarea["background"]);
	textarea.tag_configure("highlight-line", background=b);
	textarea.tag_raise("highlight-line");
	textarea.tag_lower("highlight-line", "sel");


def main(window):
	pass;

def end(window):
	pass;
