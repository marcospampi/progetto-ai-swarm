import pygame
from map import Map, CellType
from pygame import Color, Rect

CELL_TYPE_COLORS = {
  CellType.Empty : Color('#f2f2f2'),
  CellType.Wall : Color('#444444'),
  CellType.Store : Color('#4990d8'),
  CellType.Item : Color('#FFD700'),
  CellType.Entrance : Color('#2bcc6f'),
  CellType.Exit : Color('#e74b3d'),
  CellType.Robot : Color('#BC6C25')
}

class Renderer:
  map: Map
  cell_size: int

  surface_width: int
  surface_height: int
  grid_color: Color = Color('#e0e0e0')
  _surface: pygame.Surface
  _bg: pygame.Surface
  def __init__(self, map: Map, cell_size: int = 24):
    self.map = map
    self.cell_size = cell_size

    pygame.init()

    self.surface_width = cell_size * map.grid.shape[0]
    self.surface_height = cell_size * map.grid.shape[1]

    self._surface = pygame.display.set_mode((
      self.surface_width,
      self.surface_height
    ))
  
    self._bg = pygame.Surface(self._surface.get_size())
    self._bg = self._bg.convert()
    self._bg.fill('white')


    
  def run_in_loop(self, fn: callable):
    while pygame.event.wait().type != pygame.QUIT:
      fn()
      self.render()
  
  def render(self):
    self._clear_screen()
    self._draw_cells()

    self._render_grid()


  def _draw_cells(self):
      cells = self.map.grid
      metadatas = self.map.grid_metadata
      for x in range(cells.shape[0]):
        for y in range(cells.shape[1]):
          cell_type = cells[x,y]
          meta = metadatas[(x,y)] if (x,y) in metadatas else None
          color = CELL_TYPE_COLORS[cell_type]
          
          
          rect = Rect(
            x * self.cell_size,
            y * self.cell_size,
            self.cell_size,
            self.cell_size
          )
          pygame.draw.rect(self._bg, color, rect)
          


  def _render_grid(self):


      for i in range(0, self.surface_height, self.cell_size):
        pygame.draw.line(self._bg, self.grid_color, (0,i),(self.surface_height, i))
      for i in range(0, self.surface_width, self.cell_size):
        pygame.draw.line(self._bg, self.grid_color, (i,0),(i, self.surface_width))

      self._surface.blit(self._bg, (0,0))
      pygame.display.flip()

  def _clear_screen(self):
      self._bg.fill('white')
