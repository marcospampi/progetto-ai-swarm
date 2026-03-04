import math
import random
import numpy as np
from collections import deque
from dataclasses import dataclass
from map import Map, CellType


@dataclass
class Position:
    #coordinate 2D dell'agente
    x: int
    y: int
    
    def distance_to(self, other: 'Position') -> float:
        #calcola la distanza euclidea verso un'altra posizione
        return math.dist((self.x, self.y), (other.x, other.y))



class Visibility:
    #aggiorna la mappa locale in base al raggio visivo
    def __init__(self, reach: int, x_rays: bool = False) -> None:
        self.reach = reach
        self.x_rays = x_rays
    
    def update(self, position: Position, local_map: Map, global_map: Map) -> None:
        grid = global_map.grid
        rows, cols = grid.shape

        visited = {(position.x, position.y)}
        queue = deque([(position.x, position.y, 0)])
        
        local_map.set_cell((position.x, position.y), grid[position.x, position.y]) 

        while queue:
            r, c, depth = queue.popleft()
            
            if depth >= self.reach: 
                continue

            # Espansione a croce (Nord, Sud, Ovest, Est)
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc

                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    visited.add((nr, nc)) 

                    local_map.set_cell((nr, nc), grid[nr, nc])
                    
                    if grid[nr, nc] == CellType.Empty or self.x_rays:
                        queue.append((nr, nc, depth + 1))


class Strategy:

    def __init__(self, storage_x: int, storage_y: int, num_goal: int, epsilon: float = 0.8) -> None:
        self.storage = [Position(storage_x, storage_y)]
        self.num_goal = num_goal
        self.epsilon = epsilon 
        self.status = 1  # 0: Spento, 1: Esplorazione, 2: Ritorno

    def _get_random_move(self) -> tuple[int, int]: 
        return random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])

    def _get_nearest_storage(self, current_pos: Position) -> Position | None:
        if not self.storage:
            return None 
        return min(self.storage, key=lambda store: current_pos.distance_to(store))

    def next_move(self, position: Position, local_map: Map, current_energy: int) -> tuple[int, int] | None:
        if current_energy <= 0: 
            self.status = 0
            
        if self.status == 0: 
            return None

        if self.status == 1: # Esplorazione  
            if random.random() < self.epsilon:
                return self._get_random_move()

        elif self.status == 2: # Ritorno 
            near_store = self._get_nearest_storage(position)
            if near_store:
                print(f"Ritorno allo storage più vicino -> [{near_store.x}, {near_store.y}]") 
                # Qui andrà implementato il pathfinding verso near_store
            else:
                self.status = 1
                
        return None


class Agente:

    def __init__(self, position: Position, visibility: Visibility, energy: int, local_map: Map, strategy: Strategy) -> None:
        self.position = position
        self.visibility = visibility
        self.energy = energy
        self.local_map = local_map
        self.strategy = strategy

    def action(self, global_map: Map) -> None: 
        #esegue un singolo step di simulazione dell'agente
        
        self.visibility.update(self.position, self.local_map, global_map)
        
        move_vector = self.strategy.next_move(self.position, self.local_map, self.energy)
        
        if move_vector is None: 
            return

        dx, dy = move_vector 
        target_x = self.position.x + dx
        target_y = self.position.y + dy
        

        if (0 <= target_x < global_map.grid.shape[0]) and (0 <= target_y < global_map.grid.shape[1]):

            if global_map.grid[target_x, target_y] != CellType.Wall:
                self.position.x = target_x
                self.position.y = target_y
                
                self.energy -= 1

    def print_map(self) -> None:
        self.local_map.print_map()