# imports
import numpy as np
import pyglet
from pyglet.window import key
from pyglet import shapes
import time
from numba import jit, cuda
from timeit import default_timer as timer
from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
import warnings

warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)

# pyglet init
width = 750
height = 750
title = 'ant simulation'
screen = pyglet.window.Window(width, height, title)
font = ['Calibri', 12]
screenBorder = 15
border = 20
fontloc = (0.01*screen.width, screen.height-0.01*screen.height-screenBorder)
anchor_x = ['left', 'center', 'right']
anchor_y = ['top', 'center', 'bottom', 'baseline']
batch = pyglet.graphics.Batch()

def lab(text):
	label = pyglet.text.Label(text,
							font_name=font[0],
							font_size=font[1],
							x=fontloc[0], y=fontloc[1],
							anchor_x=anchor_x[0], anchor_y=anchor_y[2])
	label.draw()

# default vars
debug = False
debugStart = False
debugTimer = 0
includeEnd = False
inp = False
if inp:
	n_points = int(input("number of nodes:\n- "))
else:
	n_points = 250
global points
if n_points > 0:
	points = np.random.rand(n_points, 2)
else:
	points = None
print(type(points))
n_ants = 10
alpha = 1
beta = 1
evaporation_rate = 0.5
if debugStart:
	print(evaporation_rate)
	print(beta)
	print(alpha)
	print(n_ants)
Q = 1


def fps(start, end):
	return end-start

def distance(point1, point2):
	return np.sqrt(np.sum((point1 - point2)**2))

class Ant:
	def __init__(self, n_points, points, alpha, beta):
		# print(n_points)
		self.nodes = points
		self.alpha = alpha
		self.beta = beta
		if n_points > 0:
			self.activeNode = np.random.randint(n_points)
		else:
			self.activeNode = None
		self.visited = [False]*n_points
		if isinstance(self.activeNode, np.int64) or isinstance(self.activeNode, int):
			self.visited[self.activeNode] = True
			self.path = [self.activeNode]
		else:
			self.visited = None
			self.path = None
		self.path_length = 0
		self.disabled = False
		self.batch = pyglet.graphics.Batch()

	def reset(self, n_points):
		if n_points > 0:
			self.activeNode = np.random.randint(n_points)
		else:
			self.activeNode = None
		self.visited = [False]*n_points
		if isinstance(self.activeNode, np.int64) or isinstance(self.activeNode, int):
			self.visited[self.activeNode] = True
			self.path = [self.activeNode]
		else:
			self.visited = None
			self.path = None
		self.path_length = 0

	@jit
	def new(self, pheromone):
		if isinstance(self.activeNode, np.int64) or isinstance(self.activeNode, int):
			unvisited = np.where(np.logical_not(self.visited))[0]
			probabilities = np.zeros(len(unvisited))

			for i, unvisited_node in enumerate(unvisited):
				start = np.array([self.nodes[self.activeNode][0], self.nodes[self.activeNode][1]])
				end = np.array([self.nodes[unvisited_node][0], self.nodes[unvisited_node][1]])
				probabilities[i] = pheromone[self.activeNode, unvisited_node]**self.alpha / distance(start, end)**self.beta

			probabilities /= np.sum(probabilities)

			new_node = np.random.choice(unvisited, p=probabilities)

			if debug:
				print(new_node)
				print(self.visited[new_node])
				print(f'has visited new_node {self.visited[new_node]}')

			self.path.append(new_node)
			start = np.array([self.nodes[self.activeNode][0], self.nodes[self.activeNode][1]])
			end = np.array([self.nodes[new_node][0], self.nodes[new_node][1]])
			self.path_length += distance(start, end)
			self.visited[new_node] = True
			if debug:
				print('activeNode = '+str(self.activeNode))
				print('new_node = '+str(new_node))
			self.activeNode = new_node
		else:
			if debug:
				pass
			print('activeNode is not available')

	def able(self):
		self.disabled = not self.disabled

	def report(self):
		return self.disabled

	def draw_path(self):
		start = self.path[0]
		l = []
		for node in self.path[1:]:
			if debug:
				print(node)
			start = tuple(self.nodes[start]*(screen.width-border*2)+border)
			end = tuple(self.nodes[node]*(screen.height-border*2)+border)
			if debug:
				print(type(start))
				print(start)
				print(end)
			l.append(shapes.Line(start[0], start[1], end[0], end[1], width=2, color=(250,250,250), batch=self.batch))
			l[-1].opacity = 15
			start = node
		start = tuple(self.nodes[self.path[-1]]*(screen.width-border*2)+border)
		end = tuple(self.nodes[self.path[0]]*(screen.height-border*2)+border)
		l .append(shapes.Line(start[0], start[1], end[0], end[1], width=2, color=(250,250,250), batch=self.batch))
		l[-1].opacity = 15
		self.batch.draw()

	def move(self, pheromone):
		if (isinstance(self.activeNode, np.int64) or isinstance(self.activeNode, int)) and len(self.nodes) > 2:
			if debug:
				print(self.visited)
			if False in self.visited:
				if not self.disabled:
					self.new(pheromone)
					# self.draw_path()
					if debug:
						print('creating path')
					return True
			if False not in self.visited:
				if not self.disabled:
					self.able()
					if includeEnd:
						start = np.array([self.nodes[self.path[0]][0], self.nodes[self.path[0]][-1]])
						end = np.array([self.nodes[self.path[-1]][0], self.nodes[self.path[-1]][-1]])
						self.path_length += distance(start, end)
					if debug:
						print('end of path')
					return [self.path, self.path_length]
			if debug:
				print('not enabled')
			return None
		else:
			if debug:
				print(repr(self.activeNode))
				print(type(self.activeNode))
				print('activeNode not int')
			return True

class main:
	def __init__(self, points, screen, alpha, beta, Q, evaporation_rate):
		self.screen = screen
		if isinstance(points, np.ndarray):
			self.n_points = len(points)
		else:
			self.n_points = 0
		self.points = points
		self.pheromone = np.ones((self.n_points, self.n_points))
		self.evaporation_rate = evaporation_rate
		self.best_path = None
		self.best_path_length = np.inf
		self.ants = []
		self.Q = Q
		for ant in range(n_ants):
			self.ants.append(Ant(self.n_points, self.points, alpha, beta))
		self.update(True)

	def reset(self):
		self.best_path = None
		self.best_path_length = np.inf
		self.pheromone = np.ones((self.n_points, self.n_points))

	def update(self, first=False):
		if not first:
			self.move_ants()
		antNode = []
		for ant in self.ants:
			antNode.append(ant.activeNode)
		s = []
		if isinstance(self.points, np.ndarray):
			for nod in range(len(self.points)):
				node = self.points[nod]
				if debug:
					print(antNode)
					print(node)
				color = 'red' if nod in antNode else 'black'
				start = node[0]*(self.screen.width-border*2)+border
				end = node[-1]*(self.screen.height-border*2)+border
				color = (255,0,0) if nod in antNode else (255,255,255)
				s.append(shapes.Circle(start, end, 10, color=color, batch=batch))
				s[-1].opacity = 250

		if self.best_path:
			if debug:
				print(self.pheromone)
				print('best_path')
			start = self.best_path[0]
			# print(start)
			l = []
			for node in self.best_path[1:]:
				if debug:
					print(node)
				start = tuple(self.points[start]*(screen.width-border*2)+border)
				end = tuple(self.points[node]*(screen.height-border*2)+border)
				if debug:
					print(type(start))
					print(start)
					print(end)
				l.append(shapes.Line(start[0], start[1], end[0], end[1], width=2, color=(255,0,0), batch=batch))
				l[-1].opacity = 250
				start = node
			start = tuple(self.points[self.best_path[-1]]*(screen.width-border*2)+border)
			end = tuple(self.points[self.best_path[0]]*(screen.height-border*2)+border)
			l .append(shapes.Line(start[0], start[1], end[0], end[1], width=2, color=(255,0,0), batch=batch))
			l[-1].opacity = 250
		batch.draw()
		return self.best_path_length

	def update_nodes(self, points):
		self.points = points
		self.n_points = len(points)
		self.ants = []
		for ant in range(n_ants):
			self.ants.append(Ant(self.n_points, self.points, alpha, beta))
			self.ants[-1].reset(self.n_points)
		self.reset()
		# self.update(True)

	@jit
	def move_ants(self):
		if debug:
			print('moving ants')
		paths = []
		path_lengths = []
		count = 1
		for ant in self.ants:
			if debug:
				print('moving ant '+str(count))
				print(self.pheromone)
			moves = ant.move(self.pheromone)
			if moves == None:
				continue
			if isinstance(moves, list):
				ant.reset(self.n_points)
				paths.append(moves[0])
				path_lengths.append(moves[1])
				if moves[1] < self.best_path_length:
					self.best_path = moves[0]
					self.best_path_length = moves[1]
			count += 1
		count = 0
		for ant in self.ants:
			if ant.report():
				if debug:
					print('disabled')
				count += 1

		if debug:
			print(count, len(self.ants))
		if count >= len(self.ants):
			for ant in self.ants:
				if debug:
					print('enable')
				ant.able()
			if debug:
				print('evaporate')
			self.pheromone *= self.evaporation_rate
			for path, path_length in zip(paths, path_lengths):
				if debug:
					print('enforce')
				for i in range(self.n_points-1):
					self.pheromone[path[i], path[i+1]] += self.Q/path_length
				self.pheromone[path[-1], path[0]] += self.Q/path_length

m = main(points, screen, alpha, beta, Q, evaporation_rate)
batch.draw()

def reset():
	m.reset()

# on draw handler
@screen.event
@jit
def on_draw():
	screen.clear()
	l = m.update()
	lab(str(round(l,2))+' km')

@screen.event
def on_key_press(symbol, modifiers):
	if symbol == key.ENTER:
		reset()

@screen.event
def on_mouse_press(x, y, button, modifiers):
	global points
	if button == pyglet.window.mouse.LEFT:
		new_point = np.array([[(x-border)/(screen.width-border*2), (y-border)/(screen.height-border*2)]])
		if isinstance(points, np.ndarray):
			points = np.append(points, new_point, axis=0)
		else:
			points = new_point
		m.update_nodes(points)

pyglet.app.run()