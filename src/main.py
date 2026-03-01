import pygame
from map import Map, CellType
from rendering import Renderer
from projectUtils import *  

mymap = Map(25,25)
bot = Agente(Pose(1, 1), Visibility(3, 0, False), 100, Map(25, 25, -1), Strategy(1,1, 100, 0))
t = 100

def loop():
    global t
    if t <= 0: return 
    mymap.set_cell((bot.position.x, bot.position.y), 0)
    bot.action(mymap)
    mymap.set_cell((bot.position.x, bot.position.y), 6)
    pygame.time.delay(50)
    bot.printMap() 
    t = t - 1

def main():
 
  renderer = Renderer(bot.localMap)
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

