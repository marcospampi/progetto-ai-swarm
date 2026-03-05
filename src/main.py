import pygame
from map import Map, CellType
from rendering import Renderer
from projectUtils import *  

mymap = Map(25,25)
bot = Agente(Position(6, 1), Visibility(3, 0, False), 100, Map(25, 25, -1), Strategy(1,1, 100, 0))
mymap.set_cell((6,2), CellType.Wall)
t = 100

def loop():
    global t
    if t <= 0: return 

    mymap.set_cell((bot.position.x, bot.position.y), CellType.Robot)
    bot.local_map.set_cell((bot.position.x, bot.position.y), CellType.Empty)

    bot.action(mymap)

    bot.local_map.set_cell((bot.position.x, bot.position.y), CellType.Robot)
    mymap.set_cell((bot.position.x, bot.position.y), CellType.Robot)

    pygame.time.delay(50)
    bot.print_map() 
    t -= 1

def main():
 
  renderer = Renderer(bot.local_map)
  renderer.run_in_loop(loop)


if __name__ == '__main__':
  main()

