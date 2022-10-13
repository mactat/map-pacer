import algo_lib
from algo_lib_3d import Grid_map, PATH_TILES_DICT
import numpy as np

def simple_map_3d():
    simple_map = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ])

    grid_map = Grid_map(mode="no_diag", head_collision_allowed=False)
    grid_map.load_from_list(simple_map)

    #A* agent 1
    grid_map.agent_color = PATH_TILES_DICT[1]
    start = (2, 0) 
    end = (2, 4) 
    possible_1, path_1 = grid_map.a_star(start, end)

    # A* agent 2
    grid_map.agent_color = PATH_TILES_DICT[2]
    start = (2, 4) 
    end = (2, 0) 
    possible_2, path_2 = grid_map.a_star(start, end)

    # A* agent 3
    grid_map.agent_color = PATH_TILES_DICT[3]
    start = (0, 0) 
    end = (4, 4) 
    possible_3, path_3 = grid_map.a_star(start, end)

    grid_map.print_timegrid(speed=2, clear=True)


def medium_map_3d():
    # more complecated map
    large_map = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 0, 1, 0],
        [0, 1, 1, 1, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 0, 1, 0, 1, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ])

    grid_map = Grid_map(mode="no_diag")
    grid_map.load_from_list(large_map)

    # A* agent 1
    grid_map.agent_color = PATH_TILES_DICT[1]
    start = (9, 8) 
    end = (5, 5) 
    possible_1, path_1 = grid_map.a_star(start, end)

    # A* agent 2
    grid_map = Grid_map(mode="no_diag")
    grid_map.load_from_list(large_map)
    grid_map.agent_color = PATH_TILES_DICT[2]
    grid_map.mark_path_on_grid(path_1)
    start = (5, 9) 
    end = (9, 9) 
    possible_2, path_2 = grid_map.a_star(start, end)

    # # A* agent 3
    grid_map = Grid_map(mode="no_diag")
    grid_map.load_from_list(large_map)
    grid_map.agent_color = PATH_TILES_DICT[3]
    grid_map.mark_path_on_grid(path_1)
    grid_map.mark_path_on_grid(path_2)
    start = (9, 9) 
    end = (5, 9) 
    possible_3, path_3 = grid_map.a_star(start, end)


    grid_map.print_timegrid(speed=4, clear=True)

def random_map_3d(map_size, num_of_agent):
    # Random huge map
    grid_map = Grid_map(mode="no_diag", head_collision_allowed=False)
    huge_map = []
    for x in range(map_size):
        huge_map.append(np.random.choice([0,1],map_size,p=[0.7,0.3]).tolist())
    grid_map.load_from_list(huge_map)

    # random start and end, not obstacle
    def random_point(new_map):
        while True:
            x = np.random.randint(0, map_size)
            y = np.random.randint(0, map_size)
            if new_map[x][y] == 0:
                new_map[x][y] = 1
                return new_map, (x, y)

    for i in range(num_of_agent):
        grid_map.agent_color = PATH_TILES_DICT[i%len(PATH_TILES_DICT)]
        huge_map, start = random_point(huge_map)
        huge_map, end = random_point(huge_map)
        found, _ = grid_map.a_star(start, end)
        print(f"Agent {i+1} done. Path found: {found}")
    grid_map.print_timegrid(speed=4, clear=True)

if __name__ == "__main__":
    simple_map_3d()
    medium_map_3d()
    random_map_3d(20, 20)



