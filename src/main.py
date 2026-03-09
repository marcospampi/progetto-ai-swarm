import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import time

from projectUtils import Agente, Position, Visibility, Strategy
from map import Map, CellType
import parse_json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mappa_json", type=str)
    args = parser.parse_args()

    grid, warehouses, objects_truth = parse_json.load_environment(args.mappa_json)

    global_map_colors = [
        '#f2f2f2', # 0: EMPTY
        '#444444', # 1: WALL
        '#4990d8', # 2: STORE
        '#2bcc6f', # 3: ENTRANCE
        '#e74b3d', # 4: EXIT
        '#FFD700'  # 5: ITEM
    ]
    global_cmap = colors.ListedColormap(global_map_colors)
    global_bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5] 
    global_norm = colors.BoundaryNorm(global_bounds, global_cmap.N)

    local_map_colors = ['#000000'] + global_map_colors + ['#BC6C25'] 
    
    local_cmap = colors.ListedColormap(local_map_colors)
    local_bounds = [-1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5] 
    local_norm = colors.BoundaryNorm(local_bounds, local_cmap.N)


    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    global_map = Map(rows, cols)
    global_map.grid = np.array(grid)

    fig, (ax_global, ax_local) = plt.subplots(1, 2, figsize=(16, 8)) 
    plt.ion()

    max_ticks = 100

    agents = [Agente(
        Position(0, 0), 
        Visibility(reach=3, radius=0, x_rays=False), 
        100, 
        Map(rows, cols, value=-1),
        Strategy(1, 1, 100, 0)
    )]

    for tick in range(max_ticks):
        ax_global.clear()
        ax_local.clear()
        
        ax_global.imshow(global_map.grid, cmap=global_cmap, norm=global_norm, origin='upper') 
        ax_global.set_title(f"Mappa Globale - Tick {tick}")
        ax_global.legend([plt.Line2D([0], [0], marker='o', color='orange', linestyle='')], ['Agente'], loc="upper right")

        for agent in agents:
            agent.action(global_map)
            
            ax_global.plot(agent.position.y, agent.position.x, "o", markersize=10, color='orange')
            

        ax_local.imshow(agents[0].local_map.grid, cmap=local_cmap, norm=local_norm, origin='upper')
        ax_local.set_title(f"Mappa Locale (Percezione) - Tick {tick}")
        

        for agent in agents:
             ax_local.plot(agent.position.y, agent.position.x, "o", markersize=10, color='orange')


        ax_local.tick_params(axis='both', which='both', length=0, labelsize=0)

        plt.pause(0.05)

    plt.ioff()
    plt.show()

if __name__ == '__main__':
    main()