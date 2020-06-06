import random

class Item:
	def __init__ (self, level, sign, value=None, sides=None, tally=None, sectn=None, order=None, chldn=None):
		self.level = level
		self.sign = sign

	def value (self):
		pass

class Die:
	def __init__ (self, sides, tally, sctn):
		self.sides = sides
		self.tally = tally
		self.sctn = sctn

	def getValue (self):
		rolls = [random.randint(1, self.sides) for _ in range(self.tally)]
		rolls.sort()
		if self.sctn >= 0:
			return sum(rolls[-self.sctn:])
		else:
			return sum(rolls[:-self.sctn])

class Num:
	def __init__ (self, value):
		self.value = value

	def getValue (self):
		return self.value

# orders: [0 -> "+" or "-", 1 -> "*" or "/", 2 -> "**" or "//"]

class Arg:
	def __init__ (self, order, items):
		self.order = order
		self.items = items

	def getValue (self):
		if self.order == 2:
			pass
		elif self.order == 1:
			out = 1
			for itm in self.itms:
				out *= itm.getValue()
			return out
		else:
			return sum(itm.getValue() for itm in self.itms)

def parseQnt (text):
	if 'd' in text:
		count, sides = text.split('d')
		if len(count) == 0:
			tally = 1
			sctn = 1
		elif count.isdigit():
			tally = int(count)
			sctn = int(count)
		elif '>' in count:
			sctn, tally = count.split('>')
			if len(sctn) == 0:
				sctn = 1
			elif sctn.isdigit():
				sctn = int(sctn)
			else:
				return False
			if len(tally) == 0:
				tally = 2
			elif tally.isdigit():
				tally = int(tally)
			else:
				return False
		elif '<' in count:
			sctn, tally = count.split('<')
			if len(sctn) == 0:
				sctn = -1
			elif sctn.isdigit():
				sctn = -int(sctn)
			else:
				return False
			if len(tally) == 0:
				tally = 2
			elif tally.isdigit():
				tally = int(tally)
			else:
				return False
		else:
			return False
		if len(sides) == 0:
			sides = 20
		elif sides.isdigit():
			sides = int(sides)
		else:
			return False
		if abs(sctn) > tally:
			return False
		elif sctn == 0:
			return False
		return Die(sides, tally, sctn)
	elif text.isdigit():
		return Num(int(text))
	else:
		return False

def parseArg (text):
	pass