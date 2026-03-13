import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.patches import Circle
from strategy import RandomStrategy, ScoutStrategy
from agent import Agente, Position, VisibilitySensor, CommunicationSensor
from map import Map
import parse_json
import json
import os
from datetime import datetime

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
        '#f2f2f2'  # 5: ITEM
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

    for obj in objects_truth:
        if isinstance(obj, dict):
            r, c = obj.get('x', 0), obj.get('y', 0)
        else:
            r, c = obj[0], obj[1]
            
        global_map.grid[r, c] = 5

    # --- INIZIALIZZAZIONE AGENTI ---
    agents = [
        Agente(
            Position(0, 0), 
            VisibilitySensor(reach=10, x_rays=False), 
            CommunicationSensor(radius=4.0),
            200, 
            Map(rows, cols, value=-1),
            RandomStrategy(0.8)
        ), 
        Agente(
            Position(0, 0), 
            VisibilitySensor(reach=3, x_rays=False), 
            CommunicationSensor(radius=4.0),
            100, 
            Map(rows, cols, value=-1),
            ScoutStrategy(0.8)
        ), 
        Agente(
            Position(0, 0), 
            VisibilitySensor(reach=3, x_rays=False), 
            CommunicationSensor(radius=4.0),
            100, 
            Map(rows, cols, value=-1),
            ScoutStrategy(0.8)
        ), 
        Agente(
            Position(0, 0),  
            VisibilitySensor(reach=3, x_rays=False), 
            CommunicationSensor(radius=4.0),
            100, 
            Map(rows, cols, value=-1),
            ScoutStrategy(0.8)
        ),
        Agente(
            Position(0, 0), 
            VisibilitySensor(reach=3, x_rays=False), 
            CommunicationSensor(radius=4.0),
            100, 
            Map(rows, cols, value=-1),
            ScoutStrategy(0.8)
        )
    ]

    # --- CONFIGURAZIONE LAYOUT GRAFICO ---
    num_agents = len(agents)
    fig = plt.figure(figsize=(16, 8))
    
    gs = fig.add_gridspec(num_agents, 4) 
    
    ax_global = fig.add_subplot(gs[:, :3])
    
    axs_local = [fig.add_subplot(gs[i, 3]) for i in range(num_agents)]
    
    plt.ion()

    max_ticks = 100
    
    agent_colors = ['orange', 'cyan', 'magenta', 'red']

    totale_oggetti = len(objects_truth)
    stats = {
        'oggetti_recuperati': 0,
        'tick_totali': 0
    }
    energie_iniziali = [agente.energy for agente in agents]

    # --- CICLO DI SIMULAZIONE ---
    for tick in range(max_ticks):
        ax_global.clear()
        
        ax_global.imshow(global_map.grid, cmap=global_cmap, norm=global_norm, origin='upper') 
        ax_global.set_title(f"Mappa Globale - Tick {tick}")
        
        for obj in objects_truth:
            r = obj.get('x', 0) if isinstance(obj, dict) else obj[0]
            c = obj.get('y', 0) if isinstance(obj, dict) else obj[1]
            
            if global_map.grid[r, c] == 5:
                ax_global.plot(c, r, "o", color='#FFD700', markersize=6)

        legend_handles = []

        cella_iniziale_occupata = any(
            a.is_active and a.position.x == 0 and a.position.y == 0 
            for a in agents
        )

        for i, agent in enumerate(agents):
            if not agent.is_active:
                if not cella_iniziale_occupata:
                    agent.is_active = True
                    cella_iniziale_occupata = True
                else:
                    continue

            agent.action(agents, global_map, stats)
            
            color = agent_colors[i] if i < len(agent_colors) else 'orange'
            
            ax_global.plot(agent.position.y, agent.position.x, "o", markersize=10, color=color)
            legend_handles.append(plt.Line2D([0], [0], marker='o', color=color, linestyle='', label=f'Agente {i+1}'))
            
            raggio = agent.communication_sensor.radius
            cerchio_radio = Circle((agent.position.y, agent.position.x), raggio, color=color, alpha=0.15, fill=True, linestyle='--', linewidth=1.5)
            
            ax_global.add_patch(cerchio_radio)

            axs_local[i].clear()
            axs_local[i].imshow(agent.local_map.grid, cmap=local_cmap, norm=local_norm, origin='upper')
            axs_local[i].set_title(f"Visuale Agente {i+1}", fontsize=10)
            
            axs_local[i].plot(agent.position.y, agent.position.x, "o", markersize=8, color=color)
            
            for obj in objects_truth:
                r = obj.get('x', 0) if isinstance(obj, dict) else obj[0]
                c = obj.get('y', 0) if isinstance(obj, dict) else obj[1]
                
                if agent.local_map.grid[r, c] == 5: 
                    axs_local[i].plot(c, r, "o", color='#FFD700', markersize=4)

            axs_local[i].axis('off')

        ax_global.legend(handles=legend_handles, loc="upper right")

        ax_global.set_xlim(-0.5, cols - 0.5)
        ax_global.set_ylim(rows - 0.5, -0.5)

        plt.pause(0.05)

    plt.ioff()
    plt.show()

    energie_consumate = [e_iniziale - a.energy for e_iniziale, a in zip(energie_iniziali, agents)]
    energia_media_consumata = sum(energie_consumate) / len(agents) if agents else 0

    # --- SALVATAGGIO SU JSON ---
    nome_file_risultati = "risultati_simulazione.json"
    
    dati_run = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mappa_utilizzata": args.mappa_json,
        "numero_agenti": len(agents),
        "oggetti_recuperati": stats['oggetti_recuperati'],
        "oggetti_totali": totale_oggetti,
        "tick_impiegati": stats['tick_totali'],
        "energia_media_consumata": round(energia_media_consumata, 2)
    }

    storico_risultati = []
    if os.path.exists("results/" + nome_file_risultati):
        try:
            with open("results/" + nome_file_risultati, "r") as f:
                storico_risultati = json.load(f)
        except json.JSONDecodeError:
            print("Attenzione: Il file JSON esistente era corrotto. Verrà sovrascritto.")

    storico_risultati.append(dati_run)

    with open("results/" + nome_file_risultati, "w") as f:
        json.dump(storico_risultati, f, indent=4)
        
    print(f"\n[INFO] Risultati salvati con successo in 'results/{nome_file_risultati}'")

if __name__ == '__main__':
    main()