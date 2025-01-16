from blessed import Terminal

# Converts a key + ctrl (e.g. "^A") to it's ASCII representation.
def ctrl(char):
	return chr(ord(char.upper()) - 64)

class Editor:
	def __init__(self):
		self.keyBindings = {
			"printable": self.insertCharacter,
			"KEY_ENTER": self.splitLine,
			"KEY_BACKSPACE": self.deleteCharacterLeft,
			"x": self.deleteCharacterRight,
			"KEY_UP": self.cursorLineUp,
			"KEY_DOWN": self.cursorLineDown,
			"KEY_LEFT": self.cursorCharacterLeft,
			"KEY_RIGHT": self.cursorCharacterRight,
			ctrl("C"): self.quit,
			ctrl("S"): self.save,
		}
		self.terminal = Terminal()

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
		self.keepRunning = True
		self.lines = []
		self.cursorY = 0
		self.cursorX = 0
		self.scrollY = 0
		self.scrollX = 0
		self.filePath = ""
		self.file = None
		self.hasUnsavedChanges = False

	def drawLines(self):
		print(self.terminal.home, end="")
		for i in range(min(len(self.lines) - self.scrollY, self.terminal.height - 1)):
			lineNumber = f"{i + self.scrollY + 1:>{self.lineNumberLength}}"
			line = self.lines[self.scrollY + i]
			print(f"{lineNumber} {line}", end="\r\n")

	def drawCursor(self):
		screenY = self.cursorY - self.scrollY
		screenX = self.cursorX - self.scrollX + self.lineNumberLength + 1
		character = " "
		if self.cursorY < len(self.lines) and self.cursorX < len(self.lines[self.cursorY]):
			character = self.lines[self.cursorY][self.cursorX]
		print(self.terminal.move_yx(screenY, screenX) + self.terminal.reverse(character), end="")

	def drawStatus(self):
		star = "*" if self.hasUnsavedChanges else ""
		status = f"{self.cursorY + 1}, {self.cursorX + 1} {star}{self.filePath}"
		print(self.terminal.home + self.terminal.move_down(self.terminal.height), end="")
		print(self.terminal.reverse(status.ljust(self.terminal.width)), end="\r")

	def draw(self):
		print(self.terminal.home + self.terminal.clear, end="")
		self.drawLines()
		self.drawCursor()
		self.drawStatus()

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
		self.open("untitled.txt")
		with self.terminal.fullscreen(), self.terminal.raw(), self.terminal.keypad(), self.terminal.location():
			print(self.terminal.home + self.terminal.clear, end="", flush=True)
			while self.keepRunning:
				self.draw()
				self.processKeyPress()

	def open(self, filePath):
		self.reset()
		self.filePath = filePath
		self.file = open(self.filePath, "r+")
		self.lines = [line.rstrip("\n") for line in self.file.readlines()]
		if not self.lines:
			self.lines = [""]

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
			if self.cursorY >= self.scrollY + self.terminal.height - 2:
				self.scrollY = self.cursorY - self.terminal.height + 2
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

	def save(self, key):
		if self.hasUnsavedChanges:
			self.file.truncate(0)
			self.file.seek(0)
			self.file.writelines("\n".join(self.lines))
			if self.lines[-1] == "":
				self.file.write("\n")
			self.hasUnsavedChanges = False

	def quit(self, key):
		self.keepRunning = False
		self.file.close()

if __name__ == "__main__":
	Editor().run()
