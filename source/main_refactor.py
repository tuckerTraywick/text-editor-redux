import blessed

# Converts a key + ctrl (e.g. "^A") to it's ASCII representation.
def ctrl(char):
	return chr(ord(char.upper()) - 64)

# Searches for a key binding in a dictionary and returns it if found.
def getKeyBinding(bindings, key):
	if key.name is not None and key.name in bindings:
		return bindings[key.name]
	elif key in bindings:
		return bindings[key]
	elif "printable" in bindings and key.isprintable():
		return bindings["printable"]
	elif "else" in bindings:
		return bindings["else"]
	return None

# The top level state and behavior of the editor.
class Editor:
	def __init__(self):
		self.keyBindings = {
			ctrl("C"): self.quit,
		}

		self.terminal = blessed.Terminal()
		self.leftPanel = TabView()
		# self.rightPanel = TabView()
		# self.sidePanel = FileBrowser()
		# self.bottomPanel = Terminal()
		# self.searchPanel = SearchPanel()
		self.focus = self.leftPanel

		self.showLeftPanel = False
		# self.showRightPanel = False
		# self.showSidePanel = False
		# self.showBottomPanel = False
		# self.showSearchPanel = False
		self.keepRunning = True

	def draw(self):
		# Draw background.
		
		origin = 0
		# if self.showSidePanel:
		# 	self.sidePanel.draw(self.terminal, self.focus == self.sidePanel)
		# 	origin = self.sidePanel.width + 1

		height = self.terminal.height - 1
		# if self.showBottomPanel:
		# 	self.bottomPanel.draw(self.terminal, self.focus == self.bottomPanel)
		# 	height = self.terminal.height - self.bottomPanel.height

		if self.showLeftPanel:
			self.leftPanel.draw(self.terminal, self.focus == self.leftPanel, origin, height)
			
		# if self.showRightPanel:
		# 	self.rightPanel.draw(self.terminal, self.focus == self.rightPanel, origin + self.leftPanel.width, height)

		# if self.showSearchPanel:
		# 	self.searchPanel.draw(self.terminal, self.focus == self.searchPanel)

	def readKey(self):
		key = self.terminal.inkey()
		if not self.focus.processKeyPress(key):
			binding = getKeyBinding(self.keyBindings, key)
			if binding is not None:
				binding(key)

	def run(self):
		with self.terminal.fullscreen(), self.terminal.raw(), self.terminal.keypad(), self.terminal.location():
			print(self.terminal.home + self.terminal.clear, end="", flush=True)
			while self.keepRunning:
				self.draw()
				self.readKey()

# Superclass for all window panes in the editor.
class Panel:
	def __init__(self):
		self.keyBindings = {}

	def processKeyPress(self, key):
		binding = getKeyBinding(self.keyBindings, key)
		if binding is not None:
			binding(key)

# Shows a tabbed pane of multiple files.
class TabView(Panel):
	def __init__(self):
		super().__init__(self)
		self.keyBindings = {}
		self.tabs = []
		self.currentTabIndex = 0

	def drawTabList(self):
		pass

	def drawCurrentTab(self):
		pass

	def draw(self, terminal, focused, origin, height):
		pass

# Shows a file being edited.
class Buffer(Panel):
	def __init__(self):
		super().__init__(self)
		self.keyBindings = {}
		self.filePath = ""
		self.file = None
		self.lines = []
		self.selectionStartY = 0
		self.selectionStartX = 0
		self.selectionEndY = 0
		self.selectionEndX = 0
		self.scrollY = 0
		self.scrollX = 0
		self.hasUnsavedChanges = False

if __name__ == "__main__":
	Editor().run()
