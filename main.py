#!/usr/bin/python3
from termcolor import colored
import server_communication as sc

# Prints a representation of the maze in the terminal window.
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
	""" Represents a cell and keeps track of it's value (' ', 'X', 'A' or 'B') and whether the cell has been stepped on before. """
	def __init__(self, value):
		self.value = value
		self.stepped_on = False

	def mark_as_stepped(self):
		self.stepped_on = True

	def __str__(self):
		return '(\'{}\', {})'.format(self.value, self.stepped_on)

	def __repr__(self):
		return self.__str__()

class coordinate:
	""" Stores the coordinate's x and y components. """
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __str__(self):
		return '({}, {})'.format(self.x, self.y)

	def __repr__(self):
		return self.__str__()

	def copy(self):
		return coordinate(self.x, self.y)

class fork:
	"""
	Stores a fork's information, otherwise known as a crossroad.
	When the algorithm finds itself in front of multiple possible paths,
	it will store the corresponding coordinates and the number of steps
	it has taken to get there from the starting position,
	which will be needed to reconstruct the move_log in the future
	without having to store the actual string itself in case you need
	to go back.
	"""
	def __init__(self, coord, n_steps):
		self.coord = coord
		self.n_steps = n_steps

	def __str__(self):
		return '({}, {})'.format(self.coord, self.n_steps)

	def __repr__(self):
		return self.__str__()


class maze:
	"""
	A class designed to move around within it,
	get information about the cells and keep track of the movements,
	so we can know the path we have taken when we find the exit cell,
	thus getting the solution to the maze.
	The first cell is (1, 1), not (0, 0).
	"""
	def __init__(self, baremap):
		self.map = [[cell(c) for c in row] for row in baremap] # The whole maze's grid.
		self.cur = self.start_coordinates() # The cursor, to keep track about the current position.
		self.read_cur().mark_as_stepped() # Marks the current cell as a cell we have already stepped on.
		self.move_log = ''
		self.forks = []

	# Get the start coordinates by getting them from the server_communication file.
	def start_coordinates(self):
		return coordinate(sc.starting_coordinates[0] + 1, sc.starting_coordinates[1] + 1)

	# Look up the coordinate's info from the map.
	def get_by_coordinates(self, coord):
		try:
			if coord.y < 1 or coord.x < 1:
				raise IndexError
			return self.map[coord.y - 1][coord.x - 1]
		except IndexError:
			return cell('X')

	def read_cur(self):
		return self.get_by_coordinates(self.cur)

	# The methods here below all have one purpose: to check the nearest cells' infos.
	# The only differences are the direction in which you are 'looking'.

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

	# The methods here below all have one purpose: to move to the nearest cells.
	# Once again, the only differences are the directions.

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

	# Invokes the correct method based on the direction argument.
	def move(self, direction):
		if direction == 'E':
			self.move_e()
		elif direction == 'S':
			self.move_s()
		elif direction == 'W':
			self.move_w()
		else:
			self.move_n()

	# Returns all the remaining paths to explore for the current position.
	def remaining_paths(self):
		paths = {'E': self.peek_e(), 'S': self.peek_s(), 'W': self.peek_w(), 'N': self.peek_n()}
		return [key for key, dict_value in paths.items() if dict_value.value != 'X' and not dict_value.stepped_on]

	# Logs the current position as a fork.
	def log_fork(self):
		self.forks.append(fork(self.cur.copy(), len(self.move_log)))

	# Reverts the object to the last fork in the list, then deletes it from the forks list.
	def revert_to_last_fork(self):
		fork = self.forks[-1]
		self.cur = fork.coord
		# By knowing how many steps we had taken until the most recent fork
		# we can keep the same number of steps and discard those that come after
		# to revert to the old move_log.
		self.move_log = self.move_log[:fork.n_steps]
		del self.forks[-1]

def main():
	showmaze()
	m = maze(sc.baremap)
	# We keep going until we find the exit cell.
	while m.read_cur().value != 'B':
		paths = m.remaining_paths()
		n_paths = len(paths)
		# If there are multiple paths we have not explored yet, it's a fork.
		if n_paths > 1:
			m.log_fork()
		# If there are no paths, it's a dead end and we need to go back to the oldest fork.
		elif n_paths == 0:
			m.revert_to_last_fork()
			continue
		# Whether this is a fork or not, as long as there is a path we move toward a cell we have not stepped on before.
		m.move(paths[0])
	print('Solution:', m.move_log)

if __name__ == '__main__':
	main()