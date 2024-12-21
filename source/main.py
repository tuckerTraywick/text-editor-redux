from blessed import Terminal

class Editor:
	def __init__(self):
		self.keyBindings = {
			"q": self.quit,
			"Q": self.quit,
			"KEY_UP": self.cursorUpLine,
			"KEY_DOWN": self.cursorDownLine,
			"KEY_LEFT": self.cursorLeftCharacter,
			"KEY_RIGHT": self.cursorRightCharacter,
		}
		self.terminal = Terminal()
		self.keepRunning = True
		self.lines = [
			"hello world",
			"hello!",
			"goodbye",
		]*10
		self.cursorY = 0
		self.cursorX = 0
		self.scrollY = 0
		self.scrollX = 0

	@property
	def lineNumberLength(self):
		return len(str(len(self.lines)))
	
	@property
	def currentLine(self):
		return self.lines[self.cursorY]

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
		status = f"{self.scrollY + 1}, {self.scrollX + 1}"
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
		elif "else" in self.keyBindings:
			self.keyBindings["else"](key)

	def run(self):
		with self.terminal.fullscreen(), self.terminal.raw(), self.terminal.keypad(), self.terminal.location():
			print(self.terminal.home + self.terminal.clear, end="", flush=True)
			while self.keepRunning:
				self.draw()
				self.processKeyPress()

	def quit(self, key):
		self.keepRunning = False

	def cursorUpLine(self, key):
		if self.cursorY > 0:
			self.cursorY -= 1
			self.cursorX = min(self.cursorX, len(self.currentLine))
		else:
			self.cursorX = 0

		if self.cursorY < self.scrollY:
			self.scrollY = self.cursorY

	def cursorDownLine(self, key):
		if self.cursorY < len(self.lines) - 1:
			self.cursorY += 1
			self.cursorX = min(self.cursorX, len(self.currentLine))
			if self.cursorY >= self.scrollY + self.terminal.height - 2:
				self.scrollY = self.cursorY - self.terminal.height + 2
		else:
			self.cursorX = len(self.currentLine)
			if self.scrollY < len(self.lines) - 1:
				self.scrollY += 1

	def cursorLeftCharacter(self, key):
		if self.cursorX > 0:
			self.cursorX -= 1
		elif self.cursorY > 0:
			self.cursorUpLine("")
			self.cursorX = len(self.currentLine)

	def cursorRightCharacter(self, key):
		if self.cursorX < len(self.currentLine):
			self.cursorX += 1
		elif self.cursorY < len(self.lines) - 1:
			self.cursorDownLine("")
			self.cursorX = 0

if __name__ == "__main__":
	Editor().run()
