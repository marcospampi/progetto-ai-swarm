import pygame
from map import Map, CellType
from rendering import Renderer


def main():

  mymap = Map(24,24)

  

  renderer = Renderer(mymap)

  def loop():
    pass

  renderer.run_in_loop(loop)

  
  #pygame.init()
  #cell_size = 24
  #cell_count = 25
  #window_quad_len = cell_size * cell_count
  #screen = pygame.display.set_mode((window_quad_len,window_quad_len))
  #pygame.display.set_caption("Simulazione")
  #bg = pygame.Surface(screen.get_size())
  #bg = bg.convert()
  #bg.fill('white')  
  #
  #grid_color = pygame.Color('#aaaaaa')
  #while pygame.event.wait().type != pygame.QUIT:
  #
  #  for i in range(0, window_quad_len, cell_size ):
  #    pygame.draw.line(bg, grid_color, (0,i),(window_quad_len, i))
  #    pygame.draw.line(bg, grid_color, (i,0),(i, window_quad_len))
  #  screen.blit(bg, (0,0))
  #  pygame.display.flip()
    

if __name__ == '__main__':
  main()

