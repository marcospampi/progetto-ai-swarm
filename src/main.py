import argparse
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

from projectUtils import Agente, Position, Visibility, Strategy
from map import Map, CellType
import parse_json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mappa_json", type=str)
    args = parser.parse_args()

    grid, warehouses, objects_truth = parse_json.load_environment(args.mappa_json)

    map_colors = [
        '#f2f2f2',
        '#444444',
        '#4990d8',
        '#2bcc6f',
        '#e74b3d'
    ]

    cmap_consegna = colors.ListedColormap(map_colors)
    bounds = [0, 1, 2, 3, 4, 5]
    norm = colors.BoundaryNorm(bounds, cmap_consegna.N)

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    global_map = Map(rows, cols)
    global_map.grid = np.array(grid)

    fig, ax = plt.subplots(figsize=(8, 8))
    plt.ion()

    max_ticks = 100

    agents = [Agente(
        Position(0, 0), 
        Visibility(3, 0, False), 
        100, 
        Map(rows, cols), 
        Strategy(1, 1, 100, 0)
    )]

    for tick in range(max_ticks):
        ax.clear()
        
        ax.imshow(global_map.grid, cmap=cmap_consegna, norm=norm, origin='upper') 

        for agent in agents:
            agent.action(global_map)
            ax.plot(agent.position.y, agent.position.x, "s", markersize=10, color='#BC6C25', label="Agente")
            
        ax.set_title(f"Tick {tick}")
        ax.legend(loc="upper right", fontsize=7)
        plt.pause(0.05)

    plt.ioff()
    plt.show()

if __name__ == '__main__':
    main()