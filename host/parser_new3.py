from enum import IntEnum
from fractions import Fraction
from abc import ABC as abstract_base_class, abstractmethod
from collections import Counter
from itertools import product as itertools_product, chain as itertools_chain, zip_longest as itertools_zip_longest
from functools import reduce as functools_reduce
from operator import add as operator_add, mul as operator_mul, pow as operator_pow
from random import randint as random_randint

operators = {
	'+': 10, '-': 11, '*': 12, '/': 13, '**': 14, '*/': 15, '%': 16,
	'==': 20, '!=': 21, '>': 22, '<': 23, '>=': 24, '<=': 25,
	'&': 30, '|': 31, '!': 32, '?': 33, ':': 34,
	'(': 40, ')': 41, ',': 42, '"': 43,
	'=': 50, '=#': 51, '=!': 52,
	'd': 60, '@': 61, '!@': 62,
	'#': 70
}

charsets = [
	' ',
	'0123456789.',
	'ABCDEFGHIJKLMNOPQRSTUVWXYZabcefghijklmnopqrstuvwxyz_',
	''.join(operators.keys()),
	None
]

class Hierarchy (IntEnum):
	Ternary = 1
	Logical = 2
	Comparison = 3
	Arithmetic = 4
	Inversion = 5
	Modular = 6
	Negation = 7
	Die = 8
	Number = 9
	Error = 10
	Assignment = 11
	Symbol = 12

class Error:
	def __init__ (self, msg, ctr, ind):
		self.msg, self.ctr, self.ind = msg, ctr, ind

	def __repr__ (self):
		return '[Error: {msg} - "{ctr}" - {ind}]'.format(msg=self.msg, ctr=self.ctr, ind=self.ind)

def parseCharacters (text):
	characters = []
	previousCharacter = {'text': '', 'charset': 0}
	parentheses = []
	for i, t in enumerate(text+' '):
		for c, charset in enumerate(charsets):
			if c == 4:
				return Error('Invalid Character', t, i)
			elif t in charset:
				if previousCharacter['charset'] == c and (c != 3 or any(o.startswith(previousCharacter['text'] + t) for o in operators.keys())):
					previousCharacter['text'] += t
				else:
					if previousCharacter['charset'] == 3:
						if previousCharacter['text'] in operators:
							previousCharacter['code'] = operators[previousCharacter['text']]
							if previousCharacter['code'] == 40:
								parentheses.append(len(characters))
							elif previousCharacter['code'] == 41:
								if parentheses:
									previousCharacter['alternate'] = parentheses[-1]
									characters[parentheses[-1]]['alternate'] = len(characters)
									parentheses.pop()
								else:
									return Error('Extra Right Parentheses', t, i)
						else:
							return Error('Invalid Operator', t, i)
					if previousCharacter['charset'] != 0:
						previousCharacter['ind'] = len(characters)
						characters.append(previousCharacter)
					previousCharacter = {'ind': None, 'text': t, 'charset': c, 'code': None, 'alternate': None}
				break
	if parentheses:
		return Error('Unclosed Left Parentheses', '(', parentheses[-1]['ind'])
	return characters

def parseHierarchy (characters, start=0, stop=None, minHierarchy=Hierarchy.Ternary, outer=None, statement=False):
	if stop is None:
		stop = len(characters)

	while len(characters) and characters[0]['alternate'] == characters[-1]['ind']:
		characters = characters[1:-1]
		start += 1
		stop -= 1
		outer = None
		minHierarchy = Hierarchy.Ternary

	if outer is None:
		outer = []
		ind = 0
		while ind < stop - start:
			if characters[ind]['alternate'] is None:
				outer.append(characters[ind])
				ind += 1
			else:
				ind = characters[ind]['alternate'] - start + 1
	else:
		outer = [o for o in outer if o['ind'] in range(start, stop)]

	if statement and len(characters) >= 2 and characters[0]['charset'] == 2 and characters[1]['code'] in range(50, 53):
		symbol = (Hierarchy.Symbol, characters[0]['text'], 0, 0)
		if characters[1]['code'] == 52:
			if len(characters) > 2:
				return Error('Deassignment With Expression', '=!', 2)
			else:
				return (Hierarchy.Assignment, [symbol], 2, 0)
		else:
			return (Hierarchy.Assignment, [symbol, parseHierarchy(characters[2:], start=2)], characters[1]['code']-50, 0)

	if Hierarchy.Ternary >= minHierarchy:
		searchTernary = [c for c in outer if c['code'] in range(33, 35)]
		if searchTernary:
			if searchTernary[0]['code'] == 33:
				binaryCounter = 1
				for t in searchTernary[1:]:
					if t['code'] == 33:
						binaryCounter += 1
					else:
						binaryCounter -= 1
						if binaryCounter == 0:
							return (Hierarchy.Ternary, [
								parseHierarchy(
									characters[:searchTernary[0]['ind'] - start],
									start=start, stop=searchTernary[0]['ind'], minHierarchy=minHierarchy, outer=outer
								) if searchTernary[0]['ind'] > start else (Hierarchy.Arithmetic, [(Hierarchy.Die, [
									(Hierarchy.Number, Fraction(0), 0, 0),
									(Hierarchy.Number, Fraction(1), 0, 0),
									(Hierarchy.Number, Fraction(2), 0, 0)
								], 0, 0), (Hierarchy.Number, Fraction(1), 0, 0)], 0, [0]),
								parseHierarchy(
									characters[searchTernary[0]['ind'] - start + 1:t['ind'] - start],
									start=searchTernary[0]['ind']+1, stop=t['ind'], minHierarchy=minHierarchy, outer=outer
								) if t['ind'] > searchTernary[0]['ind'] + 1 else (Hierarchy.Number, Fraction(1), 0, 0),
								parseHierarchy(
									characters[t['ind'] - start + 1:],
									start=t['ind'] + 1, stop=stop, minHierarchy=minHierarchy, outer=outer
								) if t['ind'] + 1 < stop else (Hierarchy.Number, Fraction(0), 0, 0)
							], 0, 0)
				return Error('Unclosed Ternary', '?', searchTernary[-1]['ind'])
			else:
				return Error('Unopened Ternary', ':', searchTernary[0]['ind'])
		else:
			minHierarchy = Hierarchy.Ternary

	if Hierarchy.Logical >= minHierarchy:
		searchLogical = [c for c in outer if c['code'] in range(30, 32)]
		if searchLogical:
			return (Hierarchy.Logical, [
				parseHierarchy(
					characters[:searchLogical[0]['ind'] - start],
					start=start, stop=searchLogical[0]['ind'], minHierarchy=minHierarchy, outer=outer
				),
				parseHierarchy(
					characters[searchLogical[0]['ind'] - start + 1:],
					start=searchLogical[0]['ind'] + 1, stop=stop, minHierarchy=minHierarchy, outer=outer
				)
			], 31 - searchLogical[0]['code'], 0)
		else:
			minHierarchy = Hierarchy.Logical

	if Hierarchy.Comparison >= minHierarchy:
		searchComparison = [c for c in outer if c['code'] in range(20, 26)]
		if searchComparison:
			return (Hierarchy.Comparison, [
				parseHierarchy(
					characters[a['ind'] - start + 1 : b['ind'] - start],
					start=a['ind'] + 1, stop=b['ind'], minHierarchy=minHierarchy, outer=outer
				)
				for a, b in zip([{'ind': start - 1}] + searchComparison, searchComparison + [{'ind': stop}])
			], 0, [
				a['code'] - 20
				for a in searchComparison
			])
		else:
			minHierarchy = Hierarchy.Comparison

	if Hierarchy.Arithmetic >= minHierarchy:
		searchArithmetic = [None]*3
		for i in range(3):
			searchArithmetic[i] = [c for c in outer if c['code'] in range(10 + 2*i, 12 + 2*i)]
			if len(searchArithmetic[i]) and searchArithmetic[i][0]['ind'] == start and searchArithmetic[i][0]['code'] == 11:
				searchArithmetic[i].pop(0)
			if searchArithmetic[i]:
				return (Hierarchy.Arithmetic, [
					parseHierarchy(
						characters[a['ind'] - start + 1:b['ind'] - start],
						start=a['ind'] + 1, stop=b['ind'], minHierarchy=minHierarchy, outer=outer
					)
					for a, b in zip([{'ind': start - 1}] + searchArithmetic[i], searchArithmetic[i] + [{'ind': stop}])
				], i, [
					2*i + 11 - a['code']
					for a in searchArithmetic[i]
				])
			else:
				minHierarchy = Hierarchy.Arithmetic

	if Hierarchy.Inversion >= minHierarchy:
		if len(characters) and characters[0]['code'] == 32:
			return (Hierarchy.Inversion, [parseHierarchy(characters[1:], start=start+1, stop=stop, minHierarchy=minHierarchy, outer=outer)], 0, 0)
		else:
			minHierarchy = Hierarchy.Inversion

	if Hierarchy.Modular >= minHierarchy:
		searchModular = [c for c in outer if c['code'] == 16]
		if searchModular:
			return (Hierarchy.Modular, [
				parseHierarchy(
					characters[:searchModular[0]['ind'] - start],
					start=start, stop=searchModular[0]['ind'], minHierarchy=minHierarchy, outer=outer
				),
				parseHierarchy(
					characters[searchModular[0]['ind'] - start + 1:],
					start=searchModular[0]['ind'] + 1, stop=stop, minHierarchy=minHierarchy, outer=outer
				)
			], 0, 0)
		else:
			minHierarchy = Hierarchy.Modular

	if Hierarchy.Negation >= minHierarchy:
		if len(characters) and characters[0]['code'] == 11:
			return (Hierarchy.Negation, [parseHierarchy(characters[1:], start=start+1, stop=stop, minHierarchy=minHierarchy, outer=outer)], 0, 0)
		else:
			minHierarchy = Hierarchy.Negation

	if Hierarchy.Die >= minHierarchy:
		searchDie = [c for c in outer if c['code'] in range(60, 63)]
		if searchDie:
			if searchDie[0]['code'] == 60:
				return (Hierarchy.Die, [
					(Hierarchy.Number, Fraction(0), 0, 0),
					parseHierarchy(
						characters[:searchDie[0]['ind'] - start],
						start=start, stop=searchDie[0]['ind'], minHierarchy=minHierarchy, outer=outer
					) if searchDie[0]['ind'] > start else (Hierarchy.Number, Fraction(1), 0, 0),
					parseHierarchy(
						characters[searchDie[0]['ind'] - start + 1:],
						start=searchDie[0]['ind'] + 1, stop=stop, minHierarchy=minHierarchy, outer=outer
					) if searchDie[0]['ind'] + 1 < stop else (Hierarchy.Number, Fraction(20), 0, 0)
				], 0, 0)
			else:
				binaryCounter = 1
				for d in searchDie[1:]:
					if d['code'] == 60:
						binaryCounter -= 1
						if binaryCounter == 0:
							return (Hierarchy.Die, [
								parseHierarchy(
									characters[:searchDie[0]['ind'] - start],
									start=start, stop=searchDie[0]['ind'], minHierarchy=minHierarchy, outer=outer
								) if searchDie[0]['ind'] > start else (Hierarchy.Number, Fraction(1), 0, 0),
								parseHierarchy(
									characters[searchDie[0]['ind'] - start + 1:d['ind'] - start],
									start=searchDie[0]['ind']+1, stop=d['ind'], minHierarchy=minHierarchy, outer=outer
								) if d['ind'] > searchDie[0]['ind'] + 1 else (Hierarchy.Number, Fraction(2), 0, 0),
								parseHierarchy(
									characters[d['ind'] - start + 1:],
									start=d['ind'] + 1, stop=stop, minHierarchy=minHierarchy, outer=outer
								) if d['ind'] + 1 < stop else (Hierarchy.Number, Fraction(20), 0, 0)
							], 123-2*searchDie[0]['code'], 0)
					else:
						binaryCounter += 1
				return Error('Unclosed Die', '@', searchDie[-1]['ind'])
		else:
			minHierarchy = Hierarchy.Die

	if Hierarchy.Number >= minHierarchy:
		if len(characters) == 1 and characters[0]['charset'] == 1:
			return (Hierarchy.Number, Fraction(characters[0]['text']), 0, 0)
		else:
			minHierarchy = Hierarchy.Number

	if len(outer):
		return Error('Unrecognized Expression', '', start)
	elif len(characters):
		return Error('Unrecognized Characters', '', start)
	else:
		return Error('No Characters', '', start)

def parseHierarchyErrors (hierarchy):
	out = []
	if isinstance(hierarchy, Error):
		out.append(hierarchy)
	elif hierarchy[0] < Hierarchy.Number:
		for i in hierarchy[1]:
			out.extend(parseHierarchyErrors(i))
	return out

class Expression (abstract_base_class):
	def __init__ (self, hierarchy):
		self.hierarchy, self.components, self.level, self.signs = hierarchy

	@abstractmethod
	def evaluate (self, components): pass

	def instance (self):
		return self.evaluate([c.instance() for c in self.components])

	def plot (self):
		counter = Counter()
		for combination in itertools_product(c.plot().most_common() for c in self.components):
			counter[self.evaluate(c[0] for c in combination)] += functools_reduce(operator_mul, [c[1] for c in combination])
		return counter

	def insert (self, component):
		wrap = self.level >= component.level if self.hierarchy == component.hierarchy == Hierarchy.Arithmetic else self.hierarchy >= component.hierarchy
		return ('(' if wrap else '') + str(component) + (')' if wrap else '')

class ExpressionTernary (Expression):
	def __init__ (self, hierarchy): super().__init__(hierarchy)

	def evaluate (self, components = None):
		return components[1] if components[0] else components[2]

	def __repr__ (self):
		return self.insert(self.components[0]) + ' ? ' + self.insert(self.components[1]) + ' : ' + self.insert(self.components[2])

class ExpressionLogical (Expression):
	def __init__ (self, hierarchy): super().__init__(hierarchy)

	def evaluate (self, components = None):
		return Fraction(components[0] and components[1]) if self.level else Fraction(components[0] or components[1])

	def __repr__ (self):
		return self.insert(self.components[0]) + (' & ' if self.level else ' | ') + self.insert(self.components[1])

class ExpressionComparison (Expression):
	def __init__ (self, hierarchy): super().__init__(hierarchy)

	def evaluate (self, components = None):
		return Fraction(all((s in [0,4,5] if a == b else (s in [1,2,4] if a > b else s in [1,3,5])) for a, b, s in zip(components, components[1:], self.signs)))

	reprOperator = (' == ', ' != ', ' > ', ' < ', ' >= ', ' <= ')

	def __repr__ (self):
		return ''.join(i for i in itertools_chain.from_iterable(itertools_zip_longest(
			[self.insert(c) for c in self.components], [ExpressionComparison.reprOperator[s] for s in self.signs]
		)) if i)

class ExpressionArithmetic (Expression):
	def __init__ (self, hierarchy): super().__init__(hierarchy)

	rducOperator = (operator_add, operator_mul, lambda a, b: operator_pow(b, a))
	flipOperator = (lambda a: -1*a, lambda a: 1/a, lambda a: 1/a)
	reprOperator = (' - ', ' + ', '/', '*', '*/', '**')

	def evaluate (self, components = None):
		return functools_reduce(
			ExpressionArithmetic.rducOperator[self.level],
			[c if s else ExpressionArithmetic.flipOperator[self.level](c) for c, s in zip(components[::-1], self.signs[::-1]+[True])]
		)

	def __repr__ (self):
		return ''.join(i for i in itertools_chain.from_iterable(itertools_zip_longest(
			[self.insert(c) for c in self.components], [ExpressionArithmetic.reprOperator[2*self.level+s] for s in self.signs]
		)) if i)

class ExpressionInversion (Expression):
	def __init__ (self, hierarchy): super().__init__(hierarchy)

	def evaluate (self, components = None):
		return Fraction(not components[0])

	def __repr__ (self):
		return '!'+self.insert(self.components[0])

class ExpressionModular (Expression):
	def __init__ (self, hierarchy): super().__init__(hierarchy)

	def evaluate (self, components = None):
		return components[0] % components[1]

	def __repr__ (self):
		return self.insert(self.components[0]) + '%' + self.insert(self.components[1])

class ExpressionNegation (Expression):
	def __init__ (self, hierarchy): super().__init__(hierarchy)

	def evaluate (self, components = None):
		return -1*components[0]

	def __repr__ (self):
		return '-'+self.insert(self.components[0])

class ExpressionDie (Expression):
	def __init__ (self, hierarchy): super().__init__(hierarchy)

	def evaluate (self, components = None):
		die = [random_randint(1, components[2]) for _ in range(int(components[1]))]
		return sum(sorted(die)[
			(-self.level*int(components[0]) if self.level*components[0] > 0 else None):(-self.level*int(components[0]) if self.level*components[0] < 0 else None)
		])

	def __repr__ (self):
		if self.components[0].hierarchy == Hierarchy.Number and self.components[0].components == 0:
			return self.insert(self.components[1]) + 'd' + self.insert(self.components[2])
		else:
			return self.insert(self.components[0]) + ('@' if self.level == 1 else '!@') + self.insert(self.components[1]) + 'd' + self.insert(self.components[2])

class ExpressionNumber (Expression):
	def __init__ (self, hierarchy): super().__init__(hierarchy)

	def evaluate (self, components = None):
		return self.components

	def __repr__ (self):
		return str(self.components)

	def instance (self):
		return self.components

Expressions = {
	Hierarchy.Ternary: ExpressionTernary,
	Hierarchy.Logical: ExpressionLogical,
	Hierarchy.Comparison: ExpressionComparison,
	Hierarchy.Arithmetic: ExpressionArithmetic,
	Hierarchy.Inversion: ExpressionInversion,
	Hierarchy.Modular: ExpressionModular,
	Hierarchy.Negation: ExpressionNegation,
	Hierarchy.Die: ExpressionDie,
	Hierarchy.Number: ExpressionNumber
}

def parseExpression (hierarchy):
	if isinstance(hierarchy[1], Fraction):
		return Expressions[hierarchy[0]](hierarchy)
	else:
		hierarchy[1][:] = [parseExpression(h) for h in hierarchy[1]]
		return Expressions[hierarchy[0]](hierarchy)

def parse (text):
	characters = parseCharacters(text)
	if len(characters) == 0:
		return Error('No Characters', '', 0)
	elif isinstance(characters[0], Error):
		return characters
	else:
		hierarchy = parseHierarchy(characters, statement=True)
		hierarchyErrors = parseHierarchyErrors(hierarchy)
		if len(hierarchyErrors):
			return hierarchyErrors
		elif hierarchy[0] == Hierarchy.Assignment:
			print(hierarchy[1][0], hierarchy[2])
			return parseExpression(hierarchy[1][1])
		else:
			return parseExpression(hierarchy)

x = parse('abc = 3')

print(x)
if isinstance(x, Expression):
	print(x.instance())