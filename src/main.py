import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import json
import os
from datetime import datetime
from rich.console import Console

# Import moduli locali
from strategy import (RandomStrategy, ScoutStrategy2, 
                      SwarmExplorerStrategy, WallFollowerStrategy)
from agent import Agente, Position, VisibilitySensor, CommunicationSensor
from Logger import Logger_csv
from map import Map
import parse_json

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Swarm Intelligence Simulator")
    parser.add_argument("mappa_json", type=str, help="Percorso del file JSON della mappa")
    parser.add_argument("-g", "--graphics", action="store_true", help="Attiva la visualizzazione grafica")
    parser.add_argument("-v", "--verbose", action="store_true", help="Salva lo storico dettagliato in JSON")
    parser.add_argument("-i", "--iterations", type=int, default=1, help="Numero di simulazioni da eseguire")
    parser.add_argument("-t", "--max_ticks", type=int, default=500, help="Limite massimo di tick per run")
    args = parser.parse_args()

    # 1. Caricamento ambiente base
    grid_orig, warehouses, objects_truth = parse_json.load_environment(args.mappa_json)
    rows, cols = len(grid_orig), len(grid_orig[0]) if len(grid_orig) > 0 else 0
    totale_oggetti = len(objects_truth)
    storages = [(3,11), (3,11), (11,21), (21,11)] # Setup storage di default

    # Inizializza Logger
    logger = Logger_csv()

    # --- CICLO ITERAZIONI ---
    for n_run in range(args.iterations):
        console.rule(f"[bold green]Simulazione {n_run + 1}/{args.iterations}[/bold green]")
        
        # Reset Mappa Globale
        global_map = Map(rows, cols)
        global_map.grid = np.array(grid_orig)
        for obj in objects_truth:
            r, c = (obj.get('x', 0), obj.get('y', 0)) if isinstance(obj, dict) else (obj[0], obj[1])
            global_map.grid[r, c] = 5

        # Reset Agenti (Nuove istanze per ogni iterazione)
        agents = [
            Agente(Position(0, 0), VisibilitySensor(reach=5), CommunicationSensor(radius=5.0), 100, Map(rows, cols, value=-1), ScoutStrategy2(totale_oggetti, storages, 0.05)), 
            Agente(Position(0, 0), VisibilitySensor(reach=3), CommunicationSensor(radius=2.0), 150, Map(rows, cols, value=-1), SwarmExplorerStrategy(totale_oggetti, storages, 0.3)), 
            Agente(Position(0, 0), VisibilitySensor(reach=3), CommunicationSensor(radius=2.0), 150, Map(rows, cols, value=-1), SwarmExplorerStrategy(totale_oggetti, storages, 0.3)), 
            Agente(Position(0, 0), VisibilitySensor(reach=3), CommunicationSensor(radius=2.0), 150, Map(rows, cols, value=-1), SwarmExplorerStrategy(totale_oggetti, storages, 0.3)),
            Agente(Position(0, 0), VisibilitySensor(reach=3), CommunicationSensor(radius=2.0), 150, Map(rows, cols, value=-1), WallFollowerStrategy(totale_oggetti, storages, 0.4))
        ]

        # Setup Grafica se richiesta
        from graphics import Graphics
        graphics = Graphics(agents, global_map, objects_truth) if args.graphics else None
        if graphics: graphics.begin()

        stats = {'oggetti_recuperati': 0, 'tick_totali': 0}
        final_tick = 0

        # --- CICLO DI SIMULAZIONE (TICK) ---
        for tick in range(args.max_ticks):
            final_tick = tick
            
            agenti_operativi = [a for a in agents if (a.is_active and a.energy > 0) or (not a.is_active)]
            
            if not agenti_operativi:
                console.print("[bold red]Simulazione interrotta: tutti gli agenti sono scarichi![/bold red]")
                break

            cella_iniziale_occupata = any(a.is_active and a.position.x == 0 and a.position.y == 0 for a in agents)

            for agent in agents:
                if not agent.is_active:
                    if not cella_iniziale_occupata:
                        agent.is_active, cella_iniziale_occupata = True, True
                    else: continue
                
                agent.action(agents, global_map, stats)
            
            if graphics: graphics.draw(tick, cella_iniziale_occupata)
            
            if stats['oggetti_recuperati'] == totale_oggetti:
                console.print(f"[bold yellow]Obiettivo raggiunto al tick {tick}![/bold yellow]")
                break

        if graphics: graphics.end()

        # --- CALCOLO METRICHE E LOG ---
        energia_media = sum([a.initial_energy - a.energy for a in agents]) / len(agents)
        
        dati_run = {
            "iterazione": n_run + 1,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "mappa": args.mappa_json.split('/')[-1],
            "agenti": len(agents),
            "oggetti": f"{stats['oggetti_recuperati']}/{totale_oggetti}",
            "ticks": final_tick + 1,
            "energia_media_persa": round(energia_media, 2)
        }

        # Salvataggio CSV e Tabella Rich
        logger.log_run(dati_run, console=console)

        if args.verbose:
            path_json = "results/risultati_simulazione.json" # non volevo togliere il json al 100% 
            os.makedirs("results", exist_ok=True)
            storico = []
            if os.path.exists(path_json):
                with open(path_json, "r") as f:
                    try: storico = json.load(f)
                    except: storico = []
            storico.append(dati_run)
            with open(path_json, "w") as f:
                json.dump(storico, f, indent=4)

    console.print("\n[bold green] Tutte le iterazioni completate.[/bold green]")

if __name__ == '__main__':
    main()