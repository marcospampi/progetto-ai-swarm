from dataclasses import dataclass
from enum import Enum, IntEnum
import numpy as np

class CellType(IntEnum):
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
  
  def set_cell(self, position: tuple[int,int], cell_type: CellType, meta = None):
    self.grid[position] = cell_type
    if meta:
      self.grid_metadata[position] = meta