from typing import Any

from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.pylab import Axes
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.patches import Circle

from agent import Agente
from map import Map

map_colors = [
  '#f2f2f2', # 0: EMPTY
  '#444444', # 1: WALL
  '#4990d8', # 2: STORE
  '#2bcc6f', # 3: ENTRANCE
  '#e74b3d', # 4: EXIT
  '#f2f2f2'  # 5: ITEM
]
global_cmap = colors.ListedColormap(map_colors)
global_bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5] 
global_norm = colors.BoundaryNorm(global_bounds, global_cmap.N)
local_map_colors = ['#000000'] + map_colors + ['#BC6C25'] 

local_cmap = colors.ListedColormap(local_map_colors)
local_bounds = [-1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5] 
local_norm = colors.BoundaryNorm(local_bounds, local_cmap.N)
agent_colors = ['orange', 'cyan', 'magenta', 'red', 'orange']

class Graphics:
  agents: list[Agente]
  map: Map
  objects_truth: Any
  num_agents: int
  fig: Figure
  gs: GridSpec
  ax_global: Axes
  ax_local: list[Axes]
  ax_energy: list[Axes]
  frame_rate: float
  def __init__(self, 
               agents: list[Agente], 
               map: Map,
               objects_truth: Any = {},
               frame_rate: float = 1/60
               ):
    self.agents = agents
    self.map = map
    self.frame_rate = frame_rate
    self.objects_truth = objects_truth
  
  def begin(self):
    self.num_agents = num_agents = len(self.agents)
    self.fig = plt.figure(figsize=(18, 8))
    
    self.gs = self.fig.add_gridspec(self.num_agents, 5, width_ratios=[1, 1, 1, 1.2, 0.3]) 
    
    self.ax_global = self.fig.add_subplot(self.gs[:, :3])
    self.axs_local = [self.fig.add_subplot(self.gs[i, 3]) for i in range(num_agents)]
    self.axs_energy = [self.fig.add_subplot(self.gs[i, 4]) for i in range(num_agents)]
    
    plt.ion()
  
 

  def _draw_agent(self, tick: int, i: int, agent: Agente, cella_iniziale_occupata: bool, legend_handles: list):
    if not agent.is_active and cella_iniziale_occupata:
      self.axs_local[i].clear()
      self.axs_local[i].axis('off')
      self.axs_energy[i].clear()
      self.axs_energy[i].axis('off')
      return
      
    color = agent_colors[i] if i < len(agent_colors) else 'orange'
    
    self.ax_global.plot(agent.position.y, agent.position.x, "o", markersize=10, color=color)
    legend_handles.append(plt.Line2D([0], [0], marker='o', color=color, linestyle='', label=f'Agente {i+1}'))
    
    raggio = agent.communication_sensor.radius
    cerchio_radio = Circle((agent.position.y, agent.position.x), raggio, color=color, alpha=0.15, fill=True, linestyle='--', linewidth=1.5)
    
    self.ax_global.add_patch(cerchio_radio)
    self.axs_local[i].clear()
    self.axs_local[i].imshow(agent.local_map.grid, cmap=local_cmap, norm=local_norm, origin='upper')
    self.axs_local[i].set_title(f"Visuale Agente {i+1}", fontsize=10)
    
    self.axs_local[i].plot(agent.position.y, agent.position.x, "o", markersize=8, color=color)
    
    for obj in self.objects_truth:
        r = obj.get('x', 0) if isinstance(obj, dict) else obj[0]
        c = obj.get('y', 0) if isinstance(obj, dict) else obj[1]
        
        if agent.local_map.grid[r, c] == 5: 
            self.axs_local[i].plot(c, r, "o", color='#FFD700', markersize=4)
    
    self.axs_local[i].axis('off')
    self.axs_energy[i].clear()
    
    energia_mostrata = max(0, agent.energy) 
    
    self.axs_energy[i].bar([''], [energia_mostrata], width=0.5)
    self.axs_energy[i].set_ylim(0, agent.initial_energy)
    self.axs_energy[i].set_xticks([])
    self.axs_energy[i].set_yticks([])
    for spine in self.axs_energy[i].spines.values():
        spine.set_visible(False)
        
    offset_y = agent.initial_energy * 0.05
    self.axs_energy[i].text(0, energia_mostrata + offset_y, f"{energia_mostrata}", 
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    if i == 0:
        self.axs_energy[i].set_title("Energia", fontsize=9)

  def draw(self, tick: int, cella_iniziale_occupata: bool):
    rows, cols = self.map.grid.shape
    self.ax_global.clear()

    self.ax_global.imshow(self.map.grid, cmap=global_cmap, norm=global_norm, origin='upper') 
    self.ax_global.set_title(f"Mappa Globale - Tick {tick + 1}")
    
    for obj in self.objects_truth:
      r = obj.get('x', 0) if isinstance(obj, dict) else obj[0]
      c = obj.get('y', 0) if isinstance(obj, dict) else obj[1]
      
      if self.map.grid[r, c] == 5:
          self.ax_global.plot(c, r, "o", color='#FFD700', markersize=6)
    
    legend_handles = []

    for i, agent in enumerate(self.agents):
      self._draw_agent(tick, i, agent, cella_iniziale_occupata, legend_handles)
    
    self.ax_global.legend(handles=legend_handles, loc="upper right")
    self.ax_global.set_xlim(-0.5, cols - 0.5)
    self.ax_global.set_ylim(rows - 0.5, -0.5)

    plt.pause(self.frame_rate)

  def end(self):
    plt.ioff()
    plt.show()
