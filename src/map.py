from dataclasses import dataclass
from enum import Enum, IntEnum
import numpy as np

class CellType(IntEnum):
  # Sconosciuto
  unknown = -1
  # Corridoio
  Empty = 0
  # Muro / Scaffale
  Wall = 1
  # Magazzino
  Store = 2
  # Oggetto
  Item = 3
  # Entrata
  Entrance = 4
  # Uscita
  Exit = 5
  # Robot
  Robot = 6


@dataclass
class Map:
  grid: np.matrix
  grid_metadata: dict

  def __init__(self, grid_width: int, grid_height: int):
    self.grid = np.zeros(shape=(grid_width, grid_height), dtype=CellType)
    self.grid_metadata = {}

  def __init__(self, grid_width: int, grid_height: int, value: int = -1): 
        self.grid = np.full((grid_width, grid_height), value, dtype=int)
        self.grid_metadata = {}
  
  def set_cell(self, position: tuple[int,int], cell_type: CellType, meta = None):
    self.grid[position] = cell_type
    if meta:
      self.grid_metadata[position] = meta

  def get_cell(self, position: tuple[int,int], cell_type: CellType, meta = None):
    return cell_type 

  def print_map(self):  
        symbols = {0: " . ", 1: "###", -1: "   "} # 0: Vuoto, 1: Muro, 6: Robot
        
        print("-" * (self.grid.shape[1] * 3))
        for row in self.grid: 
            line = "".join([symbols.get(int(cell), f" {int(cell)} ") for cell in row])
            print(line)
        print("-" * (self.grid.shape[1] * 3))