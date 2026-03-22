from geometry import Position
from sensors import VisibilitySensor, CommunicationSensor
from map import Map, CellType
from strategy import BaseStrategy




class Agente:
    position: Position
    visibility_sensor: VisibilitySensor
    initial_energy: int
    energy: int
    communication_sensor: CommunicationSensor
    local_map: Map
    strategy: BaseStrategy

    def __init__(self, position: Position, visibility_sensor: VisibilitySensor,  communication_sensor: CommunicationSensor, energy: int, local_map: Map, strategy: BaseStrategy):
        self.position = position
        self.visibility_sensor = visibility_sensor
        self.energy = self.initial_energy = energy
        self.communication_sensor = communication_sensor
        self.local_map = local_map
        self.strategy = strategy
        self.carrying = False
        self.is_active = False #l'agente parte inattivo. diventa attivo quando la posizione (0, 0) si libera, in questo modo si evita che più agenti partano sovrapposti

    def action(self, agents: list['Agente'], global_map: Map, stats : dict) -> None:
        self.visibility_sensor.update(self.position, self.local_map, global_map)
        self.communication_sensor.update(self, agents)

        if hasattr(self.strategy, 'teammates'):
            self.strategy.teammates = [
                altro.position for altro in agents 
                if altro is not self and altro.is_active and altro.strategy.status.value != 0
            ]

        move_vector = self.strategy.next_move(self.position, self.local_map, self.energy, self.carrying)

        if move_vector is None: return

        dx, dy = move_vector 
        target_x = self.position.x + dx
        target_y = self.position.y + dy

        if 0 <= target_x < global_map.grid.shape[0] and 0 <= target_y < global_map.grid.shape[1]:
            #logica di non sovrapposizione tra agenti
            if global_map.grid[target_x, target_y] != CellType.Wall:
                
                cella_occupata = False
                for altro_robot in agents:
                    if altro_robot is not self:
                        if altro_robot.position.x == target_x and altro_robot.position.y == target_y:
                            cella_occupata = True
                            break
                
                if not cella_occupata:
                    self.position.x = target_x
                    self.position.y = target_y
                    self.energy -= 1

                else:
                    move_alt = self.strategy.collision_event(self.position, self.local_map, agents)
                    if move_alt != (0, 0):
                        self.position.x += move_alt[0]
                        self.position.y += move_alt[1]
                        self.energy -= 1

        if global_map.grid[self.position.x, self.position.y] == CellType.Item and self.carrying == False:
            self.carrying = True
            global_map.grid[self.position.x, self.position.y] = CellType.Empty
            self.local_map.grid[self.position.x, self.position.y] = CellType.Empty

        elif global_map.grid[self.position.x, self.position.y] == CellType.Store and self.carrying == True:
            self.carrying = False
            stats['oggetti_recuperati'] += 1

    def print_map(self) -> None:
        self.local_map.print_map()