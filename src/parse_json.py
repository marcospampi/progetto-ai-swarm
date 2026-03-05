import json

EMPTY, WALL, WAREHOUSE, ENTRANCE, EXIT = 0, 1, 2, 3, 4

with open("json/A.json", "r", encoding="utf-8") as f:
    env = json.load(f)

grid = env["grid"]
warehouses = env["warehouses"]
objects_truth = set(map(tuple, env["objects"]))  # solo riferimento simulatore

def is_walkable(r, c):
    return grid[r][c] in (EMPTY, ENTRANCE, EXIT) # Assicurarsi che ad esempio l'entrata e l'uscita siano percorribili solo in un senso (in base da dove viene l'agente)




