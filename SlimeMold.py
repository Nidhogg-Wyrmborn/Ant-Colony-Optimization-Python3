import pygame
import hashlib
import random
import math
import numpy as np
from threading import Thread
from timeit import default_timer as timer
from OpenGL.GL import *

def has(state):
	state = hashlib.sha256(str(state).encode()).hexdigest()
	return int(state, base=16)

#initiliaze pixel buffers

global display, history, buffer, doUpdate
display = (1000,800)
debug = False
agentUpdate = []
agents = []
numAgents = 10
moveSpeed = 0.03
deltaTime = 0.03
Decrease = 0.9
oldPos = {}
history = {}
buffer = bytearray(display[0] * display[1] * 3)
doUpdate = True
# {(x, y): (r, g, b)}

def pixelUpdate(screensize:tuple, history:dict, buffer=None):
	if history == {}:

		buffer = bytearray(display[0] * display[1] * 3)

		count = 0
		for i in range(display[0] * display[1] * 3):
			if count == 0:
				# new_byte = int(round((has(i)/115792089237316195423570985008687907853269984665640564039457584007913129639935)*255, 0))
				new_byte = 0
				count += 1
			else:
				count += 1
				if count >= 3:
					count = 0
			# print(new_byte)
			buffer[i] = new_byte
		return buffer
	else:
		if buffer:
			for key in history:
				rgb = history[key]
				# new_byte = int(round((has(key[0] * key[1] * 3 - 3)/115792089237316195423570985008687907853269984665640564039457584007913129639935), 0))
				new_byte = 1
				start = int(round(key[0], 0))
				end = int(round(key[1], 0))
				rgb = tuple(int(round(p, 0)) for p in rgb)
				buffer[start * end * 3 - 3] = new_byte * rgb[0]
				buffer[start * end * 3 - 2] = new_byte * rgb[1]
				buffer[start * end * 3 - 1] = new_byte * rgb[2]
			return buffer
		else:
			raise Exception('buffer not supplied')

# buffer = update(display, history)

def pixel_handle():
	global history, buffer, display, doUpdate
	while True:
		if len(agentUpdate) > 0:
			key = tuple(agents[agentUpdate[0]].position)
			value = (255,255,255)
			history[key] = value
			if debug:
				print(f"{key}: {value}")
			deled = []
			print(len(history.keys()), end="\r")
			for ky in list(history.keys()):
				if ky != key or ky not in deled:
					# print(history[ky])
					history[ky] = tuple(Decrease*x for x in history[ky])
					if history[ky][0] < 10 or history[ky][1] < 10 or history[ky][2] < 10:
						# print('delete', end="\r")
						deled.append(ky)
						del history[ky]
			doUpdate = True

		if doUpdate:
			buffer = pixelUpdate(display, history, buffer)
			doUpdate = False


class Agent:
	def __init__(self, angle:float, position:np.ndarray):
		self.position = position
		self.angle = angle

def update(agentID):
	global agents, agentUpdate
	if agentID >= numAgents:
		return

	agent = agents[agentID]
	
	direction = np.array((math.cos(agent.angle), math.sin(agent.angle)))
	# print(direction, end="\r")
	newPos = agent.position + direction * moveSpeed * deltaTime
	# print(newPos)
	# print(agentID, end="\r")
	# print(list(oldPos.keys()), end="\r")
	# print(agentID in list(oldPos.keys()), end="\r")
	if agentID in list(oldPos.keys()):
		if tuple(newPos) == tuple(oldPos[agentID]):
			# print('NOT MOVING', end="\r")
			pass
		else:
			# print("MOVING", end="\r")
			pass
	oldPos[agentID] = newPos
	# print(newPos, end="\r")

	if newPos[0] < 0 or newPos[0] >= display[0] or newPos[1] < 0 or newPos[1] >= display[1]:
		# print('bounce')
		newPos = list(newPos)
		newPos[0] = min(display[0]-0.01, max(0, newPos[0]))
		newPos[1] = min(display[1]-0.01, max(0, newPos[1]))
		newPos = tuple(newPos)
		agents[agentID].angle = np.random.rand(1,1) * 2 * math.pi

	agents[agentID].position = newPos
	agentUpdate.append(agentID)

def main():
	global buffer, agents, numAgents
	for i in range(numAgents):
		agents.append(Agent(random.randint(0,360), np.array((float(random.randint(0, display[0])), float(random.randint(0, display[1]))))))
	pygame.init()
	pygame.display.set_mode(display, pygame.DOUBLEBUF| pygame.OPENGL)

	Thread(target=pixel_handle, daemon=True).start()

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

		start = timer()

		for agentID in range(len(agents)):
			# print('updating agentID '+str(agentID), end="\r")
			update(agentID)

		glClear(GL_COLOR_BUFFER_BIT)
		glDrawPixels(display[0], display[1], GL_RGB, GL_UNSIGNED_BYTE, buffer)
		pygame.display.flip()
		# print(str(timer()-start), end="\r")

main()

#############################

# width = 500
# height = 500
# border = 20
# title = 'slime mold simulation'



# def pixelHandle(pixelx, pixely):
# 	global 
# 	print((pixelx, pixely), end="\r")
# 	shade = int(round(has(pixelx*width+pixely), 0))
# 	color = (shade, shade, shade)
# 	return [squareFunction,color]

# pixels = []
# for pixel_x in range(width):
# 	for pixel_y in range(height):
# 		pixels.append(pixelHandle(pixel_x, pixel_y))
# 		print(pixels[-1][1], end="\r")

# run window