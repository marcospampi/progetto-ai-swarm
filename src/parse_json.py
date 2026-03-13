import json

EMPTY, WALL, WAREHOUSE, ENTRANCE, EXIT = 0, 1, 2, 3, 4

def load_environment(filepath: str) -> tuple:
    
    with open(filepath, "r", encoding="utf-8") as f:
        env = json.load(f)

    grid = env["grid"]
    warehouses = env["warehouses"]
    objects_truth = set(map(tuple, env["objects"]))
    
    return grid, warehouses, objects_truth

def is_walkable(grid, r, c):
    return grid[r][c] in (EMPTY, ENTRANCE, EXIT)

