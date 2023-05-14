# import *
import numpy as np

# import * as *
import matplotlib.pyplot as plt

# from * import *
from mpl_toolkits.mplot3d import Axes3D

# get distance from 2 points
def distance(point1, point2):
    return np.sqrt(np.sum((point1 - point2)**2))

# ant colony function
def ant_colony_optimization(points, n_ants, n_iterations, alpha, beta, evaporation_rate, Q):
	# number of points = length of points
    n_points = len(points)
    # pheromones init as 1 for each point (init as matrix bidirectional matrix)
    pheromone = np.ones((n_points, n_points))
    # bestpath = none
    best_path = None
    # best length is infinity
    best_path_length = np.inf
    
    # for each iteration (could be a while loop instead and update screen using pygame and location)
    for iteration in range(n_iterations):
    	# paths = none
        paths = []
        # path lenghts = none
        path_lengths = []
        
        # for each ant in the number of ants
        for ant in range(n_ants):
        	# none have been visited starts as list of false where index is node key
            visited = [False]*n_points
            # starting point is random (doesn't matter where you're visiting them all anyway)
            current_point = np.random.randint(n_points)
            # visited current point is true (start here duh)
            visited[current_point] = True
            # path is set to current point (path list goes left to right beginning to end of path)
            path = [current_point]
            # path length = 0 (haven't gone anywhere)
            path_length = 0
            
            # while i haven't visited somewhere get going!
            while False in visited:
            	# find where we haven't visited
            	# np.where (where it is)
            	# logical not, compute truth value of NOT x element wise, for each element compute not x
            	# returns a list of points that have not been visited (aka, inverts the visited list and returns the first one, index 0)
                unvisited = np.where(np.logical_not(visited))[0]
                # probabilties is set to 0 for the each unvisited node
                probabilities = np.zeros(len(unvisited))
                
                # for each unvisited node
                for i, unvisited_point in enumerate(unvisited):
                	# the probability of that node being visited is equal to the pheromone
                	# for the path from current point to the unvisited candidate to the power of alpha (default 1) [desirability of closest]
                	# divide by the distance between the 2 points to the power of beta (default 1) [how strictly it follows pheromones]
                    probabilities[i] = pheromone[current_point, unvisited_point]**alpha / distance(points[current_point], points[unvisited_point])**beta
                
                # all probabilities are divided by the sum of all probs
                probabilities /= np.sum(probabilities)
                
                # the next point is calculated at random weighted by probability
                # numpy chooses from unvisited list and returns the index (uses index to get the probability for each point, e.g. index 0 of candidate list is index 0 of probs)
                next_point = np.random.choice(unvisited, p=probabilities)

                # add the new point to the path
                path.append(next_point)

                # add the distance between current and new to the path length
                path_length += distance(points[current_point], points[next_point])

                # set the new point to visited in the visited list
                visited[next_point] = True

                # new point is now current point
                current_point = next_point

            # append path to the paths list
            paths.append(path)

            # append path length to pathlengths
            path_lengths.append(path_length)

            # if the path length is less that previous best then it is new best
            if path_length < best_path_length:
                best_path = path
                best_path_length = path_length
        
        # evaporate the pheromones slightly
        pheromone *= evaporation_rate
        
        # for each path and path length
        for path, path_length in zip(paths, path_lengths):
        	# for each point - 1 (because python)
            for i in range(n_points-1):
            	# the pheromone is increased by Q (default 1) divide by path_length (so that best is enforced but allows deviation)
                pheromone[path[i], path[i+1]] += Q/path_length
            # for the last point to the first point do the same
            pheromone[path[-1], path[0]] += Q/path_length
    
    # display the figure
    fig = plt.figure(figsize=(8, 6))
    # display the axes
    ax = fig.add_subplot(111, projection='3d')
    # scatter the axes according to it's location
    ax.scatter(points[:,0], points[:,1], points[:,2], c='r', marker='o')

    # for each point - 1 (because python)
    for i in range(n_points-1):
    	# plot the best path)
        ax.plot([points[best_path[i],0], points[best_path[i+1],0]],
                [points[best_path[i],1], points[best_path[i+1],1]],
                [points[best_path[i],2], points[best_path[i+1],2]],
                c='g', linestyle='-', linewidth=2, marker='o')
    
    # plot the best path for last to first
    ax.plot([points[best_path[0],0], points[best_path[-1],0]],
            [points[best_path[0],1], points[best_path[-1],1]],
            [points[best_path[0],2], points[best_path[-1],2]],
            c='g', linestyle='-', linewidth=2, marker='o')
    
    # set labels
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    # show plot
    plt.show()
    
# Example usage:
points = np.random.rand(50, 3) # Generate 10 random 3D points
ant_colony_optimization(points, n_ants=10, n_iterations=100, alpha=1, beta=1, evaporation_rate=0.5, Q=1)