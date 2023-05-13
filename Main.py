# imports
import random
import pygame
import time

# pygame init
pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Calibri', 10)

debug = False
debugTimer = 0
modifier = 1
nodes = 10
cell_size = 10
border = 10
desire = 2
pheroPower = 2
screen = pygame.display.set_mode((500*modifier,500*modifier))
screen.fill("white")
clock = pygame.time.Clock()
running = True

# main class
class Main:
	# init
	def __init__(self, display, num_nodes, modifier, cell_size, border):
		self.modifier = modifier
		self.border = border
		self.display = display
		self.unVisited = []
		self.visited = []
		self.history = []
		self.idealConns = []
		self.best = 1000000000000
		# generate list of random points to display in a pygame window
		self.nodes = {}
		self.cell_size = cell_size
		self.genList(num_nodes)

		# generate dictionary of connections {'AD':45} with a length/time assigned to a connection
		# allows the ai to grab current code e.g. 'A' and append the test node, it will then select
		# a node with the ideal being the shortest but have a weight to allow others as well.
		# as the ideal path is discovered the weights for certain connections will increase
		self.activeConnections = self.nodes[list(self.nodes.keys())[0]]['connections']
		self.activeNode = list(self.nodes.keys())[0]

		for con_key in list(self.activeConnections.keys()):
			start = self.nodes[con_key.split('-')[0]]['location']
			end = self.nodes[con_key.split('-')[-1]]['location']
			pygame.draw.line(self.display, "black", start, end, width=int(round(self.activeConnections[con_key][0], 0)))

		for node in self.nodes:
			# print(repr(node))
			# print(repr(self.nodes[node]))
			col = "black" if node != self.activeNode else "red"
			pygame.draw.circle(self.display, col, self.nodes[node]['location'], 5)
			if node != self.activeNode and debug:
				ts = font.render(f"node {node} | {self.activeConnections[self.activeNode+'-'+node]}", False, "black")
				print((self.nodes[node]['location'][0]+30, self.nodes[node]['location']))
				self.display.blit(ts, (self.nodes[node]['location'][0]+10, self.nodes[node]['location'][1]))

		# TODO
		# print(repr(self.nodes))
		# print(repr(self.activeConnections))

	# generate list of nodes
	def genList(self, num_nodes):
		for i in range(num_nodes):
			while True:
				self.nodes[str(i)] = {}
				self.nodes[str(i)]['location'] = (random.randint(0,(50-self.border)*self.modifier*self.cell_size), random.randint(0,(50-self.border)*self.modifier*self.cell_size))
				if self.nodes[str(i)] in list(self.nodes.values())[:-1]:
					print("duplicate")
					continue
				else:
					# print("no dup")
					break
		for i in list(self.nodes.keys()):
			self.nodes[i]['connections'] = self.genConnections(i, 1)
		for node in self.nodes:
			self.unVisited.append(node)

	def genConnections(self, start_point, phero):
		connections = {}
		distance = {}
		for tmp in list(self.nodes.keys()):
			distance[tmp] = self.get_distance(self.nodes[start_point]['location'], self.nodes[tmp]['location'])

		for tmp in list(self.nodes.keys()):
			if tmp == start_point:
				continue
			connections[start_point+"-"+tmp] = [self.get_weights(distance[tmp], phero), distance[tmp]]
			if debug:
				print(connections[start_point+'-'+tmp])
		return connections

	def newAnt(self):
		candidates = {}
		for cand in self.unVisited:
			candidates[cand] = self.activeConnections[self.activeNode+'-'+cand]

		if debug:
			print(list(candidates.keys()))
			print(list(candidates.values()))
		AntLocation = random.choices(population=list(candidates.keys()), weights=list(c[0] for c in list(candidates.values())), k=1)
		if debug:
			print(repr(AntLocation))
			time.sleep(debugTimer)

		return AntLocation[0]

	def calculateFitness(self, nodes):
		total_len = 0
		newIdealConns = []
		start = nodes[0]
		for node in nodes[1:]:
			# print((start, node))
			# print(self.nodes[node]['connections'])
			# time.sleep(1)
			total_len += self.nodes[node]['connections'][node+'-'+start][1]
			start = node
		if debug:
			print(total_len)

		self.history.append(total_len)
		if total_len < self.best:
			self.best = total_len

		if self.best == total_len:
			start = nodes[0]
			for node in nodes[1:]:
				new = start+'-'+node
				ic = []
				ic.append(c[0] for c in self.idealConns)
				if new in ic:
					for c in self.idealConns:
						if c[0] == new:
							recur = c[1]
					recur += 0.1
				else:
					recur = 1
				newIdealConns.append([node+'-'+start, recur])
				start = node
		# else:
		# 	for c in self.idealConns:
		# 		# print(c[1])
		# 		newIdealConns.append([c[0], c[1]*1.1])
		# 	self.idealConns = newIdealConns
		self.idealConns = newIdealConns

	def cWeights(self, conns):
		ic = []
		ic.append(c[0] for c in self.idealConns)
		for conn in conns:
			if conn in ic:
				for c in self.idealConns:
					if c[0] == conn:
						recur = c[1]
				conns[conn][0] = self.get_weights(conns[conn][1], recur)
		# print(conns)
		return conns

	def update(self):
		# self.genList()
		# self.genConnections()
		# print(repr(self.nodes))
		# print(repr(self.connections))
		self.unVisited.pop(self.unVisited.index(self.activeNode))
		self.visited.append(self.activeNode)
		if len(self.unVisited) <= 0:
			self.calculateFitness(self.visited)
			self.activeNode = list(self.nodes.keys())[0]
			self.activeConnections = self.nodes[self.activeNode]['connections']
			self.unVisited = list(self.nodes.keys())
			self.unVisited.pop(self.unVisited.index(self.activeNode))
			self.visited = []
			self.visited.append(self.activeNode)
			# print(self.best)

		# generate new ant location based on weights then add previous node to "visited", ONLY VISIT NODES ONCE, once at end reset back to node 0 and try to get better path
		self.activeNode = self.newAnt()
		self.activeConnections = self.cWeights(self.nodes[self.activeNode]['connections'])

		# Display nodes as circles on screen
		# display connections from active node as lines between active node and all other nodes
		for con_key in list(self.activeConnections.keys()):
			start = self.nodes[con_key.split('-')[0]]['location']
			end = self.nodes[con_key.split('-')[-1]]['location']
			pygame.draw.line(self.display, "black", start, end, width=int(round(self.activeConnections[con_key][0], 0)))

		# display path of ant in red
		start = self.nodes[self.visited[0]]['location']
		for node in self.visited[0:]:
			end = start
			start = self.nodes[node]['location']
			pygame.draw.line(self.display, "red", start, end, width=5)


		for node in self.nodes:
			# print(repr(node))
			# print(repr(self.nodes[node]))
			col = "black" if node != self.activeNode else "red"
			pygame.draw.circle(self.display, col, self.nodes[node]['location'], 5)
			if node != self.activeNode and debug:
				ts = font.render(f"node {node} | {self.activeConnections[self.activeNode+'-'+node][1]}", False, "black")
				print((self.nodes[node]['location'][0]+30, self.nodes[node]['location'][0]))
				self.display.blit(ts, (self.nodes[node]['location'][0]+10, self.nodes[node]['location'][1]))

	def get_weights(self, distance, phero):
		if debug:
			print(distance)
		a = 1/distance**desire * phero**pheroPower
		if debug:
			print(a)
		return a

	def get_distance(self, start, end):
		x = start[0] - end[0]
		if debug:
			print(x)
		x = self.positive(x)

		y = start[1] - end[1]
		if debug:
			print(y)
		y = self.positive(y)


		if debug:
			print((x, y))
		dist = (x**2 + y**2)**(1/2)
		if debug:
			print(dist)
		return dist

	def positive(self, value):
		return value*-1 if value < 0 else value


if __name__ == '__main__':
	m = Main(screen, nodes, modifier, cell_size, border)
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
		screen.fill((255, 255, 255))
		m.update()
		pygame.display.flip()
		clock.tick(60)
	pygame.quit()