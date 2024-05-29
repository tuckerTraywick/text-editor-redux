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
		self.close()

	# Opens a file for editing.
	def open(self, path):
		self.document.open(path)
		self.needsRedraw = True

	# Closes the document being edited.
	def close(self):
		self.document.close()
		self.needsRedraw = True

	# The main loop for the editor. Keeps running until the user quits.
	def run(self):
		while self.keepRunning:
			if self.needsRedraw:
				self.needsRedraw = False
				self.document.draw(self.terminal)

# Holds a buffer and a cursor to operate on it.
class Document:
	def __init__(self):
		self.name = ""
		self.file = None
		self.buffer = Buffer()
		self.cursor = Cursor()

	# Opens a file and reads it into the buffer, and resets the cursor.
	def open(self, path):
		file = open(path, "r")
		# TODO: Handle failed `open()`.
		self.buffer.readLines(file)
		self.cursor.reset()

	# Closes the document, and resets its state.
	def close(self):
		self.buffer.reset()
		self.cursor.reset()

	# Draws the lines of the buffer to the terminal.
	def draw(self, terminal):
		for line in self.buffer.lines:
			print(line, end="")

# A list of lines that represents a piece of text.
class Buffer:
	def __init__(self):
		self.lines = []

	# Resets the state of the buffer.
	def reset(self):
		self.lines = []

	# Reads the lines of the file into the buffer.
	def readLines(self, file):
		self.lines = file.readlines()
		# TODO: Handle failed `readlines()`.

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
