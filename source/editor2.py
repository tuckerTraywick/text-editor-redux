from blessed import Terminal

# Converts a key + control (ex. "^A") to it's ASCII representation.
def ctrl(char):
	return chr(ord(char.upper()) - 64)

# Handles the logic and main loop for the editor.
class EditorController:
	def __init__(self):
		self.model = EditorModel()
		self.view = EditorView(self.model)

		self.model.document.open("source/example.c")

		terminal = self.view.printer.terminal
		self.model.document.syntax.colors = {
			"keyword": terminal.skyblue,
			"symbol": terminal.indianred,
			"identifier": terminal.snow,
			"number": terminal.mediumpurple,
			"string": terminal.lemonchiffon,
			"lineComment": terminal.palegreen3,
		}
		self.model.document.syntax.keywords = {
			"return", "for", "int", "void", "include",
		}
		self.model.document.syntax.symbols = "`~!@$%^&*()-_=+[{]}\\|;:,<.>/?"
		self.model.document.syntax.lineComment = "#"

	# Starts the main loop for the editor, stops when the user quits
	def run(self):
		terminal = self.view.printer.terminal
		with terminal.fullscreen(), terminal.raw(), terminal.keypad(), terminal.location():
			while self.model.keepRunning:
				self.model.document.height = terminal.height
				self.view.draw()
				key = self.view.getKeypress()
				self.processKeypress(key)

	# Delegates a keypress to the function it's bound to.
	def processKeypress(self, key):
		bindings = self.model.keybindings[self.model.mode]
		if key.name is not None and key.name in bindings:
			bindings[key.name](self, key)
		elif key in bindings:
			bindings[key](self, key)
		elif "else" in bindings:
			bindings["else"](self, key)

	###############################
	#### KEYBINDING FUNCTIONS #####
	###############################
	# Closes the file being edited and stops the editor.
	def quit(self, key):
		self.model.document.close()
		self.model.keepRunning = False

	# Moves the cursor up a line.
	def cursorUpLine(self, key):
		self.model.document.cursorUpLine()
		
	# Moves the cursor down a line.
	def cursorDownLine(self, key):
		self.model.document.cursorDownLine()
		
	# Moves the left a character.
	def cursorLeftCharacter(self, key):
		self.model.document.cursorLeftCharacter()

	# Moves the cursor up a line.
	def cursorRightCharacter(self, key):
		self.model.document.cursorRightCharacter()
		
	# Moves the cursor left a word.
	def cursorLeftWord(self, key):
		self.model.document.cursorLeftWord()
		
	# Moves the cursor right a word.
	def cursorRightWord(self, key):
		self.model.document.cursorRightWord()
		
	# Moves the cursor left a big word.
	def cursorLeftWORD(self, key):
		self.model.document.cursorLeftWORD()
		
	# Moves the cursor right a big word.
	def cursorRightWORD(self, key):
		self.model.document.cursorRightWORD()
		
	# Inserts a character at the cursor.
	def insert(self, key):
		if key.isprintable():
			self.model.document.insert(key)
			
	# Splits the current line at the cursor.
	def splitLine(self, key):
		self.model.document.splitLine()
		
	# Joins the current line with the previous line.
	def joinPreviousLine(self, key):
		self.model.document.joinPreviousLine()
		
	# Deletes a character to the left of the cursor.
	def deleteCharacterLeft(self, key):
		self.model.document.deleteCharacterLeft()

	# Deletes a character to the right of the cursor.
	def deleteCharacterRight(self, key):
		self.model.document.deleteCharacterRight()
		
	# Returns back to normal mode.
	def enterNormalMode(self, key):
		self.model.mode = "normal"
		
	# Enters insert mode.
	def enterInsertMode(self, key):
		self.model.mode = "insert"
		
	# Moves the cursor up one half of the screen.
	def cursorUpPage(self, key):
		self.model.document.cursorUpPage()
		
	# Moves the cursor down one half of the screen.
	def cursorDownPage(self, key):
		self.model.document.cursorDownPage()

	# Moves the cursor up a whole screen.
	def cursorUpPAGE(self, key):
		self.model.document.cursorUpPAGE()
		
	# Moves the cursor down a whole screen.
	def cursorDownPAGE(self, key):
		self.model.document.cursorDownPAGE()


# Stores and manipulates the state of the editor.
class EditorModel:
	def __init__(self):
		self.settings = {
			"relativeLineNumbers": True,
		}
		self.keybindings = {
			"normal": {
				"j": EditorController.cursorLeftCharacter,
				"l": EditorController.cursorRightCharacter,
				"i": EditorController.cursorUpLine,
				"k": EditorController.cursorDownLine,
				"J": EditorController.cursorLeftWord,
				"L": EditorController.cursorRightWord,
				"I": EditorController.cursorUpPage,
				"K": EditorController.cursorDownPage,
				ctrl("j"): EditorController.cursorLeftWORD,
				ctrl("l"): EditorController.cursorRightWORD,
				ctrl("i"): EditorController.cursorUpPAGE,
				ctrl("k"): EditorController.cursorDownPAGE,
				" ": EditorController.enterInsertMode,
				ctrl("c"): EditorController.quit,
				"KEY_UP": EditorController.cursorUpLine,
				"KEY_DOWN": EditorController.cursorDownLine,
				"KEY_LEFT": EditorController.cursorLeftCharacter,
				"KEY_RIGHT": EditorController.cursorRightCharacter,
				# "KEY_ENTER": EditorController.splitLine,
				"KEY_BACKSPACE": EditorController.deleteCharacterLeft,
				"KEY_DELETE": EditorController.deleteCharacterRight,
			},
			"insert": {
				ctrl("c"): EditorController.quit,
				"KEY_ESCAPE": EditorController.enterNormalMode,
				"KEY_UP": EditorController.cursorUpLine,
				"KEY_DOWN": EditorController.cursorDownLine,
				"KEY_LEFT": EditorController.cursorLeftCharacter,
				"KEY_RIGHT": EditorController.cursorRightCharacter,
				"KEY_ENTER": EditorController.splitLine,
				"KEY_BACKSPACE": EditorController.deleteCharacterLeft,
				"KEY_DELETE": EditorController.deleteCharacterRight,
				"else": EditorController.insert,
			},
		}
		self.mode = "normal"
		self.keepRunning = True
		self.document = Document()
		# self.workingDirectory = ""

# Stores and presents the ui of the editor.
class EditorView:
	def __init__(self, model):
		self.model = model
		self.printer = Printer()
		self.statusLineLeft = ""
		self.statusLineRight = ""
		# self.message = ""
		# self.command = None
		# self.findTerm = None
		# self.replaceTerm = None
		# self.browserFileList = None
		self.colors = {
			"statusLine": self.printer.terminal.snow_on_gray25,
			"lineNumber": self.printer.terminal.gray55_on_gray10,
			"currentLineNumber": self.printer.terminal.lightyellow_on_gray15,
			"line": self.printer.terminal.snow_on_gray10,
			"currentLine": self.printer.terminal.snow_on_gray15,
			"normal": self.printer.terminal.snow_on_slateblue3,
			"insert": self.printer.terminal.snow_on_seagreen4,
			# "visual": self.printer.terminal.snow_on_goldenrod4,
			"tabBar": self.printer.terminal.snow_on_gray25,
			"tab": self.printer.terminal.snow_on_gray40,
			"currentTab": self.printer.terminal.snow_on_gray40,
			"hasChanges": self.printer.terminal.brown2,
		}

	# Returns a keypress from the user.
	def getKeypress(self):
		return self.printer.terminal.inkey()
	
	# Draws the tab bar to the screen.
	def drawTabBar(self):
		printer = self.printer
		terminal = self.printer.terminal
		document = self.model.document
		changes = self.colors["hasChanges"]("*") if document.hasChanges else ""
		tab = self.colors["currentTab"](f" {changes}{document.name} ")
		printer.print(terminal.home + self.colors["tabBar"](terminal.ljust(tab)))
	
	# Draws the document to the screen.
	def drawDocument(self):
		scrollY = self.model.document.scrollY
		buffer = self.model.document.buffer
		cursor = self.model.document.cursor
		syntax = self.model.document.syntax
		terminal = self.printer.terminal
		for i in range(scrollY, scrollY + terminal.height - 1):
			if i == cursor.y:
				number = self.colors["currentLineNumber"](f"{i + 1:>{buffer.lineNumberLength}}")
				line = syntax.highlight(buffer.lines[i])
				self.printer.print(self.colors["currentLine"](terminal.ljust(f"{number} {line}")))
			elif i < len(buffer):
				number = self.colors["lineNumber"](f"{i + 1:>{buffer.lineNumberLength}}")
				line = syntax.highlight(buffer.lines[i])
				self.printer.print(self.colors["line"](terminal.ljust(f"{number} {line}")))
			else:
				self.printer.print(self.colors["line"](terminal.ljust("")))

	# Draws the cursor to the screen.
	def drawCursor(self):
		terminal = self.printer.terminal
		cursor = self.model.document.cursor
		scrollY = self.model.document.scrollY
		scrollX = self.model.document.scrollX
		lineNumberLength = self.model.document.buffer.lineNumberLength
		y = cursor.y - scrollY + 1
		x = cursor.x - scrollX + lineNumberLength + 1
		self.printer.print(terminal.home + terminal.move_yx(y, x))

	# Draws the status line to the screen.
	def drawStatusLine(self):
		printer = self.printer
		terminal = self.printer.terminal
		document = self.model.document
		mode = self.colors[self.model.mode](f" {self.model.mode.upper()} ")
		changes = "[+] " if document.hasChanges else ""
		status = f"{changes}{document.name}"
		status = "C | unix"
		printer.print(terminal.home + terminal.move_down(terminal.height))
		printer.print(self.colors["statusLine"](terminal.ljust(f"{mode} {status}")))

	# Draws the model to the screen.
	def draw(self):
		if self.model.mode in ["normal", "insert"]:
			self.drawTabBar()
			self.drawDocument()
			self.drawStatusLine()
			# self.drawCommmandLine()
			self.drawCursor()
		self.printer.flush()

# Represents a syntax highlighting scheme.
class Syntax:
	def __init__(self):
		self.name = "C"
		self.colors = {}
		self.keywords = {}
		self.symbols = ""
		self.string = '"'

	# Applies syntax highlighting to a line.
	def highlight(self, line):
		i = 0
		token = ""
		result = ""

		# Break the line into tokens and append each token to the result with highlighting.
		while i < len(line):
			# Skip spaces.
			if line[i].isspace():
				result += line[i]
				i += 1
			# Highlight an identifier or keyword.
			elif line[i].isalpha() or line[i] == "_":
				# Get the identifier.
				while i < len(line) and (line[i].isalnum() or line[i] == "_"):
					token += line[i]
					i += 1
				
				# If it's a keyword, highlight it as such.
				if token in self.keywords:
					result += self.colors["keyword"](token)
				else:
					result += self.colors["identifier"](token)
				token = ""
			# Highlight a number.
			elif line[i].isdigit():
				while i < len(line) and line[i].isdigit():
					token += line[i]
					i += 1
				result += self.colors["number"](token)
				token = ""
			# Higlight a symbol.
			elif line[i] in self.symbols:
				while i < len(line) and line[i] in self.symbols:
					token += line[i]
					i += 1
				result += self.colors["symbol"](token)
				token = ""
			# Highlight a string.
			elif line[i] == '"':
				token += line[i]
				i += 1

				while True:
					if i >= len(line):
						break
					elif line[i] == '"':
						token += line[i]
						i += 1
						break
					else:
						token += line[i]
						i += 1
				result += self.colors["string"](token)
				token = ""
			# Highlight a line comment.
			elif line[i] == self.lineComment:
				result += self.colors["lineComment"](line[i:])
				break
			# Apply default highlighting.
			else:
				result += line[i]
				i += 1

		return result

# Represents a buffer along with it's cursor. Used to manipulate text.
class Document:
	def __init__(self):
		self.buffer = Buffer()
		self.cursor = Cursor()
		self.syntax = Syntax()
		self.file = None
		self.name = ""
		self.hasChanges = False
		self.scrollY = 0
		self.scrollX = 0
		self.width = 0
		self.height = 0

	# Returns the line the cursor is on.
	@property
	def currentLine(self):
		return self.buffer.lines[self.cursor.y]
	
	# Returns the character under the cursor.
	@property
	def currentCharacter(self):
		if self.cursor.x < len(self.currentLine):
			return self.currentLine[self.cursor.x]
		else:
			return "\n"

	# Opens a file and reads it into the buffer, and resets the cursor.
	def open(self, path):
		self.name = path
		file = open(path, "r+")
		# TODO: Handle failed `open()`.
		self.file = file
		self.buffer.readLines(file)
		self.cursor.reset()
		self.hasChanges = False
		self.scrollY = 0
		self.scrollX = 0

	# Closes the document, and resets its state.
	def close(self):
		self.buffer.reset()
		self.cursor.reset()
		self.file.close()
		self.hasChanges = False
		self.scrollY = 0
		self.scrollX = 0

	# Returns true if the cursor is at the beginning of the buffer.
	def cursorAtBufferBegin(self):
		return self.cursor.y == 0 and self.cursor.x == 0

	# Returns true if the cursor is at the end of the buffer.
	def cursorAtBufferEnd(self):
		return self.cursor.y == len(self.buffer) - 1 and self.cursor.x == len(self.currentLine)

	# Moves the horizontal scroll to accomodate the cursor.
	def adjustHorizontalScroll(self):
		# if self.cursor.x < self.scrollX:
		# 	self.scrollX = self.cursor.x
		# elif self.cursor.x > self.scrollX + self.width - self.buffer.lineNumberLength - 2:
		# 	self.scrollX = self.cursor.x - self.width + self.buffer.lineNumberLength + 2
		pass

	# Moves the cursor to the beginning of the line.
	def cursorLineBegin(self):
		self.cursor.x = 0
		self.adjustHorizontalScroll()

	# Moves the cursor to the end of the line.
	def cursorLineEnd(self):
		self.cursor.x = len(self.currentLine)
		self.adjustHorizontalScroll()

	# Moves the cursor up a line and adjusts the scroll if needed.
	def cursorUpLine(self):
		if self.cursor.y > 0:
			self.cursor.y -= 1
			self.cursor.x = min(self.cursor.x, len(self.currentLine))
			if self.cursor.y < self.scrollY:
				self.scrollY -= 1
		else:
			self.cursor.x = 0
		self.adjustHorizontalScroll()

	# Moves the cursor down a line and adjusts the scroll if needed.
	def cursorDownLine(self):
		if self.cursor.y < len(self.buffer) - 1:
			self.cursor.y += 1
			self.cursor.x = min(self.cursor.x, len(self.currentLine))
			if self.cursor.y > self.scrollY + self.height - 2:
				self.scrollY += 1
		elif self.cursor.x != len(self.currentLine):
			self.cursor.x = len(self.currentLine)
		elif self.scrollY < len(self.buffer) - 1:
			self.scrollY += 1
		self.adjustHorizontalScroll()
	
	# Moves the cursor up half of a screen.
	def cursorUpPage(self):
		if self.cursor.y > 0:
			self.cursor.y = max(0, self.cursor.y - (self.height - 1)//2)
			self.cursor.x = min(self.cursor.x, len(self.currentLine))
			if self.cursor.y < self.scrollY:
				self.scrollY = self.cursor.y
		else:
			self.cursor.x = 0
		self.adjustHorizontalScroll()

	# Moves the cursor down half of a screen.
	def cursorDownPage(self):
		if self.cursor.y < len(self.buffer) - 1:
			self.cursor.y = min(len(self.buffer) - 1, self.cursor.y + (self.height - 1)//2)
			self.cursor.x = min(self.cursor.x, len(self.currentLine))
			if self.cursor.y > self.scrollY + self.height - 2:
				self.scrollY = min(len(self.buffer) - 1, self.scrollY + (self.height - 1)//2)
		elif self.cursor.x != len(self.currentLine):
			self.cursor.x = len(self.currentLine)
		elif self.scrollY < len(self.buffer) - 1:
			self.scrollY = min(len(self.buffer) - 1, self.scrollY + (self.height - 1)//2)
		self.adjustHorizontalScroll()
	
	# Moves the cursor up a whole screen.
	def cursorUpPAGE(self):
		if self.cursor.y > 0:
			self.cursor.y = max(0, self.cursor.y - self.height + 1)
			self.cursor.x = min(self.cursor.x, len(self.currentLine))
			if self.cursor.y < self.scrollY:
				self.scrollY = self.cursor.y
		else:
			self.cursor.x = 0
		self.adjustHorizontalScroll()

	# Moves the cursor down a whole screen.
	def cursorDownPAGE(self):
		if self.cursor.y < len(self.buffer) - 1:
			self.cursor.y = min(len(self.buffer) - 1, self.cursor.y + self.height - 1)
			self.cursor.x = min(self.cursor.x, len(self.currentLine))
			if self.cursor.y > self.scrollY + self.height - 2:
				self.scrollY = min(len(self.buffer) - 1, self.scrollY + self.height - 1)
		elif self.cursor.x != len(self.currentLine):
			self.cursor.x = len(self.currentLine)
		elif self.scrollY < len(self.buffer) - 1:
			self.scrollY = min(len(self.buffer) - 1, self.scrollY + self.height - 1)
		self.adjustHorizontalScroll()

	# Moves the cursor left a character.
	def cursorLeftCharacter(self):
		if self.cursor.x > 0:
			self.cursor.x -= 1
			# TODO: Decrement horizontal scroll if needed.
		elif self.cursor.y > 0:
			self.cursorUpLine()
			self.cursorLineEnd()
		self.adjustHorizontalScroll()

	# Moves the cursor right a character.
	def cursorRightCharacter(self):
		if self.cursor.x < len(self.currentLine):
			self.cursor.x += 1
		elif self.cursor.y < len(self.buffer) - 1:
			self.cursorDownLine()
			self.cursorLineBegin()
		self.adjustHorizontalScroll()

	# Moves the cursor left a word.
	def cursorLeftWord(self):
		symbols = "`~!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?"
		self.cursorLeftCharacter()

		# Skip the whitespace before the word.
		while not self.cursorAtBufferBegin() and self.currentCharacter in " \t\n":
			self.cursorLeftCharacter()

		if self.currentCharacter.isalnum() or self.currentCharacter == "_":
			# Get to the beginning of the word.
			while not self.cursorAtBufferBegin() and self.currentCharacter not in " \t\n" + symbols:
				self.cursorLeftCharacter()

			if self.currentCharacter in " \t\n" + symbols:
				self.cursorRightCharacter()
		else:
			# Get to the beginning of the word.
			while not self.cursorAtBufferBegin() and self.currentCharacter not in " \t\n" and not self.currentCharacter.isalnum() and not self.currentCharacter == "_":
				self.cursorLeftCharacter()

			if self.currentCharacter in " \t\n" or self.currentCharacter.isalnum() or self.currentCharacter == "_":
				self.cursorRightCharacter()
		self.adjustHorizontalScroll()
	
	# Moves the cursor right a word.
	def cursorRightWord(self):
		symbols = "`~!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?"
		if self.currentCharacter.isalnum() or self.currentCharacter == "_":
			# Get to the end of the current word.
			while not self.cursorAtBufferEnd() and self.currentCharacter not in " \t\n" + symbols:
				self.cursorRightCharacter()
		else:
			# Get to the end of the current word.
			while not self.cursorAtBufferEnd() and self.currentCharacter not in " \t\n" and not self.currentCharacter.isalnum() and self.currentCharacter != "_":
				self.cursorRightCharacter()

		# Skip the whitespace after the word.
		while not self.cursorAtBufferEnd() and self.currentCharacter in " \t\n":
			self.cursorRightCharacter()
		self.adjustHorizontalScroll()

	# Moves the cursor left a big word (anything separated by whitespace).
	def cursorLeftWORD(self):
		self.cursorLeftCharacter()

		# Skip the whitespace before the word.
		while not self.cursorAtBufferBegin() and self.currentCharacter in " \t\n":
			self.cursorLeftCharacter()

		# Get to the beginning of the word.
		while not self.cursorAtBufferBegin() and self.currentCharacter not in " \t\n":
			self.cursorLeftCharacter()

		if not self.cursorAtBufferBegin():
			self.cursorRightCharacter()
		self.adjustHorizontalScroll()

	# Moves the cursor right a big word (anything separated by whitespace).
	def cursorRightWORD(self):
		# Get to the end of the current word.
		while not self.cursorAtBufferEnd() and self.currentCharacter not in " \t\n":
			self.cursorRightCharacter()

		# Skip the whitespace after the word.
		while not self.cursorAtBufferEnd() and self.currentCharacter in " \t\n":
			self.cursorRightCharacter()
		self.adjustHorizontalScroll()

	# Inserts a character at the cursor.
	def insert(self, char):
		self.buffer.insert(self.cursor, char)
		self.cursorRightCharacter()
		self.hasChanges = True

	# Splits the current line in two.
	def splitLine(self):
		self.buffer.splitLine(self.cursor)
		self.cursorDownLine()
		self.cursor.x = 0
		self.adjustHorizontalScroll()
		self.hasChanges = True

	# Joins the current line with the previous line.
	def joinPreviousLine(self):
		if self.cursor.y > 0:
			cursorColumn = len(self.buffer.lines[self.cursor.y - 1]) + self.cursor.x
			self.buffer.joinPreviousLine(self.cursor)
			self.cursorUpLine()
			self.cursor.x = cursorColumn
			self.hasChanges = True
		self.adjustHorizontalScroll()

	# Joins the current line with the next line.
	def joinNextLine(self):
		if self.cursor.y < len(self.buffer) - 1:
			self.buffer.joinNextLine(self.cursor)
			self.hasChanges = True
		self.adjustHorizontalScroll()

	# Deletes the character to the left of the cursor.
	def deleteCharacterLeft(self):
		if self.cursor.x > 0:
			self.buffer.deleteCharacterLeft(self.cursor)
			self.cursorLeftCharacter()
			self.hasChanges = True
		elif self.cursor.y > 0:
			self.joinPreviousLine()
			self.hasChanges = True
		self.adjustHorizontalScroll()

	# Deletes the character to the right of the cursor.
	def deleteCharacterRight(self):
		if self.cursor.x < len(self.currentLine):
			self.buffer.deleteCharacterRight(self.cursor)
			self.hasChanges = True
		elif self.cursor.y < len(self.buffer) - 1:
			self.joinNextLine()
			self.hasChanges = True
		self.adjustHorizontalScroll()

# Stores and manipulates the lines of a file to be edited.
class Buffer:
	def __init__(self):
		self.lines = []

	def __len__(self):
		return len(self.lines)
	
	# The length of the longest line number in the buffer.
	@property
	def lineNumberLength(self):
		return max(3, len(str(len(self.lines))))
	
	# Resets the state of the buffer.
	def reset(self):
		self.lines = []

	# Reads the lines of the file into the buffer.
	def readLines(self, file):
		self.lines = file.read().splitlines()
		# TODO: Handle failed `read()`.

	# Inserts a string at the cursor.
	def insert(self, cursor, text):
		line = self.lines[cursor.y]
		self.lines[cursor.y] = line[:cursor.x] + text + line[cursor.x:]

	# Splits the line at the cursor.
	def splitLine(self, cursor):
		leftHalf = self.lines[cursor.y][:cursor.x]
		rightHalf = self.lines[cursor.y][cursor.x:]
		self.lines[cursor.y] = rightHalf
		self.lines.insert(cursor.y, leftHalf)

	# Joins the line at the cursor with the one above it.
	def joinPreviousLine(self, cursor):
		self.lines[cursor.y - 1] += self.lines[cursor.y]
		self.lines.pop(cursor.y)

	# Joins the line at the cursor with the one below it.
	def joinNextLine(self, cursor):
		self.lines[cursor.y] += self.lines[cursor.y + 1]
		self.lines.pop(cursor.y + 1)

	# Deletes the character to the left of the cursor.
	def deleteCharacterLeft(self, cursor):
		line = self.lines[cursor.y]
		self.lines[cursor.y] = line[:cursor.x - 1] + line[cursor.x:]

	# Deletes the character to the right of the cursor.
	def deleteCharacterRight(self, cursor):
		line = self.lines[cursor.y]
		self.lines[cursor.y] = line[:cursor.x] + line[cursor.x + 1:]

# Stores the position of the text cursor.
class Cursor:
	def __init__(self):
		self.y = 0
		self.x = 0

	# Move the cursor back to (0, 0).
	def reset(self):
		self.y = 0
		self.x = 0

# Does buffered output to the terminal. Used by `EditorView` to prevent flickering.
class Printer:
	def __init__(self):
		self.terminal = Terminal()
		self.output = ""

	# Clears the output buffer.
	def clear(self):
		self.output = ""

	# Appends to the output buffer.
	def print(self, text):
		self.output += text

	# Writes the output buffer to stdout and clears the buffer.
	def flush(self):
		print(self.terminal.home + self.terminal.clear, end="")
		print(self.output, end="", flush=True)
		self.clear()

if __name__ == "__main__":
	EditorController().run()
