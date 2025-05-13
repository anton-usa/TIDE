import time;
import re;
import keyword;
import builtins;
import theme;
import config;
from tkinter import *;
from idle.Delegator import Delegator;

def any(name, alternates):
	"Return a named group pattern matching list of alternates."
	return "(?P<%s>" % name + "|".join(alternates) + ")";

def make_pat():
	boolsTuple = ("True", "False", "None", "Ellipsis", "NotImplemented");
	kwords = [w for w in keyword.kwlist if w not in boolsTuple];
	kw = r"\b" + any("KEYWORD", kwords) + r"\b";
	builtinlist = [b for b in dir(builtins) if not b.startswith('_') and b not in keyword.kwlist and re.search("[A-Z]", b) == None];
	builtinlist.append("self");
	
	errorList = [e for e in dir(builtins) if re.search(r"[A-Z]", e) != None];

	builtin = "([^.'\"\\#]\\b|^)" + any("BUILTIN", builtinlist) + r"\b";
	error = r"\b" + any("EXC_ERROR", errorList) + r"\b";
	boolean = r"\b"+any("BOOL", boolsTuple)+r"\b";
	numbers = r"\b"+any("NUMBER", [r"[0-9]*\.[0-9]+|[1-9]+[0-9]*|0x[0-9a-fA-F]*|0"])+r"\b";
	comment = any("COMMENT", [r"#[^\n]*"]);
	sqstring = r"(\b[rRbBfF])?'[^'\\\n]*(\\.[^'\\\n]*)*'?";
	dqstring = r'(\b[rRbBfF])?"[^"\\\n]*(\\.[^"\\\n]*)*"?';
	sq3string = r"(\b[rRbBfF])?'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?";
	dq3string = r'(\b[rRbBfF])?"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?';
	string = any("STRING", [sq3string, dq3string, sqstring, dqstring]);
	
	return "|".join([kw, builtin, comment, string, boolean, numbers, error, any("SYNC", [r"\n"])]);

prog = re.compile(make_pat(), re.S);
idprog = re.compile(r"\s+(\w+)", re.S);
asprog = re.compile(r".*?\b(as)\b");

class ColorDelegator(Delegator):

	def __init__(self):
		Delegator.__init__(self)
		self.prog = prog
		self.idprog = idprog
		self.asprog = asprog
		self.LoadTagDefs()

	def setdelegate(self, delegate):
		if self.delegate is not None:
			self.unbind("<<toggle-auto-coloring>>")
		Delegator.setdelegate(self, delegate)
		if delegate is not None:
			self.config_colors()
			self.bind("<<toggle-auto-coloring>>", self.toggle_colorize_event)
			self.notify_range("1.0", "end")

	def config_colors(self):
		for tag, cnf in self.tagdefs.items():
			if cnf:
				self.tag_configure(tag, **cnf)
		self.tag_raise("sel")

	def LoadTagDefs(self):
		self.tagdefs = {
			"TODO": {"background": None, "foreground": None},
			"SYNC": {"background": None, "foreground": None},
#			"BREAK": {"background": None, "foreground": "#ff0000"},
		};
		tags = (
			("COMMENT", "comment"),
			("BOOL", "bool"),
			("KEYWORD", "keyword"),
			("BUILTIN", "builtin"),
			("STRING", "string"),
			("DEFINITION", "func"),
			("NUMBER", "number"),
			("ERROR", "error"),
			("EXC_ERROR", "exception"),
			("FOUND", "found"),
		);
		
		currentTheme = config.get("editor", "theme");
		for editorTag, themeTag in tags:
			styles = theme.get(currentTheme, themeTag).split(" ");
			
			font = (config.get("editor", "font"), config.get("editor", "size"), styles[2]);
			self.tagdefs[editorTag] = {"background": styles[0], "foreground": styles[1], "font": font};
		

	def insert(self, index, chars, tags=None):
		index = self.index(index)
		self.delegate.insert(index, chars, tags)
		self.notify_range(index, index + "+%dc" % len(chars))

	def delete(self, index1, index2=None):
		index1 = self.index(index1)
		self.delegate.delete(index1, index2)
		self.notify_range(index1)

	after_id = None
	allow_colorizing = True
	colorizing = False

	def notify_range(self, index1, index2=None):
		self.tag_add("TODO", index1, index2);
		if self.after_id: return;
		if self.colorizing: self.stop_colorizing = True;
		if self.allow_colorizing: self.after_id = self.after(1, self.recolorize);

	close_when_done = None # Window to be closed when done colorizing

	def close(self, close_when_done=None):
		if self.after_id:
			after_id = self.after_id;
			self.after_id = None;
			self.after_cancel(after_id);

		self.allow_colorizing = False;
		self.stop_colorizing = True;

		if close_when_done:
			if not self.colorizing:
				close_when_done.destroy();
			else:
				self.close_when_done = close_when_done;

	def toggle_colorize_event(self, event):
		if self.after_id:
			after_id = self.after_id;
			self.after_id = None;
			self.after_cancel(after_id);

		if self.allow_colorizing and self.colorizing:
			self.stop_colorizing = True;

		self.allow_colorizing = not self.allow_colorizing;
		if self.allow_colorizing and not self.colorizing:
			self.after_id = self.after(1, self.recolorize);
		
		return "break";

	def recolorize(self):
		self.after_id = None;

		if not self.delegate: return;
		if not self.allow_colorizing: return;
		if self.colorizing: return;
		
		try:
			self.stop_colorizing = False;
			self.colorizing = True;
			self.recolorize_main();
		finally:
			self.colorizing = False;

		if self.allow_colorizing and self.tag_nextrange("TODO", "1.0"):
			self.after_id = self.after(1, self.recolorize);
		if self.close_when_done:
			top = self.close_when_done;
			self.close_when_done = None;
			top.destroy();

	def recolorize_main(self):
		next = "1.0";
		while True:
			item = self.tag_nextrange("TODO", next);
			if not item: break
			
			head, tail = item;
			self.tag_remove("SYNC", head, tail);
			item = self.tag_prevrange("SYNC", head);
			if item:
				head = item[1];
			else:
				head = "1.0";

			chars = "";
			next = head;
			lines_to_get = 1;
			ok = False;
			while not ok:
				mark = next;
				next = self.index(mark + "+%d lines linestart" % lines_to_get);
				lines_to_get = min(lines_to_get * 2, 100);
				ok = "SYNC" in self.tag_names(next + "-1c");
				line = self.get(mark, next);
				##print head, "get", mark, next, "->", repr(line)
				if not line: return;
				
				for tag in self.tagdefs:
					self.tag_remove(tag, mark, next);

				chars = chars + line;
				m = self.prog.search(chars);
				while m:
					for key, value in m.groupdict().items():
						if value:
							a, b = m.span(key);
							self.tag_add(key, head + "+%dc" % a, head + "+%dc" % b);
							
							if value in ("def", "class"):
								m1 = self.idprog.match(chars, b);
								if m1:
									a, b = m1.span(1);
									self.tag_add("DEFINITION", head + "+%dc" % a, head + "+%dc" % b);
							elif value == "import":
								# color all the "as" words on same line, except
								# if in a comment; cheap approximation to the
								# truth
								if "#" in chars:
									endpos = chars.index("#");
								else:
									endpos = len(chars);

								while True:
									m1 = self.asprog.match(chars, b, endpos);
									if not m1: break
									
									a, b = m1.span(1)
									self.tag_add("KEYWORD", head + "+%dc" % a, head + "+%dc" % b);
					
					m = self.prog.search(chars, m.end());
				
				if "SYNC" in self.tag_names(next + "-1c"):
					head = next;
					chars = "";
				else:
					ok = False;
				
				if not ok:
					# We're in an inconsistent state, and the call to
					# update may tell us to stop.  It may also change
					# the correct value for "next" (since this is a
					# line.col string, not a true mark).  So leave a
					# crumb telling the next invocation to resume here
					# in case update tells us to leave.
					self.tag_add("TODO", next);
				self.update();
				if self.stop_colorizing: return;

	def removecolors(self):
		for tag in self.tagdefs:
			self.tag_remove(tag, "1.0", "end");


