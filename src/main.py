import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.patches import Circle
from strategy import RandomStrategy, ScoutStrategy
from agent import Agente, Position, VisibilitySensor, CommunicationSensor
from map import Map
from graphics import Graphics
import parse_json
import json
import os
from datetime import datetime

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mappa_json", type=str)
    parser.add_argument("-g", "--graphics", nargs='?', const=True, default=False)
    args = parser.parse_args()

    grid, warehouses, objects_truth = parse_json.load_environment(args.mappa_json)
    # todo!: refactor map begin
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
    # todo!: refactor map end


    # todo!: refactor agent initialization begin

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

    # todo!: refactor agent initialization end

    # --- CONFIGURAZIONE LAYOUT GRAFICO ---
    graphics = Graphics(agents, global_map, objects_truth) if args.graphics else None

    max_ticks = 150
    
    totale_oggetti = len(objects_truth)
    stats = {
        'oggetti_recuperati': 0,
        'tick_totali': 0
    }

    if graphics: graphics.begin()

    # --- CICLO DI SIMULAZIONE ---
    for tick in range(max_ticks):
        cella_iniziale_occupata = any(
            a.is_active and a.position.x == 0 and a.position.y == 0 
            for a in agents
        )

        for i, agent in enumerate(agents):
            if not agent.is_active:
                if not cella_iniziale_occupata:
                    # logica non di draw
                    agent.is_active = True
                    cella_iniziale_occupata = True
                else:
                    continue

            agent.action(agents, global_map, stats)
            
            
        if graphics: graphics.draw(tick, cella_iniziale_occupata)

    if graphics: graphics.end()

    energie_consumate = [a.initial_energy - a.energy for a in agents]
    energia_media_consumata = sum(energie_consumate) / len(agents) if agents else 0

    # --- SALVATAGGIO SU JSON ---
    nome_file_risultati = "risultati_simulazione.json"
    
    dati_run = {
        "timestamp": datetime.now().isoformat(),
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