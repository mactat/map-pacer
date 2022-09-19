import numpy as np

PATH_TILES_DICT = {
    0: "🟥",
    1: "🟦",
    2: "🟩",
    3: "🟨",
    4: "🟧",
    5: "🟪",
    6: "🟫"
}

class Obstacle:
    def __init__(self, vis="⬛"):
        self.vis = vis

    def __repr__(self):
        return self.vis

    def __str__(self):
        return self.vis


class Cell:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.g = 0
        self.h = 0
        self.f = 0
        self.visited = False
        self.parents = []
        self.neighbors = []

    def __repr__(self):
        return "⬜"

    def __str__(self):
        return "⬜"


class Grid_map:
    def __init__(self,agent_num=None, mode="no_diag", time_limit=100):
        self.grid = []
        self.frontier = []
        self.x_limit = 0
        self.y_limit = 0
        self.time_limit = time_limit
        # random till 6
        if agent_num==None: self.agent_num = np.random.randint(0, 6)
        else: self.agent_num = agent_num
        self.agent_color = PATH_TILES_DICT[self.agent_num]
        self.neighbors_coord = [(-1, 0, 1), (0, -1, 1), (0, 1, 1), (1, 0, 1), (0, 0, 1)] # x,y,z
        if mode == "diag":
            self.neighbors_coord += [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    def load_from_list(self, grid_map_list):
        self.x_limit, self.y_limit = np.shape(grid_map_list)
        self.grid = np.zeros((self.time_limit, self.x_limit, self.y_limit), dtype=object)
        for timeframe in range(self.time_limit):
            for row_num, row in enumerate(grid_map_list):
                for column_num, cell in enumerate(row):
                    if cell == 1:
                        self.grid[timeframe][row_num][column_num] = Obstacle()
                    else:
                        self.grid[timeframe][row_num][column_num] = Cell(row_num, column_num, timeframe)

        # find neighbours
        for timeframe in self.grid:
            for row in timeframe:
                for cell in row:
                    if isinstance(cell, Cell):
                        cell.neighbors = self.get_neighbors(cell)

    def __repr__(self):
        final_str = " - "*(self.y_limit+1)+"\n"
        for row in self.grid:
            final_str += "|"
            for cell in row:
                final_str += f" {str(cell)} "
            final_str += "|\n"
        final_str += " - "*(self.y_limit+1)
        return final_str

    def get_neighbors(self, cell):
        current_x = cell.x
        current_y = cell.y
        current_z = cell.z
        neighbors = []
        for n in self.neighbors_coord:
            x = current_x + n[0]
            y = current_y + n[1]
            z = current_z + n[2]
            if 0 <= x < self.x_limit and 0 <= y < self.y_limit and 0 <= z < self.time_limit and isinstance(self.grid[z][x][y], Cell):
                neighbors.append((x, y, z))
        return neighbors

    def reset_state(self):
        for timeframe in self.grid:
            for row in timeframe:
                for cell in row:
                    if isinstance(cell, Cell):
                        cell.parents = []
                        cell.visited = False
                        cell.g = float("inf")

    def mark_path_as_obstacle(self, path):
        for point in path: self.grid[point[2]][point[0]][point[1]] = Obstacle()
        for timeframe in self.grid:
            for row in timeframe:
                for cell in row:
                    if isinstance(cell, Cell):
                        cell.neighbors = self.get_neighbors(cell)
    
    def path_on_map(self, path):
        final_str = "⬛"*(self.y_limit+2)+"\n"
        for i, row in enumerate(self.grid[0]):
            final_str += "⬛"
            for j, cell in enumerate(row):
                if (i, j) in path:
                    final_str += self.agent_color
                else:
                    final_str += f"{str(cell)}"
            final_str += "⬛\n"
        final_str += "⬛"*(self.y_limit+2)
        return final_str

    def path_every_state_on_map(self, paths):
        final_str=""
        for (point1, point2) in zip(paths[0],paths[1]):
            final_str += "\n" + "⬛"*(self.y_limit+2)+"\n"
            for i, row in enumerate(self.grid[0]):
                final_str += "⬛"
                for j, cell in enumerate(row):
                    if (i, j) == point1:
                        final_str += PATH_TILES_DICT[1]
                    elif (i, j) == point2:
                        final_str += PATH_TILES_DICT[2]
                    else:
                        final_str += f"{str(cell)}"
                final_str += "⬛\n"
            final_str += "⬛"*(self.y_limit+2) +"\n"
        return final_str

    def find_path(self, start, end, algo="a_star"):
        if algo == "BFS":
            return self.BFS(start, end)
        elif algo == "dijkstra":
            return self.dijkstra(start, end)
        elif algo == "a_star":
            return self.a_star(start, end)
        else:
            raise ValueError("Invalid algo")
    def BFS(self, start, end):
        frontier = []
        starting_cell = self.grid[start[0]][start[1]]
        self.reset_state()
        starting_cell.visited = True
        frontier.append(starting_cell)
        while frontier:
            # Just pop from FIFO queue
            current = frontier.pop(0)
            for (x, y) in current.neighbors:
                if self.grid[x][y].visited:
                    continue
                frontier.append(self.grid[x][y])
                self.grid[x][y].visited = True
                self.grid[x][y].parents.append((current.x, current.y))
                self.grid[x][y].parents += current.parents

                if (x, y) == end:
                    return True, self.grid[x][y].parents + [(x, y)]
        return False, None

    def dijkstra(self, start, end):
        frontier = []
        starting_cell = self.grid[start[0]][start[1]]
        self.reset_state()
        starting_cell.visited = True
        starting_cell.g = 0
        frontier.append(starting_cell)
        while frontier:
            # priority queue based on g value
            frontier.sort(key=lambda x: x.g)
            current = frontier.pop(0)
            for (x, y) in current.neighbors:
                if self.grid[x][y].visited:
                    continue
                frontier.append(self.grid[x][y])
                self.grid[x][y].visited = True
                self.grid[x][y].parents.append((current.x, current.y))
                self.grid[x][y].parents += current.parents
                self.grid[x][y].g = current.g + 1

                if (x, y) == end:
                    return True, self.grid[x][y].parents + [(x, y)]
        return False, None

    def get_heuristic(self, point, heuristic="manhattan"):
        if heuristic == "manhattan":
            return lambda x, y: abs(x - point[0]) + abs(y - point[1])
        elif heuristic == "euclidean":
            return lambda x, y: np.sqrt((x - point[0])**2 + (y - point[1])**2)
        else:
            raise ValueError("Heuristic not implemented")

    def a_star(self, start, end):
        frontier = []
        self.reset_state()
        starting_cell = self.grid[0][start[0]][start[1]]
        heuristic_func = self.get_heuristic((end[0], end[1]), heuristic="manhattan")
        starting_cell.visited = True
        starting_cell.g = 0

        starting_cell.h = heuristic_func(starting_cell.x, starting_cell.y)
        starting_cell.f = starting_cell.g + starting_cell.h
        frontier.append(starting_cell)
        while frontier:
            # priority queue based on f value
            frontier.sort(key=lambda x: x.f)
            current = frontier.pop(0)
            for (x, y, z) in current.neighbors:
                if self.grid[z][x][y].visited:
                    continue
                frontier.append(self.grid[z][x][y])
                self.grid[z][x][y].visited = True
                self.grid[z][x][y].parents.append((current.x, current.y, current.z))
                self.grid[z][x][y].parents += current.parents
                self.grid[z][x][y].g = current.g + 1
                self.grid[z][x][y].h = heuristic_func(x, y)
                self.grid[z][x][y].f = self.grid[z][x][y].g + self.grid[z][x][y].h

                if (x, y) == end:
                    return True, [(x, y, z)] + self.grid[z][x][y].parents
        return False, None

if __name__ == "__main__":
    simple_map = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ])

    grid_map = Grid_map(mode="no_diag")
    grid_map.load_from_list(simple_map)
    # print(grid_map)
    start = (2, 0) 
    end = (2, 4) 

    # print("BFS")
    # possible, path = grid_map.BFS(start, end)
    # print(grid_map.path_on_map(path))

    # print("Dijkstra")
    # possible, path = grid_map.dijkstra(start, end)
    # print(grid_map.path_on_map(path))

    print("A* agent 1")
    possible_1, path_1 = grid_map.a_star(start, end)
    print(path_1)
    path_2d_1 = list(reversed([(x, y) for (x, y, z) in path_1]))

    start = (0, 2) 
    end = (4, 2) 

    print("A* agent 2")
    grid_map.mark_path_as_obstacle(path_1)
    possible_2, path_2 = grid_map.a_star(start, end)
    print(path_2)
    path_2d_2 = list(reversed([(x, y) for (x, y, z) in path_2]))
    diff = len(path_2) - len(path_1)
    print(diff)
    path_2d_1 += [path_2d_1[-1]]*diff
    print(path_2d_1)
    print(path_2d_2)

    print(grid_map.path_every_state_on_map([path_2d_1, path_2d_2]))
