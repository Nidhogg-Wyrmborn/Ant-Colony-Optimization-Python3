import random
import pygame
import time

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
screen = pygame.display.set_mode((500*modifier, 500*modifier))
screen.fill('white')
clock = pygame.time.Clock()
running = True

class Node:
	def __init__(self, location:tuple, ID, pheromoneLvl):
		self.neighbors = {}
		self.ID = ID
		self.location = location
		self.pheromoneLvl = pheromoneLvl
	# return location
	def get_location(self):
		return self.location

	def get_weights(self, neighborID):
		try:
			return self.neighbors[neighborID][0]
		except:
			raise Exception("neighbors not set")

	def get_neighbors(self):
		try:
			return list(neighbors.keys())
		except:
			raise Exception('neighbors not set')

	def set_weights(self, distance, pheromone):
		return 1/distance**desire * pheromone**pheroPower

	def set_pheromone(self, pheromoneLvl):
		self.pheromoneLvl = pheromoneLvl

	def get_pheromone(self):
		return self.pheromoneLvl

	def set_neighbors(self, neighborIDs, neighborDistances):
		# generate distance and weights
		if isinstance(neighborIDs, list):
			for i in range(len(neighborIDs)):
				try:
					self.neighbors[neighborIDs[i]] = [neighborDistances[i], self.set_Weights(neighborDistances[i], neighborIDs[i].get_pheromone())]
				except:
					raise Exception("neighborIDs and neighborDistances not same length")

class Ant:
	def __init__(self, Node):
		self.activeNode = Node
		self.location = self.activeNode.get_location()

	def select_new_town(self):
		neighborDetails = {}
		neighborIDs = self.activeNode.get_neighbors()
		for ID in neighborIDs:
			neighborDetails[ID]


while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	screen.fill((255, 255, 255))
	pygame.display.flip()
	clock.tick(60)
pygame.quit()