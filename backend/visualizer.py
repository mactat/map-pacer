import copy
WALL = "⬛"
EMPTY = "⬜"
PATH_TILES_DICT = {
    0: EMPTY,
    1: WALL,
    2: "🟥",
    3: "🟦",
    4: "🟩",
    5: "🟨",
    6: "🟧",
    7: "🟪",
    8: "🟫"
}

#circles with same color as tiles
INITIAL_TILES_DICT = {
    0: "⚪",
    1: "⚫",
    2: "🔴",
    3: "🔵",
    4: "🟢",
    5: "🟡",
    6: "🟠",
    7: "🟣",
    8: "⚫"
}

def map_to_tile(my_map):
    return [[PATH_TILES_DICT[tile] for tile in row] for row in my_map]

def map_to_string(my_map):
    return "<br>".join(["".join(row) for row in my_map])

def mark_paths(normal_map, paths):
    if len(paths) == 0:
        return [normal_map]
    for path in paths:
        if path == "not found":
            paths.remove(path)
    # find longest path
    longest_path = len(max(paths, key=len))
    # create an array with longest path * map
    marked_map_times = [copy.deepcopy(normal_map) for _ in range(longest_path)]

    for timestamp in range(longest_path):
        for agent_num, path in enumerate(paths):
            start_tile, end_tile = path[0], path[-1]
            if timestamp >= len(path): tile = end_tile
            else: tile = path[timestamp]
            # mark begining and end of path
            if(marked_map_times[timestamp][start_tile[0]][start_tile[1]] == EMPTY):
                marked_map_times[timestamp][start_tile[0]][start_tile[1]] = INITIAL_TILES_DICT[agent_num + 2]
                marked_map_times[timestamp][end_tile[0]][end_tile[1]] = INITIAL_TILES_DICT[agent_num + 2]

            marked_map_times[timestamp][tile[0]][tile[1]] = PATH_TILES_DICT[agent_num + 2]
    return marked_map_times

def visualize_paths(my_map, paths):
    my_map_with_paths = mark_paths(map_to_tile(my_map), paths)
    map_str = [map_to_string(single_map) for single_map in my_map_with_paths]
    return map_str