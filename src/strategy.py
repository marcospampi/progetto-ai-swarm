import random
from collections import deque
from map import Map, CellType
from geometry import Position
from enum import Enum

class AgentState(Enum):
    DEAD = 0
    EXPLORE = 1
    REACH_ITEM = 2      # ha visto un item e sta cercando di raggiungerlo
    SEEK_STORAGE = 3    # ho preso l'item e sto andando allo store più vicino

class Strategy:
    def __init__(self, num_goal: int, epsilon: float = 0.8):
        self.num_goal = num_goal
        self.epsilon = epsilon 
        self.status = AgentState.EXPLORE
        self.storages = []

    def _get_random_move(self) -> tuple[int, int]: 
        return random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])

    def _get_nearest_(self, current_pos: Position, positions: list[Position]) -> Position:
        return min(positions, key=lambda p: current_pos.manhattan_distance_to(p)) if positions else None

    def _find_nearest_target(self, current_pos, current_map, goal) -> tuple[int, int]:
        rows, cols = current_map.grid.shape
        targets = [Position(i, j) for i in range(rows) for j in range(cols) if current_map.grid[i, j] == goal]
        
        if not targets: return (-1, -1)
        
        nearest = min(targets, key=lambda t: current_pos.manhattan_distance_to(t))
        return (nearest.x, nearest.y)

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

    def next_move(self, position: Position, local_map: Map, current_energy: int, carring: bool):
        # ________________________________________________________________________________ morto
        if current_energy <= 0: self.status = AgentState.DEAD
        if self.status == AgentState.DEAD: return None

        # ________________________________________________________________________________ esplora
        if self.status == AgentState.EXPLORE:
            if self._find_nearest_target(position, local_map, CellType.Item) != (-1, -1) and carring == False:
                self.status = AgentState.REACH_ITEM
                return self.next_move(position, local_map, current_energy)
            return self._get_random_move() if random.random() < self.epsilon else (0, 0) #dobbiamo fare la logica direzionale

        
        # ________________________________________________________________________________ raggiungi l'obbiettivo più vicino
        elif self.status == AgentState.REACH_ITEM: 
            if carring == True: # ha preso l'oggetto
                self.status == AgentState.SEEK_STORAGE
                self.Path_target = []
                return next_move(self, position, local_map, current_energy, carring)

            if self.Path_target: # segui il path 
                next_move_ = self.Path_target.pop(0)
                return (next_move_.x - position.x, next_move_.y - position.y)

            elif self._find_nearest_target(position, local_map, CellType.Item) != (-1,-1): # crea il path
                x_, y_ = self._find_nearest_target(position, local_map, CellType.Item)
                target_pos = Position(x_, y_)
                self.Path_target = self._get_Path(position, local_map, target_pos)
                return next_move(self, position, local_map, current_energy, carring)

            else: # Non ha trovato più l'oggetto
                self.status == AgentState.EXPLORE
                return next_move(self, position, local_map, current_energy, carring)
                        

        # ________________________________________________________________________________ raggiungi lo storage più vicino
        if self.status == AgentState.SEEK_STORAGE:
            
            if carring == False: # ha scaricato l'oggetto
                self.status == AgentState.EXPLORE
                self.Path_target = []
                return next_move(self, position, local_map, current_energy, carring)

            if self.Path_target: # segui il path 
                next_move_ = self.Path_target.pop(0)
                return (next_move_.x - position.x, next_move_.y - position.y)

            elif self._find_nearest_target(position, local_map, CellType.Store) != (-1,-1): # crea il path
                x_, y_ = self._find_nearest_target(position, local_map, CellType.Store)
                target_pos = Position(x_, y_)
                self.Path_target = self._get_Path(position, local_map, target_pos)
                return next_move(self, position, local_map, current_energy, carring)

            else: # Non conosce la posizione di uno storage
                self.status == AgentState.EXPLORE
                return next_move(self, position, local_map, current_energy, carring)
                        
        return None