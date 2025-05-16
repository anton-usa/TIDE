"""
This module parses and styles markdown (.md) files

The parser follows this output:
	[
		["[type of text]", "[section of md text without the md symbols]"]
	]

Types of text:
	h#			-	Header [number]								-	#...
	text		-	Plain text									-	...
	code		-	single lined code text						-	`...`
	multi-code	-	multi lined code text						-	```...```
	bold		-	bolded text									-	**...**
	italic		-	italic text									-	*...*
	link-text	-	grouped link-text							-	(...)
	link		-	URL link									-	[...]
	hr			-	horizontal line								-	---
	dhr			-	double horizontal line						-	===
	# blist		-	[tab number] bullet list					-	* ...
	# # nlist	-	[tab number] [list number] numbered list	-	1. ...

Currently it can style for these applications:
	* tkinter Text widget
"""

import re;
import webbrowser;
import __main__;
import tkinter.ttk as ttk;

# TODO: make lists allow the "embeded" styles
def parse(markdown, spaceTab="    "):
	"""Parse the markdown text"""
	
	def numCharInBeginning(line, char):
		i = 0;
		while line[i] == char: i += 1;
		
		return i;
	
	def parseInlineText(i, chars, line):
		endOfStyleText = line.find(chars, i+len(chars));
		text = line[i+len(chars):endOfStyleText];
		i = endOfStyleText + len(chars);
		
		return i, text;
	
	def removeEmptyTexts():
		count = result.count(["text", ""]);
		for _ in range(count):
			result.remove(["text", ""]);
	
	# A quick fix for escaped underscores in bullet points
	lines = markdown.replace("\\_", "_").split("\n");
	result = [];
	textSoFar = "";
	quotesOpen = False;
	
	for line in lines:
		if line == "" and not quotesOpen:
			# parse new line
			result.append(["text", textSoFar+"\n"]);
			textSoFar = "";
		elif len(line) > 0 and line[0] == "#" and not quotesOpen:
			result.append(["text", textSoFar]);
			textSoFar = "";
			
			# parse for header
			num = numCharInBeginning(line, "#");
			result.append(["h"+str(num), line[num:]+"\n"]);
		elif line.strip() == "---" and not quotesOpen:
			result.append(["text", textSoFar]);
			textSoFar = "";
			
			# parse horizontal line
			result.append(["hr", "\n"]);
			result.append(["text", textSoFar]);
			textSoFar = "";
			
		elif line.strip() == "===" and not quotesOpen:
			result.append(["text", textSoFar]);
			textSoFar = "";
			
			# parse double horizontal line
			result.append(["dhr", "\n"]);
		elif line.strip()[0:2] == "* " and not quotesOpen:
			result.append(["text", textSoFar]);
			textSoFar = "";
			
			# parse bullet list
			cleanLine = line.replace(spaceTab, "\t");
			num = numCharInBeginning(cleanLine, "\t");
			result.append([str(num)+" blist", cleanLine[num+2:]+"\n"]);
		elif re.match(r"[0-9]+\. ", line.strip()) and not quotesOpen:
			result.append(["text", textSoFar]);
			textSoFar = "";
			
			# parse bullet list
			cleanLine = line.replace(spaceTab, "\t");
			num = numCharInBeginning(cleanLine, "\t");
			spaceIdx = cleanLine.find(" ");
			result.append([str(num)+" "+cleanLine[:spaceIdx-1]+" nlist", cleanLine[num+spaceIdx+1:]+"\n"]);
		else:
			# parse bold, italic, code, link text, link, text
			i = 0;
			while i < len(line):
				curChar = line[i];
				nextChar = line[i+1] if i+1 < len(line) else None;
				thirdChar = line[i+2] if i+2 < len(line) else None;
				
				if curChar == "*" and nextChar == "*" and line.find("**", i+2) > -1 and not quotesOpen:
					result.append(["text", textSoFar]);
					textSoFar = "";
					
					# parse bold
					i, text = parseInlineText(i, "**", line);
					result.append(["bold", text]);
				elif curChar == "*" and nextChar != "*" and line.find("*", i+1) > -1 and not quotesOpen:
					result.append(["text", textSoFar]);
					textSoFar = "";
					
					# parse italic
					i, text = parseInlineText(i, "*", line);
					result.append(["italic", text]);
				elif curChar == "`" and nextChar == "`" and thirdChar == "`":
					# parse multi-line quotes
					if quotesOpen:
						result.append(["multi-code", textSoFar]);
						textSoFar = "";
						quotesOpen = False;
					else:
						result.append(["text", textSoFar]);
						textSoFar = "";
						quotesOpen = True;
					
					i += 3;
				elif curChar == "`" and nextChar != "`" and line.find("`", i+1) > -1 and not quotesOpen:
					result.append(["text", textSoFar]);
					textSoFar = "";
					
					# parse quote
					i, text = parseInlineText(i, "`", line);
					result.append(["code", text]);
				elif curChar == "(" and line.find(")", i+1) > -1 and line[i-1] != "\\" and not quotesOpen:
					result.append(["text", textSoFar]);
					textSoFar = "";
					
					# parse link
					i, text = parseInlineText(i, ")", line);
					result.append(["link", text]);
				elif curChar == "[" and line.find("]", i+1) > -1 and line[i-1] != "\\" and not quotesOpen:
					result.append(["text", textSoFar]);
					textSoFar = "";
					
					# parse link text
					i, text = parseInlineText(i, "]", line);
					result.append(["link-text", text]);
				else:
					textSoFar += curChar if curChar != "\\" or (line[i-1] == "\\" and curChar == "\\") else "";
					i += 1;
			
			
			textSoFar += "\n";
	
	result.append(["text", textSoFar]);
	removeEmptyTexts();

	return result;

def tkText(textWidget, markdown):
	"""Style the md text for tkinter Text widget"""
	
	# you can edit the styles here...
	textWidget.tag_configure("text", font="TkDefaultFont 11");
	textWidget.tag_configure("h1", font="TkHeadingFont 30 bold");
	textWidget.tag_configure("h2", font="TkHeadingFont 25 bold");
	textWidget.tag_configure("h3", font="TkHeadingFont 18 bold");
	textWidget.tag_configure("h4", font="TkHeadingFont 15 bold");
	textWidget.tag_configure("h5", font="TkHeadingFont 12 bold");
	textWidget.tag_configure("h6", font="TkHeadingFont 10 bold");
	textWidget.tag_configure("code", font="TkFixedFont 10", offset=0.5, foreground="#ff0000", background="#dddddd");
	textWidget.tag_configure("multi-code", font="TkFixedFont 10", offset=0.5, foreground="#ff0000", background="#dddddd");
	textWidget.tag_configure("bold", font="TkDefaultFont 11 bold");
	textWidget.tag_configure("italic", font="TkDefaultFont 11 italic");
	textWidget.tag_configure("blist", font="TkDefaultFont 11", wrap="none");
	textWidget.tag_configure("nlist", font="TkDefaultFont 11", wrap="none");
	textWidget.tag_configure("number", font="TkDefaultFont 10 bold", offset=0.5);
	textWidget.tag_configure("hr", font="TkFixedFont");
	textWidget.tag_configure("dhr", font="TkFixedFont");
	textWidget.tag_configure("link-text", font="TkDefaultFont 11 underline", foreground="#0000ff");
	
	# where the text is added
	def setCursor(cursor):
		textWidget["cursor"] = cursor;
		
	skip = False;
	parsed = parse(markdown);
	headingLines = [];
	for section, i in zip(parsed, range(len(parsed))):
		if skip:
			skip = False;
			continue;
		
		info = section[0].split(" ");
		tabs = 0 if len(info) < 2 else int(info[0]);
		number = "" if len(info) < 3 else info[1];
		tag = info[-1];
		beginning = "\t"*tabs;
		beginning += "" if number == "" else number + ". ";
		if tag == "blist":
			order = ("•", "⚬", "▪", "▫", "▸", "▹");
			beginning += order[tabs % 6]+" ";
		
		if tag == "hr":
			textWidget.insert("end", "―"*textWidget["width"], tag);
		elif tag == "dhr":
			textWidget.insert("end", "═"*textWidget["width"], tag);
		elif tag == "nlist":
			strlen = len(beginning + section[1]);
			textWidget.insert("end", beginning, ("number", tag));
			textWidget.insert("end", section[1], tag);
		elif tag == "link-text":
			skip = True;
			textWidget.insert("end", section[1], (tag, "link"+str(i)));
			textWidget.tag_bind("link"+str(i), "<1>", lambda e, url=parsed[i+1][1]: webbrowser.open(url));
			textWidget.tag_bind("link"+str(i), "<Enter>", lambda e: setCursor(__main__.CURSOR_POINTER));
			textWidget.tag_bind("link"+str(i), "<Leave>", lambda e: setCursor("xterm"));
		else:
			if len(tag) == 2 and tag[0] == "h":
				headingLines.append(textWidget.index("end-1c"));
				textWidget.insert("end", beginning + section[1], tag);
			else:
				textWidget.insert("end", beginning + section[1], tag);
	
	return headingLines;

if __name__ == "__main__":
	with open("./README.md", "r") as f:
		print(parse(f.read()));
