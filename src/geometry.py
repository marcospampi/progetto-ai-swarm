from __future__ import annotations # FIX: Permette di usare Position come type hint dentro se stessa
import math
from collections import deque
from map import Map, CellType
from dataclasses import dataclass

@dataclass
class Position:
    x: int
    y: int

    def manhattan_distance_to(self, other: Position) -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def euclidean_distance_to(self, other: Position) -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def to_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)

    @staticmethod # Aggiunto decorator per correttezza
    def from_tuple(t: tuple[int, int]) -> Position:
        return Position(t[0], t[1])

# --- Sensori ---
class VisibilitySensor:
    def __init__(self, reach: int, x_rays: bool = False):
        self.reach = reach
        self.x_rays = x_rays
        
    def update(self, agent_position: Position, local_map: Map, global_map: Map):
        grid = global_map.grid
        rows, cols = grid.shape
        visited = {(agent_position.x, agent_position.y)}
        queue = deque([(agent_position.x, agent_position.y, 0)])
        local_map.set_cell((agent_position.x, agent_position.y), grid[agent_position.x, agent_position.y]) 

        while queue:
            r, c, depth = queue.popleft()
            if depth >= self.reach: continue
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    visited.add((nr, nc)) 
                    local_map.set_cell((nr, nc), grid[nr, nc])
                    if grid[nr, nc] != CellType.Wall or self.x_rays:
                        queue.append((nr, nc, depth + 1))

class CommunicationSensor:
    def __init__(self, radius: float):
        self.radius = radius
        
    def update(self, self_agent, agents: list):
        for other_agent in agents:
            if other_agent is self_agent or not other_agent.is_active:
                continue
                
            dist = self_agent.position.euclidean_distance_to(other_agent.position)
            
            if dist <= self.radius:
                my_grid = self_agent.local_map.grid
                other_grid = other_agent.local_map.grid
                
                mask = (my_grid == CellType.unknown) & (other_grid != CellType.unknown)
                my_grid[mask] = other_grid[mask]