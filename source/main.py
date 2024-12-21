from blessed import Terminal

class Editor:
	def __init__(self):
		self.terminal = Terminal()
		self.keepRunning = True
		self.lines = ["line"]*self.terminal.height*2
		self.cursorY = 0
		self.cursorX = 4
		self.scrollY = 0
		self.scrollX = 0

	@property
	def lineNumberLength(self):
		return len(str(len(self.lines)))

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
		print(self.terminal.home, end="")
		self.drawLines()
		self.drawCursor()
		self.drawStatus()

	def processKeyPress(self):
		key = self.terminal.inkey()
		if key in "qQ":
			self.keepRunning = False

	def run(self):
		with self.terminal.fullscreen(), self.terminal.raw(), self.terminal.keypad(), self.terminal.location():
			print(self.terminal.home + self.terminal.clear, end="", flush=True)
			while self.keepRunning:
				self.draw()
				self.processKeyPress()

if __name__ == "__main__":
	Editor().run()
