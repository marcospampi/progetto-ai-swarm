import random
from collections import deque
from abc import ABC, abstractmethod
from map import Map, CellType
from geometry import Position
from enum import IntEnum
import math

class AgentState(IntEnum):
    DEAD = 0
    EXPLORE = 1
    REACH_ITEM = 2      # ha visto un item e sta cercando di raggiungerlo
    SEEK_STORAGE = 3    # ho preso l'item e sto andando allo store più vicino
    LOW_ENERGY = 4      # Energia < 20%, cerca il punto di relay


class BaseStrategy(ABC):
    def __init__(self, epsilon: float = 0.8):
        self.epsilon = epsilon 
        self.status = AgentState.EXPLORE
        self.path_target = []
        self.min_energy_threshold = 20

        self.tabu_list = deque(maxlen=10) # Ricorda le ultime 10 posizioni
        self.tabu_tenure = 10
    
    def _get_random_move(self) -> tuple[int, int]: 
        # restituisce una mossa casuale tra le 4 direzioni cardinali
        return random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])

    def _find_nearest_target(self, current_pos : Position, local_map: Map, target_type: int) -> tuple[int, int]:
        # restituisce le coordinate del target più vicino del tipo specificato, o (-1, -1) se non trovato
        rows, cols = local_map.grid.shape
        targets = [Position(i, j) for i in range(rows) for j in range(cols) if local_map.grid[i, j] == target_type]
        
        if not targets: return (-1, -1)
        
        nearest = min(targets, key=lambda t: current_pos.manhattan_distance_to(t))
        return (nearest.x, nearest.y)

    def _is_tabu(self, x, y) -> bool:
        # controlla se la posizione (x, y) è nella tabu list
        return (x, y) in self.tabu_list

    def _update_tabu(self, current_pos: Position):
        # aggiunge la posizione corrente alla tabu list, mantenendo la dimensione massima
        self.tabu_list.append((current_pos.x, current_pos.y))

    def _get_filtered_moves(self, position: Position, local_map: Map):
        # restituisce le mosse valide (non muri) e preferisce quelle non tabu, se disponibili
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        valid_moves, tabu_moves = [], []
        for dx, dy in moves:
            nx, ny = position.x + dx, position.y + dy
            if (0 <= nx < local_map.grid.shape[0] and 0 <= ny < local_map.grid.shape[1] and local_map.grid[nx, ny] != CellType.Wall):
                if self._is_tabu(nx, ny): tabu_moves.append((dx, dy))
                else: valid_moves.append((dx, dy))
        return valid_moves if valid_moves else tabu_moves

    def _get_path(self, start: Position, local_map: Map, target: Position) -> list[Position]:
        # restituisce una lista di posizioni che rappresentano il percorso più breve da start a target usando BFS, o [] se non raggiungibile
        rows, cols = local_map.grid.shape
        if not (0 <= target.x < rows and 0 <= target.y < cols) or \
           local_map.grid[target.x, target.y] == CellType.Wall:
            return []

        queue = deque([[start]])
        visited = {(start.x, start.y)}

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
    
    def _find_optimal_relay_spot(self, current_pos: Position, local_map: Map) -> Position:
        # trova la posizione ottimale per il relay quando l'agente è a corto di energia, considerando spazio libero e distanza al centro dell'area esplorabile
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
    def _explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        # da implementare nelle strategie specifiche, definisce il comportamento di esplorazione (quando non ci sono target visibili)
        pass

    def next_move(self, position: Position, local_map: Map, current_energy: int, carring: bool) -> tuple[int, int]:
        # restituisce la prossima mossa come (dx, dy) in base allo stato attuale, alla mappa locale e all'energia residua. 
        # Gestisce anche la logica di transizione tra stati e l'aggiornamento della tabu list.
        self._update_tabu(position)
        
        # 1. GESTIONE MORTE
        if current_energy <= 0:
            self.status = AgentState.DEAD
            return None

        # 2. GESTIONE EMERGENZA ENERGIA (priorità assoluta)
        if current_energy <= self.min_energy_threshold and not carring:
            if self.status != AgentState.LOW_ENERGY:
                self.status = AgentState.LOW_ENERGY
                target = self._find_optimal_relay_spot(position, local_map)
                self.path_target = self._get_path(position, local_map, target) if target else []

        # 3. COMPORTAMENTO BASATO SULLO STATO
        if self.status == AgentState.LOW_ENERGY:
            if self.path_target:
                nxt = self.path_target.pop(0)
                return (nxt.x - position.x, nxt.y - position.y)
            return (0, 0)

        if self.status == AgentState.EXPLORE:
            target_coords = self._find_nearest_target(position, local_map, CellType.Item)
            if target_coords != (-1, -1) and not carring:
                self.status = AgentState.REACH_ITEM
            else:
                return self._explore_behavior(position, local_map)

        if self.status == AgentState.REACH_ITEM:
            if carring: 
                self.status, self.path_target = AgentState.SEEK_STORAGE, []
                return (0, 0)

            if not self.path_target:
                coords = self._find_nearest_target(position, local_map, CellType.Item)
                if coords != (-1, -1):
                    self.path_target = self._get_path(position, local_map, Position(*coords))

            if self.path_target:
                nxt = self.path_target.pop(0)
                return (nxt.x - position.x, nxt.y - position.y)

            self.status = AgentState.EXPLORE # l'item è stato preso da qualcun'altro
            return self._explore_behavior(position, local_map)

        if self.status == AgentState.SEEK_STORAGE:
            if not carring:
                self.status, self.path_target = AgentState.EXPLORE, []
                return (0, 0)
            
            if not self.path_target:
                coords = self._find_nearest_target(position, local_map, CellType.Store)
                if coords != (-1, -1):
                    self.path_target = self._get_path(position, local_map, Position(*coords))
            
            if self.path_target:
                nxt = self.path_target.pop(0)
                return (nxt.x - position.x, nxt.y - position.y)
            return self._explore_behavior(position, local_map)

        return (0, 0)

    def collision_event(self, current_pos: Position, local_map: Map, agents: list) -> tuple[int, int]:
        # restituisce una mossa alternativa quando la mossa originale è bloccata da un altro agente, cercando di spostarsi lateralmente o indietro per evitare il blocco
        self.path_target = []
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        random.shuffle(directions)
        rows, cols = local_map.grid.shape
        
        for dx, dy in directions:
            tx, ty = current_pos.x + dx, current_pos.y + dy
            
            if 0 <= tx < rows and 0 <= ty < cols:
                if local_map.grid[tx, ty] != CellType.Wall:
                    
                    cella_occupata = any(
                        a.position.x == tx and a.position.y == ty 
                        for a in agents if a.is_active
                    )
                    if not cella_occupata:
                        return (dx, dy)
        return (0, 0)


class RandomStrategy(BaseStrategy):
    # strategia di base, si muove casualmente senza considerare la mappa o lo stato
    def _explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        moves = self._get_filtered_moves(position, local_map)
        if moves:
            return random.choice(moves) if moves else (0, 0)
        return self._get_random_move()
        
class ScoutStrategy(BaseStrategy):
    # esplorazione greedy, cerca di andare sempre in una direzione finché non incontra un ostacolo o una posizione tabu, poi cambia direzione casualmente
    def __init__(self, epsilon: float = 0.8):
        super().__init__(epsilon)
        self.current_direction = self._get_random_move()

    def _explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        # con probabilità epsilon, ignora la direzione attuale e sceglie una mossa casuale filtrata (preferendo quelle non tabu)
        if random.random() < self.epsilon:
            moves = self._get_filtered_moves(position, local_map)
            return random.choice(moves) if moves else (0,0)
        
        rows, cols = local_map.grid.shape
        nx = position.x + self.current_direction[0]
        ny = position.y + self.current_direction[1]

        if not (0 <= nx < rows and 0 <= ny < cols) or \
           local_map.grid[nx, ny] == CellType.Wall or \
           self._is_tabu(nx, ny):
            
            moves = self._get_filtered_moves(position, local_map)
            self.current_direction = random.choice(moves) if moves else self._get_random_move()
            return (0, 0)
            
        return self.current_direction

class ScoutStrategy2(BaseStrategy):
    # simile a ScoutStrategy ma con una logica più intelligente per cambiare direzione: cerca di dirigersi verso le celle sconosciute più vicine, evitando quelle tabu e tenendo conto della presenza di altri agenti (se forniti)
    def _explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:        
        if random.random() < self.epsilon:
            moves = self._get_filtered_moves(position, local_map)
            return random.choice(moves) if moves else (0,0)
        
        t_coords = self._find_nearest_target(position, local_map, CellType.unknown)
        if t_coords != (-1, -1):
            target_pos = Position(*t_coords)
            path = self._get_path(position, local_map, target_pos)
            if path:
                nxt = path[0]
                if not self._is_tabu(nxt.x, nxt.y):
                    return (path[0].x - position.x, path[0].y - position.y)
                
        moves = self._get_filtered_moves(position, local_map)
        return random.choice(moves) if moves else (0, 0)
    
class WallFollowerStrategy(BaseStrategy):
# strategia da labirinto in cui si segue il muro, utile per struttura a corridoio. Bocciata perché è facile bloccarsi in cicli ridondanti
    def __init__(self, epsilon: float = 0.0):
        super().__init__(epsilon)
        self.dir = (0, 1)

    def _explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        rows, cols = local_map.grid.shape
        right_dir = (self.dir[1], -self.dir[0])
        rx, ry = position.x + right_dir[0], position.y + right_dir[1]
        
        if 0 <= rx < rows and 0 <= ry < cols and local_map.grid[rx, ry] != CellType.Wall:
            if not self._is_tabu(rx, ry):
                self.dir = right_dir
                return self.dir
            
        fx, fy = position.x + self.dir[0], position.y + self.dir[1]
        if 0 <= fx < rows and 0 <= fy < cols and local_map.grid[fx, fy] != CellType.Wall:
            if not self._is_tabu(fx, fy):
                return self.dir
            
        self.dir = (-self.dir[1], self.dir[0])
        return self.dir
    
class SparceStrategy(BaseStrategy):
    # strategia che cerca di mantenere una certa distanza dagli altri agenti, preferendo muoversi verso aree meno esplorate e meno frequentate dai compagni, per massimizzare la copertura della mappa e ridurre le sovrapposizioni nei percorsi di esplorazione.
    # utile, ma in corridoi può portare stalli, meglio destinarla a singoli agenti esploratori
    def __init__(self, epsilon: float = 0.2):
        super().__init__(epsilon)
        self.teammates = []

    def _explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        moves = self._get_filtered_moves(position, local_map)
        if not self.teammates or random.random() < self.epsilon:
            return random.choice(moves) if moves else (0, 0)

        vx, vy = 0.0, 0.0
        for t in self.teammates:
            dist = abs(position.x - t.x) + abs(position.y - t.y)
            if 0 < dist < 3: 
                vx += (position.x - t.x) / dist
                vy += (position.y - t.y) / dist
        
        if vx == 0 and vy == 0:
            return random.choice(moves) if moves else (0, 0)

        best_move = max(moves, key=lambda m: m[0]*vx + m[1]*vy)
        return best_move

class SwarmExplorerStrategy(BaseStrategy):
    # Serve che gli agenti interagiscano in modo dinamico e efficace per spartirsi dinamicamente lo spazio di ricerca.
    # UNIONE DI SPARCE E SCOUT2 (Sembra molto efficace per le operaie)
    def __init__(self, epsilon: float = 0.1):
        super().__init__(epsilon)
        self.teammates = []

    def _explore_behavior(self, position: Position, local_map: Map) -> tuple[int, int]:
        if random.random() < self.epsilon:
            # --Tabu Filtered--
            moves = self._get_filtered_moves(position, local_map)
            return random.choice(moves) if moves else (0, 0)

        rows, cols = local_map.grid.shape
        unknowns = [Position(i, j) for i in range(rows) for j in range(cols) if local_map.grid[i, j] == CellType.unknown]

        if not unknowns:
            moves = self._get_filtered_moves(position, local_map)
            return random.choice(moves) if moves else (0, 0)

        best_target = None
        best_score = float('inf')

        for unk in unknowns:
            my_dist = position.manhattan_distance_to(unk)
            teammate_penalty = 0
            tabu_penalty = 20 if self._is_tabu(unk.x, unk.y) else 0
            
            for t in self.teammates:
                t_dist = abs(t.x - unk.x) + abs(t.y - unk.y)
                if t_dist <= my_dist:
                    teammate_penalty += 100 
                elif t_dist < 8:
                    teammate_penalty += (8 - t_dist) * 2

            score = my_dist + teammate_penalty + tabu_penalty
            if score < best_score:
                best_score = score
                best_target = unk

        if best_target:
            path = self._get_path(position, local_map, best_target)
            if path:
                return (path[0].x - position.x, path[0].y - position.y)

        moves = self._get_filtered_moves(position, local_map)
        return random.choice(moves) if moves else (0, 0)