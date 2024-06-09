from editormodel import EditorModel
from editorview import EditorView

# Handles the logic and main loop for the editor.
class EditorController:
	def __init__(self):
		self.model = EditorModel(self)
		self.view = EditorView(self.model)

		self.model.document.open("source/example.c")

		terminal = self.view.printer.terminal
		self.view.colorscheme.colors = {
			"keyword": terminal.skyblue,
			"symbol": terminal.indianred,
			"identifier": terminal.snow,
			"number": terminal.mediumpurple,
			"string": terminal.lemonchiffon,
			"lineComment": terminal.palegreen3,
		}
		self.view.colorscheme.keywords = {
			"return", "for", "int", "void", "include",
		}
		self.view.colorscheme.symbols = "`~!@$%^&*()-_=+[{]}\\|;:,<.>/?"
		self.view.colorscheme.lineComment = "#"

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
			bindings[key.name](self, key)
		elif key in bindings:
			bindings[key](self, key)
		elif "else" in bindings:
			bindings["else"](self, key)

	###############################
	#### KEYBINDING FUNCTIONS #####
	###############################
	# Closes the file being edited and stops the editor.
	def quit(self, key):
		self.view.close()
		self.model.keepRunning = False

	# Saves the document to the file.
	def save(self, key):
		self.view.save()

	# Moves the cursor up a line.
	def cursorUpLine(self, key):
		self.view.cursorUpLine()
		
	# Moves the cursor down a line.
	def cursorDownLine(self, key):
		self.view.cursorDownLine()
		
	# Moves the left a character.
	def cursorLeftCharacter(self, key):
		self.view.cursorLeftCharacter()

	# Moves the cursor up a line.
	def cursorRightCharacter(self, key):
		self.view.cursorRightCharacter()
		
	# Moves the cursor left a word.
	def cursorLeftWord(self, key):
		self.view.cursorLeftWord()
		
	# Moves the cursor right a word.
	def cursorRightWord(self, key):
		self.view.cursorRightWord()
		
	# Moves the cursor left a big word.
	def cursorLeftWORD(self, key):
		self.view.cursorLeftWORD()
		
	# Moves the cursor right a big word.
	def cursorRightWORD(self, key):
		self.view.cursorRightWORD()
		
	# Inserts a character at the cursor.
	def insert(self, key):
		if key.isprintable():
			self.view.insert(key)
			
	# Splits the current line at the cursor.
	def splitLine(self, key):
		self.view.splitLine()
		
	# Joins the current line with the previous line.
	def joinPreviousLine(self, key):
		self.view.joinPreviousLine()
		
	# Deletes a character to the left of the cursor.
	def deleteCharacterLeft(self, key):
		self.view.deleteCharacterLeft()

	# Deletes a character to the right of the cursor.
	def deleteCharacterRight(self, key):
		self.view.deleteCharacterRight()
		
	# Returns back to normal mode.
	def enterNormalMode(self, key):
		self.model.mode = "normal"
		
	# Enters insert mode.
	def enterInsertMode(self, key):
		self.model.mode = "insert"
		
	# Moves the cursor up one half of the screen.
	def cursorUpPage(self, key):
		self.view.cursorUpPage()
		
	# Moves the cursor down one half of the screen.
	def cursorDownPage(self, key):
		self.view.cursorDownPage()

	# Moves the cursor up a whole screen.
	def cursorUpPAGE(self, key):
		self.view.cursorUpPAGE()
		
	# Moves the cursor down a whole screen.
	def cursorDownPAGE(self, key):
		self.view.cursorDownPAGE()
