from blessed import Terminal

# Converts a key + ctrl (e.g. "^A") to it's ASCII representation.
def ctrl(char):
	return chr(ord(char.upper()) - 64)

class Buffer:
	def __init__(self):
		self.reset()

	@property
	def lineNumberLength(self):
		return max(3, len(str(len(self.lines))))
	
	@property
	def currentLine(self):
		return self.lines[self.cursorY]

	@currentLine.setter
	def currentLine(self, line):
		self.lines[self.cursorY] = line

	def reset(self):
		self.cursorY = 0
		self.cursorX = 0
		self.scrollY = 0
		self.scrollX = 0
		self.pageHeight = 0
		self.pageWidth = 0
		self.hasUnsavedChanges = False
		self.name = ""
		self.filePath = ""
		self.file = None
		self.lines = []

	def open(self, filePath):
		self.cursorY = 0
		self.cursorX = 0
		self.scrollY = 0
		self.scrollX = 0
		self.hasUnsavedChanges = False
		self.name = filePath
		self.filePath = filePath
		self.file = open(self.filePath, "r+")

		# Read the lines of the file and keep track of the last line.
		self.lines = []
		lastLine = None
		for line in self.file:
			lastLine = line
			self.lines.append(line.rstrip("\n"))
		
		# Add a trailing newline if the last line is empty.
		if not self.lines or lastLine.endswith("\n"):
			self.lines.append("")

	def drawLines(self, y, x, height, width, terminal, screenBuffer):
		for i in range(min(len(self.lines) - self.scrollY, height)):
			lineNumber = f"{i + self.scrollY + 1:>{self.lineNumberLength}}"
			line = self.lines[self.scrollY + i]
			screenBuffer.append(terminal.move_x(x) + f"{lineNumber} {line}" + "\r\n")

	def drawCursor(self, y, x, height, width, terminal, screenBuffer):
		screenY = self.cursorY - self.scrollY
		screenX = x + self.cursorX - self.scrollX + self.lineNumberLength + 1
		character = " "
		if self.cursorY < len(self.lines) and self.cursorX < len(self.lines[self.cursorY]):
			character = self.lines[self.cursorY][self.cursorX]
		screenBuffer.append(terminal.move_yx(screenY, screenX) + terminal.reverse(character))

	def draw(self, y, x, height, width, terminal, screenBuffer):
		screenBuffer.append(terminal.move_yx(y, x))
		self.drawLines(y, x, height, width, terminal, screenBuffer)
		self.drawCursor(y, x, height, width, terminal, screenBuffer)

	def cursorLineUp(self, key):
		if self.cursorY > 0:
			self.cursorY -= 1
			self.cursorX = min(self.cursorX, len(self.currentLine))
		else:
			self.cursorX = 0

		if self.cursorY < self.scrollY:
			self.scrollY = self.cursorY

	def cursorLineDown(self, key):
		if self.cursorY < len(self.lines) - 1:
			self.cursorY += 1
			self.cursorX = min(self.cursorX, len(self.currentLine))
			if self.cursorY > self.scrollY + self.pageHeight - 1:
				self.scrollY = self.cursorY - self.pageHeight + 1
		elif self.scrollY < len(self.lines) - 1 and self.cursorX == len(self.currentLine):
			self.scrollY += 1
		else:
			self.cursorX = len(self.currentLine)

	def cursorCharacterLeft(self, key):
		if self.cursorX > 0:
			self.cursorX -= 1
		elif self.cursorY > 0:
			self.cursorLineUp("")
			self.cursorX = len(self.currentLine)

	def cursorCharacterRight(self, key):
		if self.cursorX < len(self.currentLine):
			self.cursorX += 1
		elif self.cursorY < len(self.lines) - 1:
			self.cursorLineDown("")
			self.cursorX = 0

	def insertCharacter(self, key):
		self.currentLine = self.currentLine[:self.cursorX] + key + self.currentLine[self.cursorX:]
		self.cursorCharacterRight("")
		self.hasUnsavedChanges = True

	def deleteCharacterLeft(self, key):
		if self.cursorX == 0 and self.cursorY > 0:
			length = len(self.lines[self.cursorY - 1])
			self.lines[self.cursorY - 1] += self.currentLine
			self.lines.pop(self.cursorY)
			self.cursorLineUp("")
			self.cursorX = length
			self.hasUnsavedChanges = True
		elif self.cursorX > 0:
			self.currentLine = self.currentLine[:self.cursorX - 1] + self.currentLine[self.cursorX:]
			self.cursorCharacterLeft("")
			self.hasUnsavedChanges = True

	def deleteCharacterRight(self, key):
		if self.cursorX == len(self.currentLine) and self.cursorY < len(self.lines) - 1:
			self.currentLine += self.lines[self.cursorY + 1]
			self.lines.pop(self.cursorY + 1)
			self.hasUnsavedChanges = True
		elif self.cursorX < len(self.currentLine):
			self.currentLine = self.currentLine[:self.cursorX] + self.currentLine[self.cursorX + 1:]
			self.hasUnsavedChanges = True

	def splitLine(self, key):
		end = self.currentLine[self.cursorX:]
		self.currentLine = self.currentLine[:self.cursorX]
		self.lines.insert(self.cursorY + 1, end)
		self.cursorLineDown("")
		self.cursorX = 0
		self.hasUnsavedChanges = True
	
	def close(self, key):
		# TODO: Handle unsaved changes.
		self.file.close()
		self.reset()

	def save(self, key):
		if self.hasUnsavedChanges:
			self.file.truncate(0)
			self.file.seek(0)
			self.file.writelines("\n".join(self.lines))
			self.hasUnsavedChanges = False

class FileBrowser:
	def __init__(self):
		self.directory = "/Users/tuckertraywick"
		self.entries = ["example.txt", "directory/", "another.txt"]*10
		self.cursorY = 0
		self.scrollY = 0
		self.pageHeight = 0

	def draw(self, y, x, height, width, terminal, screenBuffer):
		# Draw the current directory.
		screenBuffer.append(terminal.move_yx(y, x) + terminal.reverse(self.directory.ljust(width)) + "\r\n")

		# Draw the entries in the directory.
		for i in range(min(len(self.entries) - self.scrollY, height - 1)):
			entryIndex = i + self.scrollY
			if entryIndex == self.cursorY:
				screenBuffer.append(terminal.reverse(self.entries[entryIndex].ljust(width)) + "\r\n")
			else:
				screenBuffer.append(self.entries[entryIndex] + "\r\n")

		# Draw the arrows if needed.
		if self.scrollY > 0:
			up = terminal.reverse("^") if self.cursorY <= self.scrollY else "^"
			screenBuffer.append(terminal.move_yx(1, width - 1) + up)

		if self.scrollY + self.pageHeight < len(self.entries):
			down = terminal.reverse("v") if self.cursorY >= self.scrollY + self.pageHeight - 2 else "v"
			screenBuffer.append(terminal.move_yx(height - 1, width - 1) + down + "\r")

	def entryUp(self, key):
		if self.cursorY > 0:
			self.cursorY -= 1

		if self.cursorY < self.scrollY:
			self.scrollY = self.cursorY

	def entryDown(self, key):
		if self.cursorY < len(self.entries) - 1:
			self.cursorY += 1

		if self.cursorY > self.scrollY + self.pageHeight - 2:
			self.scrollY = self.cursorY - self.pageHeight + 2

class Editor:
	def __init__(self):
		self.reset()
		self.keyBindings = {
			"printable": lambda key: self.buffer.insertCharacter(key),
			"KEY_ENTER": lambda key: self.buffer.splitLine(key),
			"KEY_BACKSPACE": lambda key: self.buffer.deleteCharacterLeft(key),
			"x": lambda key: self.buffer.deleteCharacterRight(key),
			"KEY_UP": lambda key: self.fileBrowser.entryUp(key),
			"KEY_DOWN": lambda key: self.fileBrowser.entryDown(key),
			"KEY_LEFT": lambda key: self.buffer.cursorCharacterLeft(key),
			"KEY_RIGHT": lambda key: self.buffer.cursorCharacterRight(key),
			ctrl("C"): self.quit,
			ctrl("S"): lambda key: self.buffer.save(key),
		}

	@property
	def lineNumberLength(self):
		return max(3, len(str(len(self.lines))))
	
	@property
	def currentLine(self):
		return self.lines[self.cursorY]

	@currentLine.setter
	def currentLine(self, line):
		self.lines[self.cursorY] = line

	def reset(self):
		self.terminal = Terminal()
		self.mode = "insert"
		self.screenBuffer = []
		self.keepRunning = True

		self.buffer = Buffer()
		self.buffer.pageWidth = self.terminal.width - self.terminal.width//4 - 1
		self.buffer.pageHeight = self.terminal.height - 1

		self.fileBrowser = FileBrowser()
		self.fileBrowser.pageHeight = self.buffer.pageHeight

	def print(self, text):
		self.screenBuffer.append(text)

	def drawStatus(self):
		status = f" {self.mode}  Ln {self.cursorY + 1}, Col {self.cursorX + 1}"
		self.print(self.terminal.home + self.terminal.move_down(self.terminal.height))
		self.print(self.terminal.reverse(status.ljust(self.terminal.width)) + "\r")

	def drawBuffer(self):
		self.buffer.draw(0, self.terminal.width//4 + 1, self.buffer.pageHeight, self.buffer.pageWidth, self.terminal, self.screenBuffer)

	def drawFileBrowser(self):
		self.fileBrowser.draw(0, 0, self.terminal.height - 1, self.terminal.width//4, self.terminal, self.screenBuffer)

	def drawBar(self):
		# Draw the vertical border.
		width = self.terminal.width//4
		self.print(self.terminal.home)
		for i in range(self.terminal.height - 1):
			self.print(self.terminal.move_x(width) + self.terminal.reverse(" ") + "\r\n")
		self.print(self.terminal.move_x(width) + self.terminal.reverse(" ") + "\r")

	def draw(self):
		self.print(self.terminal.home + self.terminal.clear)
		self.drawFileBrowser()
		# self.drawBuffer()

		# Print the contents of the screen buffer and clear it.
		print("".join(self.screenBuffer), end="")
		self.screenBuffer = []

	def processKeyPress(self):
		key = self.terminal.inkey()
		if key.name is not None and key.name in self.keyBindings:
			self.keyBindings[key.name](key)
		elif key in self.keyBindings:
			self.keyBindings[key](key)
		elif "printable" in self.keyBindings:
			self.keyBindings["printable"](key)
		elif "else" in self.keyBindings:
			self.keyBindings["else"](key)

	def run(self):
		self.reset()
		self.buffer.open("untitled.txt")
		with self.terminal.fullscreen(), self.terminal.hidden_cursor(), self.terminal.raw(), self.terminal.keypad(), self.terminal.location():
			print(self.terminal.home + self.terminal.clear, end="", flush=True)
			while self.keepRunning:
				self.draw()
				self.processKeyPress()

	def quit(self, key):
		self.keepRunning = False
		self.buffer.close(None)

if __name__ == "__main__":
	Editor().run()
