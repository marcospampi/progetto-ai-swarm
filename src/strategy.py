import random
from collections import deque
from map import Map, CellType
from geometry import Position
from enum import Enum

class AgentState(Enum):
    DEAD = 0
    EXPLORE = 1
    REACH_ITEM = 2      # ha visto un item e sta cercando di raggiungerlo
    SEEK_STORAGE = 3    # calcola la BFS per il magazzino più vicino
    REACH_STORAGE = 4   # ragionge il magazzino e deposita l'item


class AbstractStrategy:
    num_goal: int
    epsilon: float
    status: AgentState
    storages: list
    Path_target: any
    def __init__(self, num_goal: int, epsilon: float = 0.8):
        self.num_goal = num_goal
        self.epsilon = epsilon 
        self.status = AgentState.EXPLORE
        self.storages = []
        self.Path_target = None
    def next_move(self, position: Position, local_map: Map, current_energy: int) -> tuple[int,int]:
        return (0,0)

class Strategy(AbstractStrategy):
    def _get_random_move(self) -> tuple[int, int]: 
        return random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])

    def _get_nearest_storage(self, current_pos: Position) -> Position:
        if not self.storages: return None 
        return min(self.storages, key=lambda store: current_pos.manhattan_distance_to(store))

    def _find_target(self, current_map) -> tuple[int, int]:
        rows, cols = current_map.grid.shape
        for i in range(rows):
            for j in range(cols):
                if current_map.grid[i, j] == CellType.Item:
                    return (i, j)
        return (-1, -1)

    def _get_Path(self, start: Position, local_map, target: Position) -> tuple[Position, list[Position]]:
        queue = deque([[start]])
        visited = {(start.x, start.y)}
        rows, cols = local_map.grid.shape

        while queue:
            path = queue.popleft()
            curr = path[-1]

            if len(path) > 1:
                return path[1], path[2:] 
            else:
                return None, []

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = curr.x + dx, curr.y + dy
                if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                    if local_map.grid[nx, ny] != CellType.Wall:
                        visited.add((nx, ny))
                        queue.append(path + [Position(nx, ny)])
        return None, []

    def next_move(self, position: Position, local_map: Map, current_energy: int) -> tuple[int,int]:
        if current_energy <= 0: self.status = AgentState.DEAD
        if self.status == AgentState.DEAD: return None

        if self.status == AgentState.EXPLORE:
            if self._find_target(local_map) != (-1, -1):
                self.status = AgentState.REACH_ITEM
                return self.next_move(position, local_map, current_energy)
            return self._get_random_move() if random.random() < self.epsilon else (0, 0)

        #sistemare questo
        elif self.status == AgentState.REACH_ITEM:
            if self.Path_target:
                next_move_ = self.Path_target.pop(0)
                return (next_move_.x - position.x, next_move_.y - position.y)
            
            x_, y_ = self._find_target(local_map)
            
            if x_ == -1: 
                self.status = AgentState.EXPLORE
                return (0, 0)
            
            target_pos = Position(x_, y_)
            next_move_, self.Path_target = self._get_Path(position, local_map, target_pos)
            
            if next_move_:
                return (next_move_.x - position.x, next_move_.y - position.y)
            

        if self.status == AgentState.SEEK_STORAGE:
            x_, y_ = self._find_target(local_map)
            if x_ == -1: 
                self.status = AgentState.EXPLORE
                return (0, 0)
            
            next_move_, self.Path_target = self._get_Path(position, local_map, Position(x_, y_))
            if next_move_:
                self.status = AgentState.REACH_STORAGE
                return (next_move_.x - position.x, next_move_.y - position.y)
            self.status = AgentState.EXPLORE
            return (0, 0)
            
        elif self.status == AgentState.REACH_STORAGE:
            if not self.Path_target:
                self.status = AgentState.EXPLORE
                return (0, 0)
            
            next_move_ = self.Path_target.pop(0)
            return (next_move_.x - position.x, next_move_.y - position.y)

        return None
    
class StupidStrategy(AbstractStrategy):
    def next_move(self, position, local_map, current_energy):
        return None