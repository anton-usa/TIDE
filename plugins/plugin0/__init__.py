import re;

keyreleaseId = None;
focusoutId = None;
focusinId = None;
buttonId = None;

def find(char, matchTo, idx, direction, textarea):
	allText = textarea.get("1.0", "end");
	previousText = textarea.get("1.0", idx);
	nextText = textarea.get(idx, "end");
	text = previousText if direction == -1 else nextText;
	reducedText = re.sub(r"[\w\s!@#$%^&*\-_+=\\|;':\",./?]", "", text);
	if len(reducedText) > 10000: return;
	
	pos = len(reducedText)-1 if direction == -1 else 1;
	innersFound = 0;
	while (pos < len(reducedText) and direction == 1) or (pos > -1 and direction == -1):
		cur = reducedText[pos];
		if cur == char:
			innersFound += 1;
		elif cur == matchTo[char] and innersFound > 0:
			innersFound -= 1;
		elif cur == matchTo[char]:
			othersFound = 0;
			pos2 = pos;
			while (pos2 < len(reducedText) and direction == 1) or (pos2 > -1 and direction == -1):
				if reducedText[pos2] == matchTo[char]:
					othersFound += 1;

				pos2 += direction;
			
			matchPos = len(allText) if direction == 1 else -1;
			for i in range(othersFound):
				if direction == 1:
					matchPos = allText.rfind(matchTo[char], 0, matchPos);
				else:
					matchPos = allText.find(matchTo[char], matchPos+1);
			
			textarea.tag_add("bracket_match", idx);
			textarea.tag_add("bracket_match", "1.0 + "+str(matchPos)+" char");
			
			break;

		pos += direction;
	
def findMatchingBracket(window):
	textarea = window.editor.textarea;
	
	textarea.tag_configure("bracket_match", underline=1);
	textarea.tag_lower("bracket_match", "sel");
	textarea.tag_lower("bracket_match", "FOUND");
	
	textarea.tag_remove("bracket_match", "1.0", "end");
	matchablesOpen = {"(": ")", "[": "]", "{": "}", "<": ">"};
	matchablesClose = {")": "(", "]": "[", "}": "{", ">": "<"};
	touchingLeft = textarea.get("insert - 1 char");
	touchingRight = textarea.get("insert");
	
	if touchingLeft in matchablesOpen:
		find(touchingLeft, matchablesOpen, "insert - 1 char", 1, textarea);
	elif touchingRight in matchablesOpen:
		find(touchingRight, matchablesOpen, "insert", 1, textarea);
	elif touchingLeft in matchablesClose:
		find(touchingLeft, matchablesClose, "insert - 1 char", -1, textarea);
	elif touchingRight in matchablesClose:
		find(touchingRight, matchablesClose, "insert", -1, textarea);

def start(window):
	global keyreleaseId, focusoutId, buttonId, focusinId;
	
	keyreleaseId = window.editor.bind("<KeyRelease>", lambda e: findMatchingBracket(window), True);
	buttonId = window.editor.bind("<ButtonRelease>", lambda e: findMatchingBracket(window), True);
	focusinId = window.editor.bind("<ButtonRelease>", lambda e: findMatchingBracket(window), True);
	focusoutId = window.editor.bind("<FocusOut>", lambda e: window.editor.textarea.tag_remove("bracket_match", "1.0", "end"), True);

def end(window):
	global keyreleaseId, focusoutId, focusinId, buttonId;
	
	window.editor.unbind("<KeyRelease>", keyreleaseId);
	window.editor.unbind("<FocusOut>", focusoutId);
	window.editor.unbind("<FocusIn>", focusinId);
	window.editor.unbind("<ButtonRelease>", buttonId);
	
	keyreleaseId = None;
	focusoutId = None;
	focusinId = None;
	buttonId = None;

def main(window): pass;
