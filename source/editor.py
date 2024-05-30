# TODO: Add assertions for keybinding methods, e.x., you can't call `deleteCharacterLeft()` if the
#       cursor is at the beginning of a line.
# TODO: Remove unnecessary arguments in keybinding methods in `Buffer`.
# TODO: Implement horizontal scrolling.

import blessed

# Converts a key + control (ex. "^A") to it's ascii representation.
def ctrl(char):
	return chr(ord(char.upper()) - 64)

# A buffer between building the screen and printing it. Helps prevent flickering.
class Printer:
	def __init__(self, terminal):
		self.terminal = terminal
		self.string = ""

	# Clears the buffer.
	def clear(self):
		self.string = ""

	# Adds text to the buffer to print.
	def print(self, text):
		self.string += text

	# Writes the text to stdout and clears the buffer.
	def flush(self):
		print(self.terminal.home + self.terminal.clear, end="")
		print(self.string, end="", flush=True)
		self.clear()

# The state of the entire editor and terminal.
class Editor:
	def __init__(self):
		self.terminal = blessed.Terminal()
		self.printer = Printer(self.terminal)
		self.document = Document()
		self.keepRunning = True
		self.needsRedraw = True
		self.document.buffer = Buffer()
		self.mode = " NORMAL "

		self.colors = {
			"statusLine": self.terminal.gray99_on_gray25,
			"lineNumber": self.terminal.gray43_on_gray10,
			"currentLineNumber": self.terminal.lightyellow_on_gray15,
			"text": self.terminal.snow_on_gray10,
			"currentLine": self.terminal.snow_on_gray15,
		}
		self.modeColors = {
			" NORMAL ": self.terminal.snow_on_slateblue3,
			" INSERT ": self.terminal.snow_on_seagreen4,
			" VISUAL ": self.terminal.snow_on_goldenrod4,
		}
		self.keybindings = {
			" NORMAL ": {
				"h": self.cursorLeftCharacter,
				"l": self.cursorRightCharacter,
				"k": self.cursorUpLine,
				"j": self.cursorDownLine,
				"i": self.enterInsertMode,
				"H": self.cursorLeftWORD,
				"L": self.cursorRightWORD,
				ctrl("c"): self.quit,
				"KEY_UP": self.cursorUpLine,
				"KEY_DOWN": self.cursorDownLine,
				"KEY_LEFT": self.cursorLeftCharacter,
				"KEY_RIGHT": self.cursorRightCharacter,
				# "KEY_ENTER": self.splitLine,
				"KEY_BACKSPACE": self.deleteCharacterLeft,
				"KEY_DELETE": self.deleteCharacterRight,
			},
			" INSERT ": {
				ctrl("c"): self.quit,
				"KEY_ESCAPE": self.enterNormalMode,
				"KEY_UP": self.cursorUpLine,
				"KEY_DOWN": self.cursorDownLine,
				"KEY_LEFT": self.cursorLeftCharacter,
				"KEY_RIGHT": self.cursorRightCharacter,
				"KEY_ENTER": self.splitLine,
				"KEY_BACKSPACE": self.deleteCharacterLeft,
				"KEY_DELETE": self.deleteCharacterRight,
				"else": self.insert,
			},
		}

		self.open("source/example.txt")

	# Opens a file for editing.
	def open(self, path):
		self.document.open(path)
		self.needsRedraw = True

	# Closes the document being edited.
	def close(self):
		self.document.close()
		self.needsRedraw = True

	# Draws the status line at the bottom of the screen.
	def drawStatusLine(self):
		mode = self.modeColors[self.mode](self.mode)
		changes = "[+] " if self.document.hasChanges else ""
		status = f"{mode} {changes}{self.document.name} ({self.document.cursor.row + 1}, {self.document.cursor.column + 1}) | {self.document.fileType} | {self.document.lineEndingType}"
		self.printer.print(self.terminal.home + self.terminal.move_down(self.terminal.height))
		self.printer.print(self.colors["statusLine"](self.terminal.ljust(status)))

	# Draws the cursor.
	def drawCursor(self):
		y = self.document.cursor.row - self.document.scrollY
		# TODO: Remove magic number.
		x = self.document.cursor.column - self.document.scrollX + 4
		# TODO: Find a way to get the cursor to show up without flushing stdout.
		self.printer.print(self.terminal.home + self.terminal.move_yx(y, x))

	# Draws the editor.
	def draw(self):
		self.printer.clear()
		self.document.draw(self.printer, self.colors)
		self.drawStatusLine()
		self.drawCursor()
		self.printer.flush()

	# Processes key presses.
	def processInput(self):
		key = self.terminal.inkey()
		bindings = self.keybindings[self.mode]
		if key.name is not None and key.name in bindings:
			bindings[key.name](self.printer, key)
		elif key in bindings:
			bindings[key](self.printer, key)
		elif "else" in bindings:
			bindings["else"](self.printer, key)

	# The main loop for the editor. Keeps running until the user quits.
	def run(self):
		with self.terminal.fullscreen(), self.terminal.raw(), self.terminal.keypad():
			while self.keepRunning:
				if self.needsRedraw:
					self.needsRedraw = False
					self.draw()
				self.processInput()
	
	###############################
	#### KEYBINDING FUNCTIONS #####
	###############################
	# Closes the file being edited and stops the editor.
	def quit(self, printer, key):
		self.close()
		self.keepRunning = False

	# Moves the cursor up a line.
	def cursorUpLine(self, printer, key):
		self.document.cursorUpLine(printer, key)
		self.needsRedraw = True

	# Moves the cursor down a line.
	def cursorDownLine(self, printer, key):
		self.document.cursorDownLine(printer, key)
		self.needsRedraw = True

	# Moves the left a character.
	def cursorLeftCharacter(self, printer, key):
		self.document.cursorLeftCharacter(printer, key)
		self.needsRedraw = True

	# Moves the cursor up a line.
	def cursorRightCharacter(self, printer, key):
		self.document.cursorRightCharacter(printer, key)
		self.needsRedraw = True

	# Moves the cursor left a big word.
	def cursorLeftWORD(self, printer, key):
		self.document.cursorLeftWORD(printer, key)
		self.needsRedraw = True

	# Moves the cursor right a big word.
	def cursorRightWORD(self, printer, key):
		self.document.cursorRightWORD(printer, key)
		self.needsRedraw = True

	# Inserts a character at the cursor.
	def insert(self, printer, key):
		if key.isprintable():
			self.document.insert(printer, key)
			self.needsRedraw = True

	# Splits the current line at the cursor.
	def splitLine(self, printer, key):
		self.document.splitLine(printer, key)
		self.needsRedraw = True

	# Joins the current line with the previous line.
	def joinPreviousLine(self, printer, key):
		self.document.joinPreviousLine(printer, key)
		self.needsRedraw = True

	# Deletes a character to the left of the cursor.
	def deleteCharacterLeft(self, printer, key):
		self.document.deleteCharacterLeft(printer, key)
		self.needsRedraw = True

	# Deletes a character to the right of the cursor.
	def deleteCharacterRight(self, printer, key):
		self.document.deleteCharacterRight(printer, key)
		self.needsRedraw = True

	# Returns back to normal mode.
	def enterNormalMode(self, printer, key):
		self.mode = " NORMAL "
		self.needsRedraw = True

	# Enters insert mode.
	def enterInsertMode(self, printer, key):
		self.mode = " INSERT "
		self.needsRedraw = True

# Holds a buffer and a cursor to operate on it.
class Document:
	def __init__(self):
		self.name = ""
		self.fileType = "text" # TODO: Set this field in `open()`.
		self.lineEndingType = "unix" # TODO: Set this field in `open()`.
		self.hasChanges = False
		self.file = None
		self.buffer = Buffer()
		self.cursor = Cursor()
		self.selectionCursor = Cursor()
		self.scrollY = 0
		self.scrollX = 0

	# Returns the line the cursor is on.
	@property
	def currentLine(self):
		return self.buffer.lines[self.cursor.row]
	
	# Returns the character under the cursor.
	@property
	def currentCharacter(self):
		if self.cursor.column < len(self.currentLine):
			return self.currentLine[self.cursor.column]
		else:
			return "\n"
		
	# Returns the character behind the cursor.
	@property
	def previousCharacter(self):
		if self.cursorAtBufferBegin():
			return "\0"
		elif self.cursor.column > 0:
			return self.currentLine[self.cursor.column - 1]
		else:
			return "\n"
		
	# Returns true if the cursor is at the beginning of the buffer.
	def cursorAtBufferBegin(self):
		return self.cursor.row == 0 and self.cursor.column == 0

	# Returns true if the cursor is at the end of the buffer.
	def cursorAtBufferEnd(self):
		return self.cursor.row == self.buffer.length - 1 and self.cursor.column == len(self.currentLine)

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

	# Draws the lines of the buffer to the terminal.
	def draw(self, printer, colors):
		self.buffer.draw(printer, colors, self.scrollY, self.scrollY + printer.terminal.height - 1, self.cursor.row)

	# Moves the cursor to the beginning of the line.
	def cursorLineBegin(self, printer, key):
		self.cursor.column = 0
		# TODO: Adjust horizontal scroll if needed.
			
	# Moves the cursor to the end of the line.
	def cursorLineEnd(self, printer, key):
		self.cursor.column = len(self.currentLine)
		# TODO: Adjust horizontal scroll if needed.

	# Moves the cursor up a line and adjusts the scroll if needed.
	def cursorUpLine(self, printer, key):
		if self.cursor.row > 0:
			self.cursor.row -= 1
			self.cursor.column = min(self.cursor.column, len(self.currentLine))
			if self.cursor.row < self.scrollY:
				self.scrollY -= 1
		else:
			self.cursor.column = 0
			# TODO: Adjust horizontal scroll if needed.

	# Moves the cursor down a line and adjusts the scroll if needed.
	def cursorDownLine(self, printer, key):
		if self.cursor.row < self.buffer.length - 1:
			self.cursor.row += 1
			self.cursor.column = min(self.cursor.column, len(self.currentLine))
			if self.cursor.row > self.scrollY + printer.terminal.height - 2:
				self.scrollY += 1
			# TODO: Adjust horizontal scroll if needed.
		elif self.cursor.column != len(self.currentLine):
			self.cursor.column = len(self.currentLine)
			# TODO: Adjust horizontal scroll if needed.
		elif self.scrollY < self.buffer.length - 1:
			self .scrollY += 1
	
	# Moves the cursor left a character.
	def cursorLeftCharacter(self, printer, key):
		if self.cursor.column > 0:
			self.cursor.column -= 1
			# TODO: Decrement horizontal scroll if needed.
		elif self.cursor.row > 0:
			self.cursorUpLine(printer, key)
			self.cursorLineEnd(printer, key)

	# Moves the cursor right a character.
	def cursorRightCharacter(self, printer, key):
		if self.cursor.column < len(self.currentLine):
			self.cursor.column += 1
			# TODO: Increment horizonal scroll if needed.
		elif self.cursor.row < self.buffer.length - 1:
			self.cursorDownLine(printer, key)
			self.cursorLineBegin(printer, key)

	# Moves the cursor left a big word (anything separated by whitespace).
	def cursorLeftWORD(self, printer, key):
		self.cursorLeftCharacter(printer, key)

		# Skip the whitespace before the word.
		while not self.cursorAtBufferBegin() and self.currentCharacter in " \t\n":
			self.cursorLeftCharacter(printer, key)

		# Get to the beginning of the word.
		while not self.cursorAtBufferBegin() and self.currentCharacter not in " \t\n":
			self.cursorLeftCharacter(printer, key)

		if not self.cursorAtBufferBegin():
			self.cursorRightCharacter(printer, key)

	# Moves the cursor right a big word (anything separated by whitespace).
	def cursorRightWORD(self, printer, key):
		# Get to the end of the current word.
		while not self.cursorAtBufferEnd() and self.currentCharacter not in " \t\n":
			self.cursorRightCharacter(printer, key)

		# Skip the whitespace after the word.
		while not self.cursorAtBufferEnd() and self.currentCharacter in " \t\n":
			self.cursorRightCharacter(printer, key)

	# Inserts a character at the cursor.
	def insert(self, printer, key):
		self.buffer.insert(self.cursor, key)
		self.cursorRightCharacter(printer, key)
		self.hasChanges = True

	# Splits the current line in two.
	def splitLine(self, printer, key):
		self.buffer.splitLine(self.cursor)
		self.cursorDownLine(printer, key)
		self.cursor.column = 0
		# TODO: Adjust horizontal scroll if needed.
		self.hasChanges = True

	# Joins the current line with the previous line.
	def joinPreviousLine(self, printer, key):
		if self.cursor.row > 0:
			cursorColumn = len(self.buffer.lines[self.cursor.row - 1]) + self.cursor.column
			self.buffer.joinPreviousLine(self.cursor)
			self.cursorUpLine(printer, key)
			self.cursor.column = cursorColumn
			# TODO: Adjust horizontal scroll if needed.
			self.hasChanges = True

	# Joins the current line with the next line.
	def joinNextLine(self, printer, key):
		if self.cursor.row < self.buffer.length - 1:
			self.buffer.joinNextLine(self.cursor)
			self.hasChanges = True

	# Deletes the character to the left of the cursor.
	def deleteCharacterLeft(self, printer, key):
		if self.cursor.column > 0:
			self.buffer.deleteCharacterLeft(self.cursor)
			self.cursorLeftCharacter(printer, key)
			self.hasChanges = True
		elif self.cursor.row > 0:
			self.joinPreviousLine(printer, key)
			self.hasChanges = True

	# Deletes the character to the right of the cursor.
	def deleteCharacterRight(self, printer, key):
		if self.cursor.column < len(self.currentLine):
			self.buffer.deleteCharacterRight(self.cursor)
			self.hasChanges = True
		elif self.cursor.row < self.buffer.length - 1:
			self.joinNextLine(printer, key)
			self.hasChanges = True

# A list of lines that represents a piece of text.
class Buffer:
	def __init__(self):
		self.lines = []

	# Returns how many lines are in the buffer.
	@property
	def length(self):
		return len(self.lines)
	
	# Resets the state of the buffer.
	def reset(self):
		self.lines = []

	# Reads the lines of the file into the buffer.
	def readLines(self, file):
		self.lines = file.read().splitlines()
		# TODO: Handle failed `read()`.

	# Draws the lines of the buffer to the terminal.
	def draw(self, printer, colors, start, end, current):
		for i, line in enumerate(self.lines[start:end]):
			numberColor = colors["currentLineNumber"] if start + i == current else colors["lineNumber"]
			number = numberColor(f"{start + i + 1:>3} ")
			lineColor = colors["currentLine"] if start + i == current else colors["text"]
			printer.print(lineColor(printer.terminal.ljust(f"{number}{line}")))
		
		for j in range(printer.terminal.height - i - 1):
			printer.print(colors["text"](printer.terminal.ljust(colors["lineNumber"]("    "))))

	# Inserts a string at the cursor.
	def insert(self, cursor, text):
		line = self.lines[cursor.row]
		self.lines[cursor.row] = line[:cursor.column] + text + line[cursor.column:]

	# Splits the line at the cursor.
	def splitLine(self, cursor):
		leftHalf = self.lines[cursor.row][:cursor.column]
		rightHalf = self.lines[cursor.row][cursor.column:]
		self.lines[cursor.row] = rightHalf
		self.lines.insert(cursor.row, leftHalf)

	# Joins the line at the cursor with the one above it.
	def joinPreviousLine(self, cursor):
		self.lines[cursor.row - 1] += self.lines[cursor.row]
		self.lines.pop(cursor.row)

	# Joins the line at the cursor with the one below it.
	def joinNextLine(self, cursor):
		self.lines[cursor.row] += self.lines[cursor.row + 1]
		self.lines.pop(cursor.row + 1)

	# Deletes the character to the left of the cursor.
	def deleteCharacterLeft(self, cursor):
		line = self.lines[cursor.row]
		self.lines[cursor.row] = line[:cursor.column - 1] + line[cursor.column:]

	# Deletes the character to the right of the cursor.
	def deleteCharacterRight(self, cursor):
		line = self.lines[cursor.row]
		self.lines[cursor.row] = line[:cursor.column] + line[cursor.column + 1:]

# A location in a buffer.
class Cursor:
	def __init__(self):
		self.row = 0
		self.column = 0

	# Move the cursor back to (0, 0).
	def reset(self):
		self.row = 0
		self.column = 0

def main():
	Editor().run()

if __name__ == "__main__":
	main()
