# TODO: Add assertions for keybinding methods, e.x., you can't call `deleteCharacterLeft()` if the
#       cursor is at the beginning of a line.
# TODO: Remove unnecessary arguments in keybinding methods in `Buffer`.
# TODO: Implement horizontal scrolling.

import blessed

# Converts a key + control (ex. "^A") to it's ascii representation.
def ctrl(char):
	return chr(ord(char.upper()) - 64)

# The state of the entire editor and terminal.
class Editor:
	def __init__(self):
		self.terminal = blessed.Terminal()
		self.document = Document()
		self.keepRunning = True
		self.needsRedraw = True
		self.document.buffer = Buffer()
		self.keybindings = {
			# "q": self.quit,
			ctrl("q"): self.quit,
			"KEY_UP": self.cursorUpLine,
			"KEY_DOWN": self.cursorDownLine,
			"KEY_LEFT": self.cursorLeftCharacter,
			"KEY_RIGHT": self.cursorRightCharacter,
			"KEY_ENTER": self.splitLine,
			"KEY_BACKSPACE": self.deleteCharacterLeft,
			"KEY_DELETE": self.deleteCharacterRight,
			"else": self.insert,
		}

		self.open("source/example.txt")
		self.terminal.pixel_width

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
		changes = "[+] " if self.document.hasChanges else ""
		status = f"{changes}{self.document.name} ({self.document.cursor.row + 1}, {self.document.cursor.column + 1}) | {self.document.fileType} | {self.document.lineEndingType}"
		print(self.terminal.home + self.terminal.move_down(self.terminal.height), end="")
		print(self.terminal.ljust(self.terminal.reverse + status), end="")
		print(self.terminal.normal, end="")

	# Draws the cursor.
	def drawCursor(self):
		y = self.document.cursor.row - self.document.scrollY
		# TODO: Remove magic number.
		x = self.document.cursor.column - self.document.scrollX + 4
		# TODO: Find a way to get the cursor to show up without flushing stdout.
		print(self.terminal.home + self.terminal.move_yx(y, x), end="", flush=True)

	# Draws the editor.
	def draw(self):
		print(self.terminal.home + self.terminal.clear, end="")
		self.document.draw(self.terminal)
		self.drawStatusLine()
		self.drawCursor()

	# Processes key presses.
	def processInput(self):
		key = self.terminal.inkey()
		if key.name is not None and key.name in self.keybindings:
			self.keybindings[key.name](self.terminal, key)
		elif key in self.keybindings:
			self.keybindings[key](self.terminal, key)
		elif "else" in self.keybindings:
			self.keybindings["else"](self.terminal, key)

	# The main loop for the editor. Keeps running until the user quits.
	def run(self):
		with self.terminal.fullscreen(), self.terminal.raw():
			while self.keepRunning:
				if self.needsRedraw:
					self.needsRedraw = False
					self.draw()
				self.processInput()
	
	###############################
	#### KEYBINDING FUNCTIONS #####
	###############################
	# Closes the file being edited and stops the editor.
	def quit(self, terminal, key):
		self.close()
		self.keepRunning = False

	# Moves the cursor up a line.
	def cursorUpLine(self, terminal, key):
		self.document.cursorUpLine(terminal, key)
		self.needsRedraw = True

	# Moves the cursor down a line.
	def cursorDownLine(self, terminal, key):
		self.document.cursorDownLine(terminal, key)
		self.needsRedraw = True

	# Moves the left a character.
	def cursorLeftCharacter(self, terminal, key):
		self.document.cursorLeftCharacter(terminal, key)
		self.needsRedraw = True

	# Moves the cursor up a line.
	def cursorRightCharacter(self, terminal, key):
		self.document.cursorRightCharacter(terminal, key)
		self.needsRedraw = True

	# Inserts a character at the cursor.
	def insert(self, terminal, key):
		if key.isprintable():
			self.document.insert(terminal, key)
			self.needsRedraw = True

	# Splits the current line at the cursor.
	def splitLine(self, terminal, key):
		self.document.splitLine(terminal, key)
		self.needsRedraw = True

	# Joins the current line with the previous line.
	def joinPreviousLine(self, terminal, key):
		self.document.joinPreviousLine(terminal, key)
		self.needsRedraw = True

	# Deletes a character to the left of the cursor.
	def deleteCharacterLeft(self, terminal, key):
		self.document.deleteCharacterLeft(terminal, key)
		self.needsRedraw = True

	# Deletes a character to the right of the cursor.
	def deleteCharacterRight(self, terminal, key):
		self.document.deleteCharacterRight(terminal, key)
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
	def draw(self, terminal):
		self.buffer.draw(terminal, self.scrollY, self.scrollY + terminal.height - 1)

	# Moves the cursor to the beginning of the line.
	def cursorLineBegin(self, terminal, key):
		self.cursor.column = 0
		# TODO: Adjust horizontal scroll if needed.
			
	# Moves the cursor to the end of the line.
	def cursorLineEnd(self, terminal, key):
		self.cursor.column = len(self.currentLine)
		# TODO: Adjust horizontal scroll if needed.

	# Moves the cursor up a line and adjusts the scroll if needed.
	def cursorUpLine(self, terminal, key):
		if self.cursor.row > 0:
			self.cursor.row -= 1
			self.cursor.column = min(self.cursor.column, len(self.currentLine))
			if self.cursor.row < self.scrollY:
				self.scrollY -= 1
		else:
			self.cursor.column = 0
			# TODO: Adjust horizontal scroll if needed.

	# Moves the cursor down a line and adjusts the scroll if needed.
	def cursorDownLine(self, terminal, key):
		if self.cursor.row < self.buffer.length - 1:
			self.cursor.row += 1
			self.cursor.column = min(self.cursor.column, len(self.currentLine))
			if self.cursor.row > self.scrollY + terminal.height - 2:
				self.scrollY += 1
			# TODO: Adjust horizontal scroll if needed.
		else:
			self.cursor.column = len(self.currentLine)
			# TODO: Adjust horizontal scroll if needed.
	
	# Moves the cursor left a character.
	def cursorLeftCharacter(self, terminal, key):
		if self.cursor.column > 0:
			self.cursor.column -= 1
			# TODO: Decrement horizontal scroll if needed.
		elif self.cursor.row > 0:
			self.cursorUpLine(terminal, key)
			self.cursorLineEnd(terminal, key)

	# Moves the cursor right a character.
	def cursorRightCharacter(self, terminal, key):
		if self.cursor.column < len(self.currentLine):
			self.cursor.column += 1
			# TODO: Increment horizonal scroll if needed.
		elif self.cursor.row < self.buffer.length - 1:
			self.cursorDownLine(terminal, key)
			self.cursorLineBegin(terminal, key)

	# Inserts a character at the cursor.
	def insert(self, terminal, key):
		self.buffer.insert(self.cursor, key)
		self.cursorRightCharacter(terminal, key)

	# Splits the current line in two.
	def splitLine(self, terminal, key):
		self.buffer.splitLine(self.cursor)
		self.cursorDownLine(terminal, key)
		self.cursor.column = 0
		# TODO: Adjust horizontal scroll if needed.

	# Joins the current line with the previous line.
	def joinPreviousLine(self, terminal, key):
		if self.cursor.row > 0:
			cursorColumn = len(self.buffer.lines[self.cursor.row - 1]) + self.cursor.column
			self.buffer.joinPreviousLine(self.cursor)
			self.cursorUpLine(terminal, key)
			self.cursor.column = cursorColumn
			# TODO: Adjust horizontal scroll if needed.

	# Joins the current line with the next line.
	def joinNextLine(self, terminal, key):
		if self.cursor.row < self.buffer.length - 1:
			self.buffer.joinNextLine(self.cursor)

	# Deletes the character to the left of the cursor.
	def deleteCharacterLeft(self, terminal, key):
		if self.cursor.column > 0:
			self.buffer.deleteCharacterLeft(self.cursor)
			self.cursorLeftCharacter(terminal, key)
		elif self.cursor.row > 0:
			self.joinPreviousLine(terminal, key)

	# Deletes the character to the right of the cursor.
	def deleteCharacterRight(self, terminal, key):
		if self.cursor.column < len(self.currentLine):
			self.buffer.deleteCharacterRight(self.cursor)
		elif self.cursor.row < self.buffer.length:
			self.joinNextLine(terminal, key)

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
	def draw(self, terminal, start, end):
		for i, line in enumerate(self.lines[start:end]):
			print(f"{start + i + 1:>3} {line}", end="\r\n")

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
