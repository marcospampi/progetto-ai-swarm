from dataclasses import dataclass
from enum import Enum, IntEnum
import numpy as np

class CellType(IntEnum):
  unknown = -1
  Empty = 0
  Wall = 1
  Store = 2
  Entrance = 3  
  Exit = 4      
  Item = 5      
  Robot = 6


@dataclass
class Map:
  grid: np.matrix
  grid_metadata: dict

  def __init__(self, grid_width: int, grid_height: int):
    self.grid = np.zeros(shape=(grid_width, grid_height), dtype=CellType)
    self.grid_metadata = {}

  def __init__(self, grid_width: int, grid_height: int, value: int = 0): 
    self.grid = np.full((grid_width, grid_height), value, dtype=int)
    self.grid_metadata = {}
  
  def set_cell(self, position: tuple[int,int], cell_type: CellType, meta = None) -> None:
    self.grid[position] = cell_type
    if meta:
      self.grid_metadata[position] = meta

  def get_cell(self, position: tuple[int,int]) -> CellType:
    return self.grid[position]

  def print_map(self) -> None:  
        symbols = {0: " . ", 1: "###", -1: "   "} # 0: Vuoto, 1: Muro, 6: Robot
        
        print("-" * (self.grid.shape[1] * 3))
        for row in self.grid: 
            line = "".join([symbols.get(int(cell), f" {int(cell)} ") for cell in row])
            print(line)
        print("-" * (self.grid.shape[1] * 3))