import random
import pygame
import time

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Calibri', 10)

debug = False
debugTimer = 0
modifier = 1.5
Smodifier = 1.5
nodes = 100
num_ants = 20
cell_size = 10
border = 10
desire = 1.1
pheroPower = 2
tickTime = 120
neigh = True
screen = pygame.display.set_mode((500*modifier, 500*modifier))
screen.fill('white')
clock = pygame.time.Clock()
running = True

class Node:
	def __init__(self, location:tuple, ID):
		# create empty neighbor dict
		self.neighbors = {}

		# set self ID (for when node is in a list)
		self.ID = ID

		# set self location tuple
		self.location = location

		# set pheromone level to empty dict
		self.pheromoneLvl = {}
	
	# get self id
	def get_ID(self):
		return self.ID

	# return location
	def get_location(self):
		return self.location

	# get distance relative to neighbor (ID)
	def get_distance(self, neighborID):
		# try to retrieve if error then it's not been set yet
		try:
			return self.neighbors[neighborID]
		except:
			raise Exception("neighbors not set")

	# get neighbors (if the node isn't connected to every other node)
	def get_neighbors(self):
		# try, if fail not set
		try:
			return list(self.neighbors.keys())
		except Exception as e:
			raise Exception('neighbors not set\n\n'+str(e))

	# set weights based on 1/distance (percent) ^ desirability (how much the ant will prefer closer targets) * pheromonelvl ^ pheromone power (how much the pheromone affects choice)
	def set_weights(self, distance, pheromone):
		return 1/distance**desire * pheromone**pheroPower

	# set the pheromone level according to neighbor id (only affects connection between this node and the id of the other)
	def set_pheromone(self, pheromoneLvl, ID):
		self.pheromoneLvl[ID] = self.set_weights(self.neighbors[ID], pheromoneLvl)

	# get the pheremone level from this node to another node's id
	def get_pheromone(self, ID):
		return self.pheromoneLvl[ID]

	# set neighbors via id and distances (IDs must be in same order as distances e.g. 1,2,3,4 must be relative to 3.3,2.7,9.6,1.1)
	def set_neighbors(self, neighborIDs, neighborDistances):
		# generate distance and weights
		if isinstance(neighborIDs, list) and len(neighborIDs) == len(neighborDistances) and isinstance(neighborDistances, list):
			for i in range(len(neighborIDs)):
				if neighborIDs[i] == self.ID:
					continue
				try:
					self.neighbors[neighborIDs[i]] = neighborDistances[i]
					self.pheromoneLvl[neighborIDs[i]] = self.set_weights(neighborDistances[i], 1)
				except Exception as e:
					raise Exception("neighborIDs and neighborDistances not same length\n\n"+str(e))
		else:
			raise Exception("IDs must be a list/IDs must be same length as Distances/Distances must be a list")

# Ant class
class Ant:
	# init
	def __init__(self, Node, nodelist:dict):
		# set active node to the init node object
		self.activeNode = Node

		# set node dict (dict of all node objects, the key is node ids)
		self.nodelist = nodelist

		# set current location to the active nodes location
		self.location = self.activeNode.get_location()

		# create list of visited and unvisited nodes
		self.visited = []
		self.unvisited = list(self.nodelist.keys())

		# is disabled
		self.disabled = False

		# set history to empty list
		self.hist = []

		# set score to 0 (length traveled)
		self.scor = 0

	# select a new node based on weights/pheremones
	def select_new_town(self):
		if not self.disabled:
			# get neighbor ids from active node
			neighborIDs = self.activeNode.get_neighbors()
			count = 0
			for ID in range(len(neighborIDs)-1):
				if debug:
					print(len(neighborIDs), ID-count)
				if neighborIDs[ID-count] in self.visited:
					neighborIDs.pop(ID-count)
					count += 1

			if len(neighborIDs) <= 0:
				if debug or neigh:
					print('neighborIDs <= 0')
				neighborIDs = self.activeNode.get_neighbors()

			# create dict of weights, locations, distances
			weights = {}
			location = {}
			distance = {}

			# for each id get weights, and location
			for ID in neighborIDs:
				weights[ID] = self.activeNode.get_pheromone(ID)
				location[ID] = self.nodelist[ID].get_location()
				distance[ID] = self.activeNode.get_distance(ID)

			new_town = random.choices(population=neighborIDs, weights=list(weights.values()), k=1)[0]

			if debug:
				print(new_town)
				print(weights[new_town], max(list(weights.values())))
				print(location[new_town])
				print(distance[new_town], min(list(distance.values())))

			return new_town
		else:
			return

	# get active node (current "town")
	def get_activeNode(self):
		return self.activeNode.get_ID()

	# move to new town
	def move(self, node):
		if not self.disabled:
			if debug:
				print(self.visited)
				print(self.unvisited)
			self.scor += self.activeNode.get_distance(node.get_ID())
			try:
				self.unvisited.pop(self.unvisited.index(self.activeNode.get_ID()))
				self.visited.append(self.activeNode.get_ID())
			except:
				pass
			self.activeNode = node
			self.location = self.activeNode.get_location()
		else:
			return

	# get visited locations (to display path)
	def get_visited(self):
		return self.visited

	# reset
	def reset(self):
		self.visited = []
		self.unvisited = list(self.nodelist.keys())
		self.hist = []
		self.scor = 0

	# score
	def score(self):
		return self.scor

	# disable
	def disable(self):
		self.disabled = True

	# enable
	def enable(self):
		self.disabled = False

	# return True if disabled
	def enabled(self):
		return self.disabled

	# return history if var empty or add ID to history if ID in var
	def history(self, ID=None):
		if ID == None:
			return self.hist
		self.hist.append(ID)

# main screen class
class Main:
	# init
	def __init__(self, screen, num_nodes:int, modifier:float, border:int):
		# set init vars to object vars
		self.screen = screen
		self.num_nodes = num_nodes
		self.modifier = modifier
		self.border = border
		self.nodelist = {}

		# create node dict (keys = IDs)
		for nodeKey in range(num_nodes):
			self.nodelist[str(nodeKey)] = Node((random.randint(0+self.border, 500*modifier-self.border), random.randint(0+self.border, 500*modifier-self.border)), str(nodeKey))

		for node in self.nodelist:
			self.nodelist[node].set_neighbors(list(self.nodelist.keys()), self.get_distances(self.nodelist, self.nodelist[node]))

		# create Ant object
		self.ants = []

		for i in range(num_ants):
			self.ants.append(Ant(self.nodelist[list(self.nodelist.keys())[0]], self.nodelist))

		antNodes = []
		for ant in self.ants:
			antNodes.append(ant.get_activeNode())

		for node in self.nodelist[antNodes[0]].get_neighbors():
			start = self.nodelist[antNodes[0]].get_location()
			end = self.nodelist[node].get_location()
			pygame.draw.line(self.screen, "grey", start, end, width=5)

		for node in self.nodelist:
			color = "red" if node in antNodes else "black"
			pygame.draw.circle(self.screen, color, self.nodelist[node].get_location(), 10)

	# update function (while window running to move ant)
	def update(self):
		self.move_ants()

		antNodes = []
		for ant in self.ants:
			antNodes.append(ant.get_activeNode())
		for node in self.nodelist[antNodes[0]].get_neighbors():
			start = self.nodelist[antNodes[0]].get_location()
			end = self.nodelist[node].get_location()
			pygame.draw.line(self.screen, "grey", start, end, width=int(round(5/Smodifier, 0)))

		for ant in self.ants:
			visited = ant.get_visited()
			if len(visited) > 0:
				start = self.nodelist[visited[0]].get_location()
				for node in visited[1:]:
					end = self.nodelist[node].get_location()
					pygame.draw.line(self.screen, "red", start, end, width=int(round(5/Smodifier, 0)))
					start = end
			else:
				start = self.nodelist[ant.get_activeNode()].get_location()
			pygame.draw.line(self.screen, 'red', start, self.nodelist[ant.get_activeNode()].get_location(), width=int(round(5/Smodifier, 0)))

		for node in self.nodelist:
			color = "red" if node in antNodes else "black"
			pygame.draw.circle(self.screen, color, self.nodelist[node].get_location(), int(round(10/Smodifier, 0)))

	def move_ants(self):
		count = 0
		history = {}
		best = random.choice(self.ants).score()
		for ant in range(len(self.ants)):
			if len(self.ants[ant].unvisited) <= 0:
				history[ant] = self.ants[ant].history()
				if self.ants[ant].score() > best:
					best = self.ants[ant].score()
				self.ants[ant].reset()
				self.ants[ant].disable()

		for ant in self.ants:
			# print(ant.enabled())
			if ant.enabled():
				# print('yes')
				count += 1

		if count >= len(self.ants)-1:
			# print("counter")
			for ant in self.ants:
				ant.enable()

		for ant in self.ants:
			self.move_ant(ant)

	def move_ant(self, ant):
		new_town = ant.select_new_town()
		if new_town == None:
			return
		ant.history(new_town)
		ant.move(self.nodelist[new_town])

	# get distances for one node for each item in a list (of nodes)
	def get_distances(self, nodelist, node):
		# for each item in the nodelist generate the distance
		distances = []

		# get the starting nodes location (tuple)
		start = node.get_location()

		for n in list(nodelist.values()):
			# set end to each node's location that isn't the starting node, per iteration
			if n == node:
				distances.append(0)
				continue
			end = n.get_location()

			# x = startx - endx
			# if x is negative make positive otherwise leave it
			x = start[0]-end[0]
			x = -1*x if x < 0 else x

			# same with y
			y = start[1]-end[1]
			y = -1*y if y < 0 else y

			# use pythag to calc distance between 2 nodes
			dist = (x**2 + y**2)**(1/2)

			# round to 2 decimals
			dist = round(dist, 2)

			# add to list
			distances.append(dist)

		if debug:
			print(len(distances))
			print(len(nodelist))
		# return distances
		return distances

m = Main(screen, nodes, modifier, border)
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	screen.fill((255, 255, 255))
	m.update()
	pygame.display.flip()
	clock.tick(tickTime)
pygame.quit()