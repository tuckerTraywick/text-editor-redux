from editormodel import EditorModel
from editorview import EditorView

# Handles the logic and main loop for the editor.
class EditorController:
	def __init__(self):
		self.model = EditorModel(self)
		self.view = EditorView(self.model)

		self.model.document.open("source/example.c")

	# Starts the main loop for the editor, stops when the user quits
	def run(self):
		terminal = self.view.printer.terminal
		with terminal.fullscreen(), terminal.raw(), terminal.keypad(), terminal.location():
			while self.model.keepRunning:
				self.view.height = terminal.height
				self.view.draw()
				key = self.view.getKeypress()
				self.processKeypress(key)

	# Delegates a keypress to the function it's bound to.
	def processKeypress(self, key):
		bindings = self.model.keybindings[self.model.mode]
		if key.name is not None and key.name in bindings:
			bindings[key.name](key)
		elif key in bindings:
			bindings[key](key)
		elif "else" in bindings:
			bindings["else"](key)

	###############################
	#### KEYBINDING FUNCTIONS #####
	###############################
	# Closes the file being edited and stops the editor.
	def quit(self, key):
		self.model.document.close()
		self.model.keepRunning = False

	# Saves the model.document to the file.
	def save(self, key):
		self.model.document.save()

	# Moves the cursor up a line.
	def cursorUpLine(self, key):
		self.model.document.cursorUpLine()
		
	# Moves the cursor down a line.
	def cursorDownLine(self, key):
		self.model.document.cursorDownLine()
		
	# Moves the left a character.
	def cursorLeftCharacter(self, key):
		self.model.document.cursorLeftCharacter()

	# Moves the cursor up a line.
	def cursorRightCharacter(self, key):
		self.model.document.cursorRightCharacter()
		
	# Moves the cursor left a word.
	def cursorLeftWord(self, key):
		self.model.document.cursorLeftWord()
		
	# Moves the cursor right a word.
	def cursorRightWord(self, key):
		self.model.document.cursorRightWord()
		
	# Moves the cursor left a big word.
	def cursorLeftWORD(self, key):
		self.model.document.cursorLeftWORD()
		
	# Moves the cursor right a big word.
	def cursorRightWORD(self, key):
		self.model.document.cursorRightWORD()
		
	# Inserts a character at the cursor.
	def insert(self, key):
		if key.isprintable():
			self.model.document.insert(key)
			
	# Splits the current line at the cursor.
	def splitLine(self, key):
		self.model.document.splitLine()
		
	# Joins the current line with the previous line.
	def joinPreviousLine(self, key):
		self.model.document.joinPreviousLine()
		
	# Deletes a character to the left of the cursor.
	def deleteCharacterLeft(self, key):
		self.model.document.deleteCharacterLeft()

	# Deletes a character to the right of the cursor.
	def deleteCharacterRight(self, key):
		self.model.document.deleteCharacterRight()
		
	# Returns back to normal mode.
	def enterNormalMode(self, key):
		self.model.mode = "normal"
		
	# Enters insert mode.
	def enterInsertMode(self, key):
		self.model.mode = "insert"
		
	# Moves the cursor up one half of the screen.
	def cursorUpPage(self, key):
		self.model.document.cursorUpPage()
		
	# Moves the cursor down one half of the screen.
	def cursorDownPage(self, key):
		self.model.document.cursorDownPage()

	# Moves the cursor up a whole screen.
	def cursorUpPAGE(self, key):
		self.model.document.cursorUpPAGE()
		
	# Moves the cursor down a whole screen.
	def cursorDownPAGE(self, key):
		self.model.document.cursorDownPAGE()
