import blessed

# The state of the entire editor and terminal.
class Editor:
	def __init__(self):
		self.term = blessed.Terminal()
		self.Document = Document()

	def run(self):
		print("hello")

# Holds a buffer and a cursor to operate on it.
class Document:
	def __init__(self):
		self.buffer = Buffer()
		self.cursor = Cursor()

# A list of lines that represents a piece of text.
class Buffer:
	def __init__(self):
		self.lines = []

# A location in a buffer.
class Cursor:
	def __init__(self):
		self.row = 0
		self.column = 0

def main():
	Editor().run()

if __name__ == "__main__":
	main()
