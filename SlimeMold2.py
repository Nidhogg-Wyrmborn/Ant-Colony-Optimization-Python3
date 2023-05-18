import numpy as np
import cv2

size = (500, 500, 3)

moveSpeed = 1

im = np.zeros(size, np.uint8)

agents = [{'x':5,'y':5,'vx':1,'vy':1}]

def sin2d(x,y):
	"""2-d sine function to plot"""
	return np.sin(x) + np.cos(y)

def getFrame():
	"""Generate next frame of simulation as numpy array"""

	update()

	getFrame.z = im

	return getFrame.z

getFrame.z = None

def update():
	for agent in agents:
		im[agent['x'], agent['y']] = (0,0,0)
		agent['x'] += agent['vx'] * moveSpeed
		agent['y'] += agent['vy'] * moveSpeed

		if agent['x'] > size[0]-1:
			print('agentx > size0-1')
			agent['vx'] *= -1
			agent['x'] -= agent['x']-size[0]+1

		if agent['x'] < 0:
			print('agentx < 0')
			agent['vx'] *= -1
			agent['x'] += -agent['x']

		if agent['y'] > size[1]-1:
			print('agenty > size1-1')
			agent['vy'] *= -1
			agent['y'] -= agent['y']-size[1]+1

		if agent['y'] < 0:
			print('agenty < 0')
			agent['vy'] *= -1
			agent['y'] += -agent['y']

		print((agent['x'], agent['y']))

		im[agent['x'], agent['y']] = (255, 255, 255)

while True:
	npimage = getFrame()

	cv2.imshow('image', npimage)
	k = cv2.waitKey(100)

	if k == 27:
		cv2.destroyAllWindows()
		break