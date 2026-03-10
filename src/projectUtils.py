import math
import random
import numpy as np
from collections import deque
from dataclasses import dataclass
from map import Map, CellType

@dataclass
class Position:
    x: int
    y: int
    def distance_to(self, other: 'Position') -> float:
        return math.dist((self.x, self.y), (other.x, other.y))

class Visibility:
    def __init__(self, reach: int, radius_: float, x_rays: bool = False):
        self.reach = reach
        self.radius = radius_
        self.x_rays = x_rays
        
    def update(self, position: Position, local_map: Map, global_map: Map):
        grid = global_map.grid
        rows, cols = grid.shape
        visited = {(position.x, position.y)}
        queue = deque([(position.x, position.y, 0)])
        local_map.set_cell((position.x, position.y), grid[position.x, position.y]) 

        while queue:
            r, c, depth = queue.popleft()
            if depth >= self.reach: continue
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    visited.add((nr, nc)) 
                    local_map.set_cell((nr, nc), grid[nr, nc])
                    if grid[nr, nc] == CellType.Empty or self.x_rays:
                        queue.append((nr, nc, depth + 1))

class Strategy:
    def __init__(self, storage_x: int, storage_y: int, num_goal: int, epsilon: float = 0.8):
        self.Path_target = []
        self.storage = [Position(storage_x, storage_y)]
        self.num_goal = num_goal
        self.epsilon = epsilon 
        self.status = 3

    def _get_random_move(self) -> tuple[int, int]: 
        return random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])

    def _get_nearest_storage(self, current_pos: Position) -> Position:
        if not self.storage: return None 
        return min(self.storage, key=lambda store: current_pos.distance_to(store))

    def _find_target(self, current_map) -> tuple[int, int]:
        rows, cols = current_map.grid.shape
        for i in range(rows):
            for j in range(cols):
                if current_map.grid[i][j] == 3:
                    return (i, j)
        return (-1, -1)

    def _get_Path(self, start: Position, local_map, target: Position) -> tuple[Position, list[Position]]:
        queue = deque([[start]])
        visited = {(start.x, start.y)}
        rows, cols = local_map.grid.shape

        while queue:
            path = queue.popleft()
            curr = path[-1]

            if (curr.x, curr.y) == (target.x, target.y):
                return path[1], path[2:] 

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = curr.x + dx, curr.y + dy
                if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                    if local_map.grid[nx, ny] != CellType.Wall:
                        visited.add((nx, ny))
                        queue.append(path + [Position(nx, ny)])
        return None, []

    def next_move(self, position: Position, local_map: Map, current_energy: int):
        if current_energy <= 0: self.status = 0
        if self.status == 0: return None
        
        elif self.status == 1:
            if self._find_target(local_map) != (-1, -1): 
                self.status = 3
                return self.next_move(position, local_map, current_energy)
            return self._get_random_move() if random.random() < self.epsilon else (0, 0)
            
        elif self.status == 2:
            near_store = self._get_nearest_storage(position)
            if near_store:
                next_move_, self.Path_target = self._get_Path(position, local_map, near_store)
                if next_move_:
                    self.status = 4
                    return (next_move_.x - position.x, next_move_.y - position.y)
            self.status = 1
            return (0, 0)
        
        elif self.status == 3:
            x_, y_ = self._find_target(local_map)
            if x_ == -1: 
                self.status = 1
                return (0, 0)
            
            next_move_, self.Path_target = self._get_Path(position, local_map, Position(x_, y_))
            if next_move_:
                self.status = 4
                return (next_move_.x - position.x, next_move_.y - position.y)
            self.status = 1
            return (0, 0)
            
        elif self.status == 4:
            if not self.Path_target:
                self.status = 1
                return (0, 0)
            
            next_move_ = self.Path_target.pop(0)
            return (next_move_.x - position.x, next_move_.y - position.y)

        return None

class Agente:
    def __init__(self, position: Position, visibility: Visibility, energy: int, local_map: Map, strategy: Strategy):
        self.position = position
        self.visibility = visibility
        self.energy = energy
        self.local_map = local_map
        self.strategy = strategy

    def action(self, global_map: Map): 
        self.visibility.update(self.position, self.local_map, global_map)
        move_vector = self.strategy.next_move(self.position, self.local_map, self.energy)

        if move_vector is None: return

        dx, dy = move_vector 
        target_x = self.position.x + dx
        target_y = self.position.y + dy

        if 0 <= target_x < global_map.grid.shape[0] and 0 <= target_y < global_map.grid.shape[1]:
            if global_map.grid[target_x, target_y] != CellType.Wall:
                self.position.x = target_x
                self.position.y = target_y
                self.energy -= 1

    def print_map(self) -> None:
        self.local_map.print_map()