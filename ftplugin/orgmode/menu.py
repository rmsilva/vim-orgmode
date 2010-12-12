import vim

from orgmode.keybinding import Keybinding, MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT

def register_menu(f):
	def r(*args, **kwargs):
		p = f(*args, **kwargs)
		if hasattr(p, 'menu') and (isinstance(p.menu, Submenu) \
				or isinstance(p.menu, HorizontalLine) or isinstance(p.menu, ActionEntry)):
			p.menu.create()
		return p
	return r

class Submenu(object):
	""" Submenu entry """

	def __init__(self, name, parent=None):
		object.__init__(self)
		self.name = name
		self.parent = parent
		self._children = []

	def __add__(self, entry):
		if entry not in self._children:
			self._children.append(entry)
			entry.parent = self
			return entry

	def __sub__(self, entry):
		if entry in self._children:
			idx = self._children.index(entry)
			del self._children[idx]

	@property
	def children(self):
		return self._children[:]

	def get_menu(self):
		n = self.name.replace(' ', '\\ ')
		if self.parent:
			return '%s.%s' % (self.parent.get_menu(), n)
		return n

	def create(self):
		for c in self.children:
			c.create()

class HorizontalLine(object):
	""" Menu entry for a HorizontalLine """

	def __init__(self, parent):
		object.__init__(self)
		self.parent = parent

	def create(self):
		vim.command('-%s-' % repr(self))

class ActionEntry(object):
	""" ActionEntry entry """

	def __init__(self, lname, action, rname=None, mode=MODE_NORMAL, parent=None):
		"""
		:lname: menu title on the left hand side of the menu entry
		:action: could be a vim command sequence or an actual Keybinding
		:rname: menu title that appears on the right hand side of the menu
				entry. If action is a Keybinding this value ignored and is
				taken from the Keybinding
		:mode: defines when the menu entry/action is executable
		:parent: the parent instance of this object. The only valid parent is Submenu
		"""
		object.__init__(self)
		self._lname = lname
		self._action = action
		self._rname = rname
		if mode not in (MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT):
			raise ValueError('Parameter mode not in MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT')
		self._mode = mode
		self.parent = parent

	@property
	def lname(self):
		return self._lname.replace(' ', '\\ ')

	@property
	def action(self):
		if isinstance(self._action, Keybinding):
			return self._action.action
		return self._action

	@property
	def rname(self):
		if isinstance(self._action, Keybinding):
			return self._action.key.replace('<Tab>', 'Tab')
		return self._rname

	@property
	def mode(self):
		if isinstance(self._action, Keybinding):
			return self._action.mode
		return self._mode

	def create(self):
		menucmd = ':%smenu ' % self.mode
		menu = ''
		cmd = ''

		if self.parent:
			menu = self.parent.get_menu()
		menu += '.%s' % self.lname

		if self.rname:
			cmd = '%s %s<Tab>%s %s' % (menucmd, menu, self.rname, self.action)
		else:
			cmd = '%s %s %s' % (menucmd, menu, self.action)

		vim.command(cmd)

		if isinstance(self._action, Keybinding):
			self._action.create()
