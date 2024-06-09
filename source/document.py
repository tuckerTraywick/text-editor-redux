# Represents a buffer along with it's cursor. Used to manipulate text.
class Document:
	def __init__(self):
		self.buffer = Buffer()
		self.cursor = Cursor()
		self.file = None
		self.name = ""
		self.path = ""
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
		self.path = path
		file = open(path, "r+")
		# TODO: Handle failed `open()`.
		self.file = file
		self.buffer.readLines(file)
		self.cursor.reset()
		self.hasChanges = False
		self.scrollY = 0
		self.scrollX = 0

	# Saves the document to the file.
	def save(self):
		self.file.close()
		self.file = open(self.path, "w")
		self.file.writelines(line + "\n" for line in self.buffer.lines)
		self.hasChanges = False

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
		if self.cursor.x < self.scrollX:
			self.scrollX = self.cursor.x
		elif self.cursor.x > self.scrollX + self.width - self.buffer.lineNumberLength - 2:
			self.scrollX = self.cursor.x - self.width + self.buffer.lineNumberLength + 2

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
			if self.cursor.y > self.scrollY + self.height - 3:
				self.scrollY += 1
		elif self.cursor.x != len(self.currentLine):
			self.cursor.x = len(self.currentLine)
		elif self.scrollY < len(self.buffer) - 1:
			self.scrollY += 1
		self.adjustHorizontalScroll()
	
	# Moves the cursor up half of a screen.
	def cursorUpPage(self):
		if self.cursor.y > 0:
			self.cursor.y = max(0, self.cursor.y - (self.height - 2)//2)
			self.cursor.x = min(self.cursor.x, len(self.currentLine))
			if self.cursor.y < self.scrollY:
				self.scrollY = self.cursor.y
		else:
			self.cursor.x = 0
		self.adjustHorizontalScroll()

	# Moves the cursor down half of a screen.
	def cursorDownPage(self):
		if self.cursor.y < len(self.buffer) - 1:
			self.cursor.y = min(len(self.buffer) - 1, self.cursor.y + (self.height - 2)//2)
			self.cursor.x = min(self.cursor.x, len(self.currentLine))
			if self.cursor.y > self.scrollY + self.height - 3:
				self.scrollY = min(len(self.buffer) - 1, self.scrollY + (self.height - 2)//2)
		elif self.cursor.x != len(self.currentLine):
			self.cursor.x = len(self.currentLine)
		elif self.scrollY < len(self.buffer) - 1:
			self.scrollY = min(len(self.buffer) - 1, self.scrollY + (self.height - 2)//2)
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
			self.cursor.y = min(len(self.buffer) - 1, self.cursor.y + self.height - 2)
			self.cursor.x = min(self.cursor.x, len(self.currentLine))
			if self.cursor.y > self.scrollY + self.height - 3:
				self.scrollY = min(len(self.buffer) - 1, self.scrollY + self.height - 2)
		elif self.cursor.x != len(self.currentLine):
			self.cursor.x = len(self.currentLine)
		elif self.scrollY < len(self.buffer) - 1:
			self.scrollY = min(len(self.buffer) - 1, self.scrollY + self.height - 2)
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
