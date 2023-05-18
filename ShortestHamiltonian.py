# imports
import numpy as np
import pygame
import time
from datetime import datetime

# pygame init
modifier = 1.5
pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Calibri', 16)
screen = pygame.display.set_mode((500*modifier, 500*modifier))
clock = pygame.time.Clock()
screen.fill('white')

# default vars
debug = False # debug
debugStart = False # debug at start (print default vars)
debugTimer = 0 # how long to wait at debug points
includeEnd = False # include end to start distance
inp = False
if inp:
	n_points = int(input("number of nodes:\n- ")) # number of nodes
else:
	n_points = 15
points = np.random.rand(n_points, 2)
n_ants = 5 # number of ants
alpha = 1 # how strictly it follows pheromones (1 = lenient)
beta = 1 # how much it desires close nodes (1 = don't care)
evaporation_rate = 0.5 # amount pheremone evaporates each iteration
if debugStart:
	print(evaporation_rate)
	print(beta)
	print(alpha)
	print(n_ants)
Q = 1 # amount pheromone increases on good route
running = True
tickTime = 600 # how many frames per second for display
border = 20 # pixels from edge

# calculate fps
def fps(start, end):
	return end-start

# distance function
def distance(point1, point2):
	return np.sqrt(np.sum((point1 - point2)**2))

# ant
class Ant:
	# init
	def __init__(self, n_points, points, alpha, beta):
		self.nodes = points
		self.alpha = alpha
		self.beta = beta
		self.activeNode = np.random.randint(n_points)
		self.visited = [False]*n_points
		self.visited[self.activeNode] = True
		self.path = [self.activeNode]
		self.path_length = 0
		self.disabled = False

	def reset(self, n_points):
		self.activeNode = np.random.randint(n_points)
		self.visited = [False]*n_points
		self.visited[self.activeNode] = True
		self.path = [self.activeNode]
		self.path_length = 0

	def new(self, pheromone):
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
		self.activeNode = new_node

	def able(self):
		self.disabled = not self.disabled

	def report(self):
		return self.disabled

	def move(self, pheromone):
		if debug:
			print(self.visited)
		if False in self.visited:
			if not self.disabled:
				self.new(pheromone)
				return True
		if False not in self.visited:
			if not self.disabled:
				self.able()
				if includeEnd:
					start = np.array([self.nodes[self.path[0]][0], self.nodes[self.path[0]][-1]])
					end = np.array([self.nodes[self.path[-1]][0], self.nodes[self.path[-1]][-1]])
					self.path_length += distance(start, end)
				return [self.path, self.path_length]
		return None

# main
class main:
	# init
	def __init__(self, points, screen, alpha, beta, Q, evaporation_rate):
		self.screen = screen
		self.n_points = len(points)
		self.points = points
		self.pheromone = np.ones((n_points, n_points))
		self.evaporation_rate = evaporation_rate
		self.best_path = None
		self.best_path_length = np.inf
		self.ants = []
		self.Q = Q
		for ant in range(n_ants):
			self.ants.append(Ant(self.n_points, self.points, alpha, beta))
		self.update(True)

	def update(self, first=False):
		if not first:
			# self.pheromone[self.pheromone < 0.0001] = 0.001
			self.move_ants()
		antNode = []
		for ant in self.ants:
			antNode.append(ant.activeNode)
		for nod in range(len(self.points)):
			node = self.points[nod]
			if debug:
				print(antNode)
				print(node)
			color = 'red' if nod in antNode else 'black'
			start = node[0]*(500*modifier-border*2)+border
			end = node[-1]*(500*modifier-border*2)+border
			pygame.draw.circle(self.screen, color, (int(start), int(end)), 5)

        # TODO create RGB colour from 128,0,0 to 255,128,128, where you scale
        # the 0 to 255 based on the position in the list. (or 0-1 if that's how it works)
		if self.best_path:
			if debug:
				print(self.pheromone)
				print('best_path')
			start = self.best_path[0]
			for node in self.best_path[1:]:
				if debug:
					print(node)
				start = tuple(self.points[start]*(500*modifier-border*2)+border)
				end = tuple(self.points[node]*(500*modifier-border*2)+border)
				if debug:
					print(type(start))
					print(start)
					print(end)
				pygame.draw.line(self.screen, 'red', start, end, width=5)
				start = node
			start = tuple(self.points[self.best_path[-1]]*(500*modifier-border*2)+border)
			end = tuple(self.points[self.best_path[0]]*(500*modifier-border*2)+border)
			pygame.draw.line(self.screen, 'red', start, end, width=5)
		return self.best_path_length

	# iterate through ant list for ant objects, and move each to a new node based on pheromones
	def move_ants(self):
		if debug:
			print('moving ants')
		paths = []
		path_lengths=[]
		count = 1
		for ant in self.ants:
			if debug:
				print('moving ant '+str(count))
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


if __name__ == '__main__':
	m = main(points, screen, alpha, beta, Q, evaporation_rate)
	if debug:
		print(repr(points))
		for point in points:
			print(repr(point*(500-border)+border))
	while running:
		# start = datetime.now()
		for event in pygame.event.get():
			if event.type== pygame.QUIT:
				running = False
		screen.fill((255, 255, 255))
		FPS = m.update()
		time.sleep(debugTimer)
		# end = datetime.now()
		# FPS = fps(start, end)
		# try:
			# FPS = round(1/float(str(FPS.seconds)+'.'+str(FPS.microseconds)),0)
		# except:
			# FPS = 0
		ts = font.render(f"shortest length: {round(FPS, 2)} km", False, "black")
		screen.blit(ts, (0.01*500*modifier, 0.01*500*modifier))
		pygame.display.flip()
		clock.tick(tickTime)
	pygame.quit()
