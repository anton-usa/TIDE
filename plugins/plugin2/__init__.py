import re;

bindId = None;

def start(window):
	bindId = window.editor.bind("<Return>", lambda e: main(window), True);

def main(window):
	textarea = window.editor.textarea;

	lineContent = textarea.get("insert linestart", "insert lineend");
	fromInsertContent = textarea.get("insert", "insert lineend");
	
	charSearch = re.compile(r"[^\t ]");
	lineContentChar = charSearch.search(lineContent); 
	fromInsertChar = charSearch.search(fromInsertContent);
	
	lineContentStart = lineContentChar.span()[0] if lineContentChar else len(lineContent);
	fromInsertStart = fromInsertChar.span()[0] if fromInsertChar else 0;
	
	textarea.insert("insert", "\n"+lineContent[:(lineContentStart-fromInsertStart)]);
	textarea.see("insert");

	return "break";

def end(window):
	window.editor.unbind("<Return", bindId);
