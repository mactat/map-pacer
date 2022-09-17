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
    def __init__(self, x, y):
        self.x = x
        self.y = y
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
    def __init__(self,agent_num=None, mode="no_diag"):
        self.grid = []
        self.frontier = []
        self.x_limit = 0
        self.y_limit = 0
        # random till 6
        if not agent_num: self.agent_num = np.random.randint(0, 6)
        else: self.agent_num = agent_num
        self.agent_color = PATH_TILES_DICT[self.agent_num]
        self.neighbors_coord = [(-1, 0), (0, -1), (0, 1), (1, 0)]
        if mode == "diag":
            self.neighbors_coord += [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    def load_from_list(self, grid_map_list):
        self.x_limit, self.y_limit = np.shape(grid_map_list)
        self.grid = np.zeros((self.x_limit, self.y_limit), dtype=object)
        for row_num, row in enumerate(grid_map_list):
            for column_num, cell in enumerate(row):
                if cell == 1:
                    self.grid[row_num][column_num] = Obstacle()
                else:
                    self.grid[row_num][column_num] = Cell(row_num, column_num)

        # find neighbours
        for row in self.grid:
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
        neighbors = []
        for n in self.neighbors_coord:
            x = current_x + n[0]
            y = current_y + n[1]
            if 0 <= x < self.x_limit and 0 <= y < self.y_limit and isinstance(self.grid[x][y], Cell):
                neighbors.append((x, y))
        return neighbors

    def reset_state(self):
        for row in self.grid:
            for cell in row:
                if isinstance(cell, Cell):
                    cell.parents = []
                    cell.visited = False
                    cell.g = float("inf")

    def path_on_map(self, path):
        final_str = "⬛"*(self.y_limit+2)+"\n"
        for i, row in enumerate(self.grid):
            final_str += "⬛"
            for j, cell in enumerate(row):
                if (i, j) in path:
                    final_str += self.agent_color
                else:
                    final_str += f"{str(cell)}"
            final_str += "⬛\n"
        final_str += "⬛"*(self.y_limit+2)
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
        starting_cell = self.grid[start[0]][start[1]]
        heuristic_func = self.get_heuristic(end, heuristic="euclidean")
        starting_cell.visited = True
        starting_cell.g = 0

        starting_cell.h = heuristic_func(starting_cell.x, starting_cell.y)
        starting_cell.f = starting_cell.g + starting_cell.h
        frontier.append(starting_cell)
        while frontier:
            # priority queue based on f value
            frontier.sort(key=lambda x: x.f)
            current = frontier.pop(0)
            for (x, y) in current.neighbors:
                if self.grid[x][y].visited:
                    continue
                frontier.append(self.grid[x][y])
                self.grid[x][y].visited = True
                self.grid[x][y].parents.append((current.x, current.y))
                self.grid[x][y].parents += current.parents
                self.grid[x][y].g = current.g + 1
                self.grid[x][y].h = heuristic_func(x, y)
                self.grid[x][y].f = self.grid[x][y].g + self.grid[x][y].h

                if (x, y) == end:
                    return True, self.grid[x][y].parents + [(x, y)]
        return False, None

if __name__ == "__main__":
    simple_map = np.array([
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

    ])

    grid_map = Grid_map(mode="no_diag")
    grid_map.load_from_list(simple_map)
    print(grid_map)
    start = (7, 0)
    end = (7, 19)

    print("BFS")
    possible, path = grid_map.BFS(start, end)
    print(grid_map.path_on_map(path))

    print("Dijkstra")
    possible, path = grid_map.dijkstra(start, end)
    print(grid_map.path_on_map(path))

    print("A*")
    possible, path = grid_map.a_star(start, end)
    print(grid_map.path_on_map(path))
