import random
from collections import deque
from abc import ABC, abstractmethod
from map import Map, CellType
from geometry import Position
from enum import Enum

class AgentState(Enum):
    DEAD = 0
    EXPLORE = 1
    REACH_ITEM = 2      # ha visto un item e sta cercando di raggiungerlo
    SEEK_STORAGE = 3    # ho preso l'item e sto andando allo store più vicino

class BaseStrategy(ABC):
    def __init__(self, num_goal: int, epsilon: float = 0.8):    #è necessario num_goal? per me no. gli agenti infatti non sanno quanti sono gli item e non gli interessa saperlo. --Antonio
        self.num_goal = num_goal
        self.epsilon = epsilon 
        self.status = AgentState.EXPLORE
        self.storages = []
        self.Path_target = []

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

    def _get_Path(self, start: Position, local_map: Map, target: Position) -> list[Position]:
        queue = deque([[start]])
        visited = {(start.x, start.y)}
        rows, cols = local_map.grid.shape

        while queue:
            path = queue.popleft()
            curr = path[-1]

            # siamo arrivati al target, restituiamo la rotta da seguire escludendo la posizione di partenza
            if curr.x == target.x and curr.y == target.y:
                return path[1:]

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = curr.x + dx, curr.y + dy
                
                if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                    cell_type = local_map.grid[nx, ny]
                    
                    if cell_type == CellType.Wall:
                        continue
                        
                    if self.status == AgentState.SEEK_STORAGE and cell_type == CellType.Exit:
                        continue
                        
                    if self.status != AgentState.SEEK_STORAGE and cell_type == CellType.Entrance:
                        continue

                    visited.add((nx, ny))
                    queue.append(path + [Position(nx, ny)])

        return []
    
    @abstractmethod
    def explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        pass

    def next_move(self, position: Position, local_map: Map, current_energy: int, carring: bool):
        # ________________________________________________________________________________ morto
        if current_energy <= 0: self.status = AgentState.DEAD
        if self.status == AgentState.DEAD: return None

        # ________________________________________________________________________________ esplora
        if self.status == AgentState.EXPLORE:
            #se trovo un item e non sto già portando un item allora inizia a raggiungerlo
            if self._find_nearest_target(position, local_map, CellType.Item) != (-1, -1) and carring == False:
                self.status = AgentState.REACH_ITEM
                return self.next_move(position, local_map, current_energy, carring)
            
            return self.explore_behavior(position, local_map)

        
        # ________________________________________________________________________________ raggiungi l'obbiettivo più vicino
        elif self.status == AgentState.REACH_ITEM: 
            if carring == True: # ha preso l'oggetto
                self.status = AgentState.SEEK_STORAGE
                self.Path_target = []
                return self.next_move(position, local_map, current_energy, carring)

            elif self.Path_target: # ho la rotta da seguire
                next_move_ = self.Path_target.pop(0)
                return (next_move_.x - position.x, next_move_.y - position.y)

            elif self._find_nearest_target(position, local_map, CellType.Item) != (-1,-1): # crea il path
                x_, y_ = self._find_nearest_target(position, local_map, CellType.Item)
                target_pos = Position(x_, y_)
                self.Path_target = self._get_Path(position, local_map, target_pos)
                if self.Path_target:
                    return self.next_move(position, local_map, current_energy, carring)
                else:
                    return (0, 0)

            else: # Non ha trovato più l'oggetto
                self.status = AgentState.EXPLORE
                return self.next_move(position, local_map, current_energy, carring)
                        

        # ________________________________________________________________________________ raggiungi lo storage più vicino
        if self.status == AgentState.SEEK_STORAGE:
            
            if carring == False: # ha depositato l'oggetto
                self.status = AgentState.EXPLORE
                self.Path_target = []
                return self.next_move(position, local_map, current_energy, carring)

            elif self.Path_target: # segui il path 
                next_move_ = self.Path_target.pop(0)
                return (next_move_.x - position.x, next_move_.y - position.y)

            elif self._find_nearest_target(position, local_map, CellType.Store) != (-1,-1): # crea il path
                x_, y_ = self._find_nearest_target(position, local_map, CellType.Store)
                target_pos = Position(x_, y_)
                self.Path_target = self._get_Path(position, local_map, target_pos)
                if self.Path_target:
                    return self.next_move(position, local_map, current_energy, carring)
                else:
                    return (0, 0)

            else:
                self.status = AgentState.EXPLORE
                return self.next_move(position, local_map, current_energy, carring)
                        
        return None
    

class RandomStrategy(BaseStrategy):

    def explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        return self._get_random_move() if random.random() < self.epsilon else (0, 0)


class ScoutStrategy(BaseStrategy):
    # va dritto finché non sbatte contro un muro, poi cambia direzione
    def __init__(self, epsilon: float = 0.8):
        super().__init__(epsilon)
        self.current_direction = self._get_random_move()

    def explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        rows, cols = local_map.grid.shape
        nx = position.x + self.current_direction[0]
        ny = position.y + self.current_direction[1]

        if not (0 <= nx < rows and 0 <= ny < cols) or \
           local_map.grid[nx, ny] == CellType.Wall or \
           random.random() < 0.05:
            
            self.current_direction = self._get_random_move()
            return (0, 0)
            
        return self.current_direction