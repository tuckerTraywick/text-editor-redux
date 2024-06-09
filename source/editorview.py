from colorscheme import Colorscheme
from blessed import Terminal

# Stores and presents the ui of the editor.
class EditorView:
	def __init__(self, model):
		self.model = model
		self.printer = Printer()
		terminal = self.printer.terminal
		self.colorscheme = Colorscheme()
		self.colorscheme.themeColors = {
			"statusLine": terminal.snow_on_gray25,
			"lineNumber": terminal.gray55_on_gray10,
			"currentLineNumber": terminal.lightyellow_on_gray15,
			"line": terminal.snow_on_gray10,
			"currentLine": terminal.snow_on_gray15,
			"normal": terminal.snow_on_slateblue3,
			"insert": terminal.snow_on_seagreen3,
			"tabBar": terminal.snow_on_gray25,
			"tab": terminal.snow_on_gray40,
			"currentTab": terminal.snow_on_gray35,
			"hasChanges": terminal.brown2,
		}
		self.colorscheme.syntaxColors = {
			"keyword": terminal.skyblue,
			"symbol": terminal.indianred,
			"identifier": terminal.snow,
			"number": terminal.mediumpurple,
			"string": terminal.lemonchiffon,
			"lineComment": terminal.palegreen3,
		}

	# Returns a keypress from the user.
	def getKeypress(self):
		return self.printer.terminal.inkey()
	
	# Draws the tab bar to the screen.
	def drawTabBar(self):
		printer = self.printer
		terminal = self.printer.terminal
		document = self.model.document
		changes = self.colorscheme.themeColors["hasChanges"]("•") if document.hasChanges else ""
		tab = self.colorscheme.themeColors["currentTab"](f" {changes}{document.name} ")
		printer.print(terminal.home + self.colorscheme.themeColors["tabBar"](terminal.ljust(tab)))
	
	# Draws the document to the screen.
	def drawDocument(self):
		scrollY = self.model.document.scrollY
		scrollX = self.model.document.scrollX
		buffer = self.model.document.buffer
		cursor = self.model.document.cursor
		terminal = self.printer.terminal
		lineEnd = scrollX + terminal.width - buffer.lineNumberLength - 1
		for i in range(scrollY, scrollY + terminal.height - 1):
			if i == cursor.y:
				number = self.colorscheme.themeColors["currentLineNumber"](f"{i + 1:>{buffer.lineNumberLength}}")
				line = buffer.lines[i][scrollX:lineEnd]
				self.printer.print(self.colorscheme.themeColors["currentLine"](terminal.ljust(f"{number} {line}")))
			elif i < len(buffer):
				number = self.colorscheme.themeColors["lineNumber"](f"{i + 1:>{buffer.lineNumberLength}}")
				line = buffer.lines[i][scrollX:lineEnd]
				self.printer.print(self.colorscheme.themeColors["line"](terminal.ljust(f"{number} {line}")))
			else:
				self.printer.print(self.colorscheme.themeColors["line"](terminal.ljust("")))

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
		mode = self.colorscheme.themeColors[self.model.mode](f" {self.model.mode.upper()} ")
		status = f"C | Unix | Ln {document.cursor.y + 1}, Col {document.cursor.x + 1}"
		printer.print(terminal.home + terminal.move_down(terminal.height))
		printer.print(self.colorscheme.themeColors["statusLine"](terminal.ljust(f"{mode} {status}")))

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
