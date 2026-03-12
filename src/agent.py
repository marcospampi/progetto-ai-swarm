from geometry import Position, VisibilitySensor, CommunicationSensor
from map import Map, CellType
from strategy import Strategy


class Agente:
    def __init__(self, position: Position, visibility_sensor: VisibilitySensor,  communication_sensor: CommunicationSensor, energy: int, local_map: Map, strategy: Strategy):
        self.position = position
        self.visibility_sensor = visibility_sensor
        self.energy = energy
        self.communication_sensor = communication_sensor
        self.local_map = local_map
        self.strategy = strategy
        self.carring = False # Angelo


    def action(self, agents: list['Agente'], global_map: Map):
        self.visibility_sensor.update(self.position, self.local_map, global_map)
        self.communication_sensor.update(self, agents)
        move_vector = self.strategy.next_move(self.position, self.local_map, self.energy, self.carring)

        if move_vector is None: return

        dx, dy = move_vector 
        target_x = self.position.x + dx
        target_y = self.position.y + dy

        if 0 <= target_x < global_map.grid.shape[0] and 0 <= target_y < global_map.grid.shape[1]:
            if global_map.grid[target_x, target_y] not in (CellType.Wall, CellType.Entrance):                
                self.position.x = target_x
                self.position.y = target_y
                self.energy -= 1

        if global_map.grid[self.position.x, self.position.y] == CellType.Item and self.carring == False:
            self.carring = True
            global_map.grid[self.position.x, self.position.y] = CellType.Empty
            self.local_map.grid[self.position.x, self.position.y] = CellType.Empty

    def print_map(self) -> None:
        self.local_map.print_map()