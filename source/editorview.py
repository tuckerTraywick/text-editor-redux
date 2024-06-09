from blessed import Terminal

# Stores and presents the ui of the editor.
class EditorView:
	def __init__(self, model):
		self.model = model
		self.printer = Printer()
		self.colorscheme = {
			"statusLine": self.printer.terminal.snow_on_gray25,
			"lineNumber": self.printer.terminal.gray55_on_gray10,
			"currentLineNumber": self.printer.terminal.lightyellow_on_gray15,
			"line": self.printer.terminal.snow_on_gray10,
			"currentLine": self.printer.terminal.snow_on_gray15,
			"normal": self.printer.terminal.snow_on_slateblue3,
			"insert": self.printer.terminal.snow_on_seagreen3,
			"tabBar": self.printer.terminal.snow_on_gray25,
			"tab": self.printer.terminal.snow_on_gray40,
			"currentTab": self.printer.terminal.snow_on_gray35,
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
		changes = self.colors["hasChanges"]("•") if document.hasChanges else ""
		tab = self.colors["currentTab"](f" {changes}{document.name} ")
		printer.print(terminal.home + self.colors["tabBar"](terminal.ljust(tab)))
	
	# Draws the document to the screen.
	def drawDocument(self):
		scrollY = self.model.document.scrollY
		scrollX = self.model.document.scrollX
		buffer = self.model.document.buffer
		cursor = self.model.document.cursor
		syntax = self.model.document.syntax
		terminal = self.printer.terminal
		lineEnd = scrollX + terminal.width - buffer.lineNumberLength - 1
		for i in range(scrollY, scrollY + terminal.height - 1):
			if i == cursor.y:
				number = self.colors["currentLineNumber"](f"{i + 1:>{buffer.lineNumberLength}}")
				line = syntax.highlight(buffer.lines[i][scrollX:lineEnd])
				self.printer.print(self.colors["currentLine"](terminal.ljust(f"{number} {line}")))
			elif i < len(buffer):
				number = self.colors["lineNumber"](f"{i + 1:>{buffer.lineNumberLength}}")
				line = syntax.highlight(buffer.lines[i][scrollX:lineEnd])
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
		status = f"C | Unix | Ln {document.cursor.y + 1}, Col {document.cursor.x + 1}"
		printer.print(terminal.home + terminal.move_down(terminal.height))
		printer.print(self.colors["statusLine"](terminal.ljust(f"{mode} {status}")))

	# Draws the model to the screen.
	def draw(self):
		self.model.document.height = self.printer.terminal.height
		self.model.document.width = self.printer.terminal.width
		if self.model.mode in ["normal", "insert"]:
			self.drawTabBar()
			self.drawDocument()
			self.drawStatusLine()
			self.drawCursor()
		self.printer.flush()

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
