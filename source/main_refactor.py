import blessed

# Converts a character + ctrl (e.g. "^A") to it's ASCII representation.
def ctrl(char):
	return chr(ord(char.upper()) - 64)

# Searches for a key binding in a dictionary and returns it if found.
def getKeyBinding(bindings, key):
	if key.name and key.name in bindings:
		return bindings[key.name]
	elif key in bindings:
		return bindings[key]
	elif "printable" in bindings and key.isprintable():
		return bindings["printable"]
	elif "else" in bindings:
		return bindings["else"]
	return None

# Superclass for all window panes in the editor.
class Panel:
	def __init__(self, parent):
		self.keyBindings = {}
		self.parent = parent
		self.focused = False
		self.visible = False

	def processKeyPress(self, key):
		binding = getKeyBinding(self.keyBindings, key)
		if self.parent and not binding:
			self.parent.processKeyPress(key)
		else:
			binding(key)

	def draw(self, terminal, y, x, height, width):
		pass

# The top level state and behavior of the editor.
class Editor(Panel):
	def __init__(self):
		super().__init__(None)
		self.visible = True
		self.keyBindings = {
			ctrl("C"): self.quit,
		}

		self.terminal = blessed.Terminal()
		self.buffer = Buffer(self)
		self.buffer.focused = True
		self.buffer.visible = True
		self.buffer.pageHeight = self.terminal.height
		self.buffer.pageWidth = self.terminal.width
		self.buffer.open("untitled.txt")
		
		self.focus = self.buffer
		self.keepRunning = True

	def draw(self):
		y, x = 0, 0
		height, width = self.terminal.height, self.terminal.width
		self.buffer.draw(self.terminal, y, x, height, width)

	def readKey(self):
		key = self.terminal.inkey()
		self.focus.processKeyPress(key)

	def run(self):
		with self.terminal.fullscreen(), self.terminal.raw(), self.terminal.keypad(), self.terminal.location(), self.terminal.hidden_cursor():
			print(self.terminal.home + self.terminal.clear, end="", flush=True)
			while self.keepRunning:
				self.draw()
				self.readKey()

	def quit(self, key):
		self.keepRunning = False

# A tabbed pane of multiple files.
class TabView(Panel):
	def __init__(self, editor):
		super().__init__(editor)
		self.keyBindings = {}
		self.tabs = []
		self.currentTabIndex = 0

	def drawTabList(self):
		pass

	def drawCurrentTab(self):
		pass

	def draw(self, terminal, focused, origin, height):
		pass

# A file being edited.
class Buffer(Panel):
	def __init__(self, tabView):
		super().__init__(tabView)
		self.keyBindings = {
			"KEY_ENTER": self.splitLine,
			"KEY_BACKSPACE": self.deleteCharacterLeft,
			"x": self.deleteCharacterRight,
			"KEY_UP": self.cursorLineUp,
			"KEY_DOWN": self.cursorLineDown,
			"KEY_LEFT": self.cursorCharacterLeft,
			"KEY_RIGHT": self.cursorCharacterRight,
			ctrl("S"): self.save,
			"printable": self.insertCharacter,
		}
		self.reset()
		
	@property
	def lineNumberLength(self):
		return max(3, len(str(len(self.lines))))
	
	@property
	def currentLine(self):
		return self.lines[self.selectionStartY]

	@currentLine.setter
	def currentLine(self, line):
		self.lines[self.selectionStartY] = line

	def reset(self):
		self.filePath = ""
		self.file = None
		self.lines = [""]
		self.selectionStartY = 0
		self.selectionStartX = 0
		self.scrollY = 0
		self.scrollX = 0
		self.pageHeight = 0
		self.pageWidth = 0
		self.hasUnsavedChanges = False

	def drawLines(self, terminal, y, x, height, width):
		print(terminal.home + terminal.move_yx(y, x), end="")
		for i in range(min(len(self.lines) - self.scrollY, height - 1)):
			lineNumber = f"{i + self.scrollY + 1:>{self.lineNumberLength}}"
			line = self.lines[self.scrollY + i]
			status = f"{lineNumber} {line}"
			print(status[:min(len(status), width)], end="\r\n")

	def drawCursor(self, terminal, y, x, height, width):
		screenY = y + self.selectionStartY - self.scrollY
		screenX = x + self.selectionStartX - self.scrollX + self.lineNumberLength + 1
		character = " "
		if self.selectionStartY < len(self.lines) and self.selectionStartX < len(self.lines[self.selectionStartY]):
			character = self.lines[self.selectionStartY][self.selectionStartX]
		print(terminal.move_yx(screenY, screenX) + terminal.reverse(character), end="\r")

	def draw(self, terminal, y, x, height, width):
		if self.visible:
			self.drawLines(terminal, y, x, height, width)
			self.drawCursor(terminal, y, x, height, width)

	def open(self, filePath):
		self.reset()
		self.filePath = filePath
		self.file = open(self.filePath, "r+")
		self.lines = [line.rstrip("\n") for line in self.file.readlines()]
		if not self.lines:
			self.lines = [""]

	def cursorLineUp(self, key):
		if self.selectionStartY > 0:
			self.selectionStartY -= 1
			self.selectionStartX = min(self.selectionStartX, len(self.currentLine))
		else:
			self.selectionStartX = 0

		if self.selectionStartY < self.scrollY:
			self.scrollY = self.selectionStartY

	def cursorLineDown(self, key):
		if self.selectionStartY < len(self.lines) - 1:
			self.selectionStartY += 1
			self.selectionStartX = min(self.selectionStartX, len(self.currentLine))
			if self.selectionStartY >= self.scrollY + self.pageHeight - 2:
				self.scrollY = self.selectionStartY - self.pageHeight + 2
		elif self.scrollY < len(self.lines) - 1 and self.selectionStartX == len(self.currentLine):
			self.scrollY += 1
		else:
			self.selectionStartX = len(self.currentLine)

	def cursorCharacterLeft(self, key):
		if self.selectionStartX > 0:
			self.selectionStartX -= 1
		elif self.selectionStartY > 0:
			self.cursorLineUp("")
			self.selectionStartX = len(self.currentLine)

	def cursorCharacterRight(self, key):
		if self.selectionStartX < len(self.currentLine):
			self.selectionStartX += 1
		elif self.selectionStartY < len(self.lines) - 1:
			self.cursorLineDown("")
			self.selectionStartX = 0

	def insertCharacter(self, key):
		self.currentLine = self.currentLine[:self.selectionStartX] + key + self.currentLine[self.selectionStartX:]
		self.cursorCharacterRight("")
		self.hasUnsavedChanges = True

	def deleteCharacterLeft(self, key):
		if self.selectionStartX == 0 and self.selectionStartY > 0:
			length = len(self.lines[self.selectionStartY - 1])
			self.lines[self.selectionStartY - 1] += self.currentLine
			self.lines.pop(self.selectionStartY)
			self.cursorLineUp("")
			self.selectionStartX = length
			self.hasUnsavedChanges = True
		elif self.selectionStartX > 0:
			self.currentLine = self.currentLine[:self.selectionStartX - 1] + self.currentLine[self.selectionStartX:]
			self.cursorCharacterLeft("")
			self.hasUnsavedChanges = True

	def deleteCharacterRight(self, key):
		if self.selectionStartX == len(self.currentLine) and self.selectionStartY < len(self.lines) - 1:
			self.currentLine += self.lines[self.selectionStartY + 1]
			self.lines.pop(self.selectionStartY + 1)
			self.hasUnsavedChanges = True
		elif self.selectionStartX < len(self.currentLine):
			self.currentLine = self.currentLine[:self.selectionStartX] + self.currentLine[self.selectionStartX + 1:]
			self.hasUnsavedChanges = True

	def splitLine(self, key):
		end = self.currentLine[self.selectionStartX:]
		self.currentLine = self.currentLine[:self.selectionStartX]
		self.lines.insert(self.selectionStartY + 1, end)
		self.cursorLineDown(None)
		self.selectionStartX = 0
		self.hasUnsavedChanges = True

	def save(self, key):
		if self.hasUnsavedChanges:
			self.file.truncate(0)
			self.file.seek(0)
			self.file.writelines("\n".join(self.lines))
			self.hasUnsavedChanges = False

if __name__ == "__main__":
	Editor().run()
