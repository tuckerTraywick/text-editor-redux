import blessed

# The state of the entire editor and terminal.
class Editor:
	def __init__(self):
		self.terminal = blessed.Terminal()
		self.document = Document()
		self.keepRunning = True
		self.needsRedraw = True
		self.document.buffer = Buffer()

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
		status = f"{changes}{self.document.name} ({self.document.cursor.row}, {self.document.cursor.column}) | {self.document.fileType} | {self.document.lineEndingType}"
		print(self.terminal.home + self.terminal.move_down(self.terminal.height), end="")
		print(self.terminal.ljust(self.terminal.reverse + status), end="\r")

	# Draws the editor to the terminal.
	def draw(self):
		print(self.terminal.home + self.terminal.clear, end="")
		self.document.draw(self.terminal)
		self.drawStatusLine()

	# The main loop for the editor. Keeps running until the user quits.
	def run(self):
		with self.terminal.fullscreen(), self.terminal.cbreak():
			while self.keepRunning:
				if self.needsRedraw:
					self.needsRedraw = False
					self.draw()

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

	# Opens a file and reads it into the buffer, and resets the cursor.
	def open(self, path):
		self.name = path
		file = open(path, "r+")
		# TODO: Handle failed `open()`.
		self.file = file
		self.buffer.readLines(file)
		self.cursor.reset()

	# Closes the document, and resets its state.
	def close(self):
		self.buffer.reset()
		self.cursor.reset()
		self.file.close()

	# Draws the lines of the buffer to the terminal.
	def draw(self, terminal):
		self.buffer.draw(terminal)

# A list of lines that represents a piece of text.
class Buffer:
	def __init__(self):
		self.lines = []

	# Resets the state of the buffer.
	def reset(self):
		self.lines = []

	# Reads the lines of the file into the buffer.
	def readLines(self, file):
		self.lines = file.read().splitlines()
		# TODO: Handle failed `read()`.

	# Draws the lines of the buffer to the terminal.
	def draw(self, terminal):
		for i, line in enumerate(self.lines):
			print(f"{i + 1:>3} {line}")

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
