import math
import numpy as np
from collections import deque
from map import Map, CellType
import random

class Pose:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def dist(self, x, y):
        return math.dist([self.x, self.y], [x, y])

    def FindNear(self, targets: list[Pose]) -> Pose | None:
        if not targets: return None 
        return min(targets, key=lambda t: self.dist(t.x, t.y))

class Visibility:
    def __init__(self, reach, radius, xRays=False):
        self.reach = reach
        self.radius = radius
        self.xRays = xRays
    
    def update(self, position, localMap : Map, grid : np.matrix):
        rows, cols = grid.shape
        visited = {(position.x, position.y)}
        queue = deque([(position.x, position.y, 0)])
        
        #localMap.set_cell((position.x, position.y), grid[position.x, position.y]) 

        while queue:
            r, c, deep = queue.popleft()
            
            if deep >= self.reach: 
                continue

            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc

                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    visited.add((nr, nc)) 

                    #localMap.set_cell((nr, nc), grid[nr, nc])
                    localMap.set_cell((nr, nc), 0)
                    
                    if grid[nr, nc] == 0 or self.xRays:
                        queue.append((nr, nc, deep + 1))

class Strategy:
    def __init__(self, storage_x : int, storage_y : int, max_energy : int, num_goal : int, epsilon=0.8):
        self.storage = [Pose(storage_x, storage_y)]
        self.max_energy = max_energy
        self.current_energy = max_energy
        self.num_goal = num_goal
        self.status = 1
        self.epsilon = epsilon 

 
    def _get_random_move(self): 
        return random.choice([(-1,0), (1,0), (0,-1), (0,1)])

    def next_move(self, position : Pose, localMap : Map):
        if self.status == 0: return None

        if self.status == 1: # Esplorazione  
            if random.random() < self.epsilon:
                return self._get_random_move()  
            #return self._get_strategic_move(position, localMap) 

        elif self.status == 2: # Ritorno 
            near_store = position.FindNear(self.storage)
            if near_store:
                print(f"Storage più vicino -> [{near_store.x},{near_store.y}]") 
            else:
                self.status = 1
        # pensare se aggiungere il ritorno safe    
        if self.current_energy <= 0: self.status = 0

class Agente:
    def __init__(self, position_ : Pose, visibility_ : Visibility, charge_ : int, localMap_: Map, strategy_: Strategy):
        self.position = position_
        self.visibility = visibility_
        self.charge = charge_
        self.localMap = localMap_
        self.strategy = strategy_

    def action(self, Map : Map): 
        self.visibility.update(self.position, self.localMap, Map.grid)
        res = self.strategy.next_move(self.position, self.localMap)
        if res is None: return

        x_, y_ = res 
        new_x, new_y = self.position.x + x_, self.position.y + y_
        
        if 0 <= new_x < self.localMap.grid.shape[0]:
            self.position.x = new_x
        if 0 <= new_y < self.localMap.grid.shape[1]:
            self.position.y = new_y

    def printMap(self):
        self.localMap.print_map()
