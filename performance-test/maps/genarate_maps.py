import random
import numpy as np
import json

def generate_map(map_size):
    current_map=[]
    agents = ["agent-0", "agent-1", "agent-2"]
    for x in range(map_size):
        current_map.append(np.random.choice([0,1],map_size,p=[0.8,0.2]).tolist())
    generated_map = put_agents_in_map(current_map, agents)
    return generated_map

def get_random_free_position(my_map, num_of_agents):
    positions = []
    while len(positions) < num_of_agents:
        x = random.randint(0, len(my_map) - 1)
        y = random.randint(0, len(my_map) - 1)
        if my_map[x][y] == 0:
            positions.append([x, y])
    return positions

def put_agents_in_map(current_map, agents):
    for agent, position in zip(agents, get_random_free_position(current_map, len(agents))):
        current_map[position[0]][position[1]] = f"{agent}-start"
    for agent, position in zip(agents, get_random_free_position(current_map, len(agents))):
        current_map[position[0]][position[1]] = f"{agent}-end"
    return current_map


sizes= [21,23,25,27,29,31]
for size in sizes:
    with open(f'{size}.json', 'w') as outfile:
        json.dump(generate_map(size), outfile)