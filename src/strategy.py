import random
from collections import deque
from abc import ABC, abstractmethod
from map import Map, CellType
from geometry import Position
from enum import Enum
import math

class AgentState(Enum):
    DEAD = 0
    EXPLORE = 1
    REACH_ITEM = 2      # ha visto un item e sta cercando di raggiungerlo
    SEEK_STORAGE = 3    # ho preso l'item e sto andando allo store più vicino
    LOW_ENERGY = 4      # Energia < 20%, cerca il punto di relay


class BaseStrategy(ABC):
    def __init__(self, num_goal: int, storages: list, epsilon: float = 0.8):    #è necessario num_goal? per me no. gli agenti infatti non sanno quanti sono gli item e non gli interessa saperlo. --Antonio
        self.num_goal = num_goal
        self.epsilon = epsilon 
        self.status = AgentState.EXPLORE
        self.storages = storages
        self.Path_target = []

    num_goal: int
    epsilon: float
    status: AgentState
    storages: list
    Path_target: any
    
    """
    def __init__(self, num_goal: int, epsilon: float = 0.8):    #è necessario num_goal? per me no. gli agenti infatti non sanno quanti sono gli item e non gli interessa saperlo. --Antonio
        self.num_goal = num_goal
        self.epsilon = epsilon 
        self.status = AgentState.EXPLORE
        self.storages = []
        self.Path_target = None
    """
    
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
    
    #metodo che permette di trovare un punto di relay ottimale per la comunicazione quando l'agente si scarica. Cerca un punto libero spazioso e centrale rispetto alla propria mappa locale
    def _find_optimal_relay_spot(self, current_pos: Position, local_map: Map) -> Position:
        rows, cols = local_map.grid.shape
        empty_cells = []
    
        for r in range(rows):
            for c in range(cols):
                if local_map.grid[r, c] == CellType.Empty:
                    empty_cells.append((r, c))
                    
        if not empty_cells:
            return None
            
        # calcolo del centroide
        sum_r = sum(r for r, c in empty_cells)
        sum_c = sum(c for r, c in empty_cells)
        center_r = sum_r / len(empty_cells)
        center_c = sum_c / len(empty_cells)
        
        candidates = []
        
        # valutiamo lo spazio e la centralità di ogni cella
        for r, c in empty_cells:
            free_around = 0
            
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0: continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if local_map.grid[nr, nc] in [CellType.Empty, CellType.Entrance, CellType.Exit]:
                            free_around += 1
                            
            dist_to_center = math.sqrt((r - center_r)**2 + (c - center_c)**2)
            
            candidates.append({
                'pos': Position(r, c),
                'free_around': free_around,
                'dist_to_center': dist_to_center
            })
        
        max_free_available = max(c['free_around'] for c in candidates)
        acceptable_free_space = max(5, max_free_available)
        
        spacious_spots = [c for c in candidates if c['free_around'] >= acceptable_free_space]
        
        if not spacious_spots:
            spacious_spots = candidates
            
        # tra i posti larghi, scegliamo quello più vicino al centroide
        spacious_spots.sort(key=lambda x: x['dist_to_center'])
        
        return spacious_spots[0]['pos']
    
    @abstractmethod
    def explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        pass

    def next_move(self, position: Position, local_map: Map, current_energy: int, carring: bool):
        # ________________________________________________________________________________ morto
        if current_energy <= 0: 
            self.status = AgentState.DEAD
            return None
        
        # ________________________________________________________________________________ low energy
        if current_energy <= 20 and not carring and self.status != AgentState.LOW_ENERGY:
            self.status = AgentState.LOW_ENERGY
            target = self._find_optimal_relay_spot(position, local_map)
            self.Path_target = self._get_Path(position, local_map, target) if target else []

        if self.status == AgentState.LOW_ENERGY:
            if self.Path_target:
                nxt = self.Path_target.pop(0)
                return (nxt.x - position.x, nxt.y - position.y)
            return (0, 0)

        # ________________________________________________________________________________ esplora
        if self.status == AgentState.EXPLORE:
            if self._find_nearest_target(position, local_map, CellType.Item) != (-1, -1) and not carring:
                self.status = AgentState.REACH_ITEM
                return self.next_move(position, local_map, current_energy, carring)
            return self.explore_behavior(position, local_map)

        # ________________________________________________________________________________ raggiungi l'obbiettivo più vicino
        elif self.status == AgentState.REACH_ITEM: 
            if carring:
                self.status = AgentState.SEEK_STORAGE
                self.Path_target = []
                return self.next_move(position, local_map, current_energy, carring)

            coords = self._find_nearest_target(position, local_map, CellType.Item)
            if coords != (-1, -1):
                path = self._get_Path(position, local_map, Position(*coords))
                if path: return (path[0].x - position.x, path[0].y - position.y)

            self.status = AgentState.EXPLORE
            return self.next_move(position, local_map, current_energy, carring)

        # ________________________________________________________________________________ raggiungi lo storage più vicino
        if self.status == AgentState.SEEK_STORAGE:
            if not carring:
                self.status = AgentState.EXPLORE
                self.Path_target = []
                return self.next_move(position, local_map, current_energy, carring)

            coords = self._find_nearest_target(position, local_map, CellType.Store)
            if coords != (-1, -1):
                path = self._get_Path(position, local_map, Position(*coords))
                if path: return (path[0].x - position.x, path[0].y - position.y)

            self.status = AgentState.EXPLORE
            return self.next_move(position, local_map, current_energy, carring)
                        
        return None

class RandomStrategy(BaseStrategy):

    def explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        return self._get_random_move() if random.random() < self.epsilon else (0, 0)


# Strategia Utile (potrebbe essere la base per le strategie più sofisticate)
class ScoutStrategy(BaseStrategy):
    # dritto contro un muro poi cambia direzione
    def __init__(self, num_goal: int, storages: list, epsilon: float = 0.8):
        super().__init__(num_goal, storages, epsilon)
        self.current_direction = self._get_random_move()

    def explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        if random.random() < self.epsilon:
            return self._get_random_move()
        
        rows, cols = local_map.grid.shape
        nx = position.x + self.current_direction[0]
        ny = position.y + self.current_direction[1]

        if not (0 <= nx < rows and 0 <= ny < cols) or \
           local_map.grid[nx, ny] == CellType.Wall or \
           random.random() < 0.05:
            
            self.current_direction = self._get_random_move()
            return (0, 0)
            
        return self.current_direction

# Strategia Utile (potrebbe essere la base per le strategie più sofisticate)
class ScoutStrategy2(BaseStrategy):
    # esplorazione greedy, sempre verso l'ignoto
    def __init__(self, num_goal: int, storages: list, epsilon: float = 0.8):
        super().__init__(num_goal, storages, epsilon)
        self.current_direction = self._get_random_move()

    def explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:        
        if random.random() < self.epsilon:
            return self._get_random_move()
        
        t_coords = self._find_nearest_target(position, local_map, CellType.unknown)
        if t_coords != (-1, -1):
            target_pos = Position(*t_coords)
            path = self._get_Path(position, local_map, target_pos)
            if path:
                return (path[0].x - position.x, path[0].y - position.y)
                
        return (0, 0)
    

# STRATEGIA BOCCIATA (facile bloccarsi in cicli ridondanti)
class WallFollowerStrategy(BaseStrategy):
    # strategia da labirinto in cui si segue il muro, utile per struttura a corridoio
    def __init__(self, num_goal: int, storages: list, epsilon: float = 0.0):
        super().__init__(num_goal, storages, epsilon)
        self.dir = (0, 1)

    def explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        rows, cols = local_map.grid.shape
        right_dir = (self.dir[1], -self.dir[0])
        rx, ry = position.x + right_dir[0], position.y + right_dir[1]
        
        if 0 <= rx < rows and 0 <= ry < cols and local_map.grid[rx, ry] != CellType.Wall:
            self.dir = right_dir
            return self.dir
            
        fx, fy = position.x + self.dir[0], position.y + self.dir[1]
        if 0 <= fx < rows and 0 <= fy < cols and local_map.grid[fx, fy] != CellType.Wall:
            return self.dir
            
        self.dir = (-self.dir[1], self.dir[0])
        return self.dir

# STRATEGIA UTILE (ma in corridoi può portare stalli, meglio destinarla a singoli agenti esploratori)
class SparceStrategy(BaseStrategy):
    # evitiamo sovrapposizioni massimizzando l'esplorazione totale
    def __init__(self, num_goal: int, storages: list, epsilon: float = 0.2):
        super().__init__(num_goal, storages, epsilon)
        self.teammates = []

    def explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        if not self.teammates or random.random() < self.epsilon:
            return self._get_random_move()

        vx, vy = 0.0, 0.0
        for t in self.teammates:
            dist = abs(position.x - t.x) + abs(position.y - t.y)
            if 0 < dist < 5: 
                vx += (position.x - t.x) / dist
                vy += (position.y - t.y) / dist
        
        if vx == 0 and vy == 0:
            return self._get_random_move()

        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        best_move = max(moves, key=lambda m: m[0]*vx + m[1]*vy)
        
        nx, ny = position.x + best_move[0], position.y + best_move[1]
        rows, cols = local_map.grid.shape
        
        if 0 <= nx < rows and 0 <= ny < cols and local_map.grid[nx, ny] != CellType.Wall:
            return best_move
            
        return self._get_random_move()

# Serve che gli agenti interagiscano in modo dinamico e efficace per spartirsi dinamicamente lo spazio di ricerca

# UNIONE DI SPARCE E SCOUT2 (Sembra molto efficace per le operaie)
class SwarmExplorerStrategy(BaseStrategy):
    def __init__(self, num_goal: int, storages: list, epsilon: float = 0.1):
        super().__init__(num_goal, storages, epsilon)
        self.teammates = []

    def explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        if random.random() < self.epsilon:
            return self._get_random_move()

        rows, cols = local_map.grid.shape
        unknowns = [Position(i, j) for i in range(rows) for j in range(cols) if local_map.grid[i, j] == CellType.unknown]

        if not unknowns:
            return self._get_random_move()

        best_target = None
        best_score = float('inf')

        for unk in unknowns:
            my_dist = position.manhattan_distance_to(unk)
            teammate_penalty = 0
            
            for t in self.teammates:
                t_dist = abs(t.x - unk.x) + abs(t.y - unk.y)
                if t_dist <= my_dist:
                    teammate_penalty += 100 
                elif t_dist < 8:
                    teammate_penalty += (8 - t_dist) * 2

            score = my_dist + teammate_penalty
            if score < best_score:
                best_score = score
                best_target = unk

        if best_target:
            path = self._get_Path(position, local_map, best_target)
            if path:
                return (path[0].x - position.x, path[0].y - position.y)

        return self._get_random_move()
