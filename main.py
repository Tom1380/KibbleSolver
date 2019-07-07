#!/usr/bin/python3
from termcolor import colored
import server_communication as sc

def showmaze():
	for row in sc.baremap:
		print('            ', end = '')
		for cell in row:
			if cell == 'X':
				print(colored('X ', 'red'), end = '')
			elif cell == ' ':
				print(colored('O ', 'white'), end = '')
			elif cell == 'B':
				print(colored('B ', 'green'), end = '')
			else:
				print(colored('A ', 'blue'), end = '')
		print()

class cell:
	def __init__(self, value):
		self.value = value
		self.stepped_on = False

	def mark_as_stepped(self):
		self.stepped_on = True

	def __str__(self):
		return '(\'{}\', {})'.format(self.value, self.stepped_on)
		
class coordinate:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __str__(self):
		return '({}, {})'.format(self.x, self.y)

	def copy(self):
		return coordinate(self.x, self.y)
		
class maze:
	def __init__(self, baremap):
		self.map = [[cell(c) for c in row] for row in baremap]
		self.cur = self.start_coordinates()
		self.read_cur().mark_as_stepped()
		self.size = len(baremap)
		self.move_log = ''

	def start_coordinates(self):
		for y, row in enumerate(self.map):
			for x, cell in enumerate(row):
				if cell.value == 'A':
					return coordinate(x + 1, y + 1)

	def get_by_coordinates(self, coord):
		try:
			if coord.y < 1 or coord.x < 1:
				raise IndexError
			return self.map[coord.y - 1][coord.x - 1]
		except IndexError:
			return cell('X')

	def read_cur(self):
		return self.get_by_coordinates(self.cur)

	def peek_n(self):
		north = self.cur.copy()
		north.y -= 1
		return self.get_by_coordinates(north)

	def peek_e(self):
		east = self.cur.copy()
		east.x += 1
		return self.get_by_coordinates(east)

	def peek_s(self):
		south = self.cur.copy()
		south.y += 1
		return self.get_by_coordinates(south)

	def peek_w(self):
		west = self.cur.copy()
		west.x -= 1
		return self.get_by_coordinates(west)

	def move_n(self):
		self.move_log += 'N'
		north = self.cur
		north.y -= 1
		value = self.get_by_coordinates(north).value
		assert(value != 'X')
		self.cur = north
		self.read_cur().mark_as_stepped()

	def move_e(self):
		self.move_log += 'E'
		east = self.cur
		east.x += 1
		value = self.get_by_coordinates(east).value
		assert(value != 'X')
		self.cur = east
		self.read_cur().mark_as_stepped()

	def move_s(self):
		self.move_log += 'S'
		south = self.cur
		south.y += 1
		value = self.get_by_coordinates(south).value
		assert(value != 'X')
		self.cur = south
		self.read_cur().mark_as_stepped()

	def move_w(self):
		self.move_log += 'W'
		west = self.cur
		west.x -= 1
		value = self.get_by_coordinates(west).value
		assert(value != 'X')
		self.cur = west
		self.read_cur().mark_as_stepped()

showmaze()
m = maze(sc.baremap)