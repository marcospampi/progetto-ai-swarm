import matplotlib.pyplot as plt
import numpy as np
import time

from projectUtils import Agente, Position, Visibility, Strategy
from map import *
from parse_json import *


rows = len(grid)
cols = len(grid[0]) if rows > 0 else 0

global_map = Map(rows, cols)
global_map.grid = np.array(grid)


fig, ax = plt.subplots(figsize=(8, 8))
plt.ion()

max_ticks = 100


agents = [Agente(
    Position(6, 1), 
    Visibility(3, 0, False), 
    100, 
    Map(rows, cols), 
    Strategy(1, 1, 100, 0)
)]


for tick in range(max_ticks):
    ax.clear()
    
    ax.imshow(global_map.grid, cmap='gray_r') 

    for agent in agents:

        agent.action(global_map)
        ax.plot(agent.position.y, agent.position.x, "o", markersize=8, color='orange', label="Agente")
        
    ax.set_title(f"Tick {tick}")
    ax.legend(loc="upper right", fontsize=7)
    plt.pause(0.05)

plt.ioff()
plt.show()