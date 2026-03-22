from __future__ import annotations # FIX: Permette di usare Position come type hint dentro se stessa
import math
from collections import deque
from map import Map, CellType
from dataclasses import dataclass

@dataclass
class Position:
    x: int
    y: int

    def manhattan_distance_to(self, other: Position) -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def euclidean_distance_to(self, other: Position) -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def to_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)

    @staticmethod # Aggiunto decorator per correttezza
    def from_tuple(t: tuple[int, int]) -> Position:
        return Position(t[0], t[1])

