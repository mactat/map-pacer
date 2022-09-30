import numpy as np
import time,os

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
    def __init__(self,agent_num=None, mode="no_diag",head_collision_allowed=False, time_limit=100):
        self.grid = []
        self.frontier = []
        self.x_limit = 0
        self.y_limit = 0
        self.time_limit = time_limit
        self.head_collision_allowed = head_collision_allowed
        # random till 6
        if agent_num==None: self.agent_num = np.random.randint(0, 6)
        else: self.agent_num = agent_num
        self.agent_color = PATH_TILES_DICT[self.agent_num]
        self.longest_path = None
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

        self.reset_state(reset_graph=True)

    def mark_path_on_grid(self, path):
        end = path[-1]
        goal_timestamp = len(path)
        if not self.head_collision_allowed: self.avoid_head_collision(path)
        self.remove_from_neighbors(path + self.get_goal_as_path(end, goal_timestamp))
        self.mark_path_as_obstacle(path)
        self.mark_goal_as_obstacle(end, goal_timestamp)


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

    def reset_state(self,reset_graph=True):
        for timeframe in self.grid:
            for row in timeframe:
                for cell in row:
                    if not isinstance(cell, Cell): continue
                    cell.parents = []
                    cell.visited = False
                    if reset_graph: cell.neighbors = self.get_neighbors(cell)
                    cell.g = float("inf")

    def remove_from_neighbors(self, points):
        for timeframe in self.grid:
            for row in timeframe:
                for cell in row:
                    if not isinstance(cell, Cell): continue
                    cell.parents = []
                    cell.visited = False
                    for point in points:
                        if point in cell.neighbors:
                            cell.neighbors.remove(point)
                    cell.g = float("inf")

    def avoid_head_collision(self, path):
        prev_point = None
        for point in path:
            if prev_point == None:
                prev_point = point
                continue

            # Why is that needed??? Shouldn't the next point be an free cell anyway?
            if isinstance(self.grid[prev_point[2]][point[0]][point[1]], Obstacle): 
                prev_point = point
                continue
            if (prev_point[0], prev_point[1], point[2]) not in self.grid[prev_point[2]][point[0]][point[1]].neighbors: 
                prev_point = point
                continue
            # Remove head path in opposite direction than move to avoid head collision
            self.grid[prev_point[2]][point[0]][point[1]].neighbors.remove((prev_point[0], prev_point[1], point[2]))

            prev_point = point
    def mark_path_as_obstacle(self, path):
        for point in path: self.grid[point[2]][point[0]][point[1]] = Obstacle(vis=self.agent_color)

    def print_single_grid(self, grid):
        final_str = "⬛"*(self.y_limit+2)+"\n"
        for row in grid:
            final_str += "⬛"
            for cell in row:
                final_str += f"{str(cell)}"
            final_str += "⬛\n"
        final_str += "⬛"*(self.y_limit+2)
        return final_str

    def print_timegrid(self, speed=1, clear=True):
        if self.longest_path == None: return "No path found"
        for i in range(self.longest_path):
            if clear: os.system('cls' if os.name == 'nt' else 'clear')
            print(f"Timeframe {i}")
            print(self.print_single_grid(self.grid[i]))
            time.sleep(1/speed)

    def mark_goal_as_obstacle(self, goal, timeframe_num):
        for time in range(timeframe_num, self.time_limit):
            self.grid[time][goal[0]][goal[1]] = Obstacle(vis=self.agent_color)

    def get_goal_as_path(self, goal, timeframe_num):
        path = [(goal[0], goal[1], time) for time in range(timeframe_num, self.time_limit)]
        return path

    def find_path(self, start, end, algo="a_star"):
        if algo == "a_star":
            return self.a_star(start, end)
        else:
            raise ValueError("Invalid algo")


    def get_heuristic(self, point, heuristic="manhattan"):
        if heuristic == "manhattan":
            return lambda x, y: abs(x - point[0]) + abs(y - point[1])
        elif heuristic == "euclidean":
            return lambda x, y: np.sqrt((x - point[0])**2 + (y - point[1])**2)
        else:
            raise ValueError("Heuristic not implemented")

    def a_star(self, start, end):
        frontier = []
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
                if (isinstance(self.grid[z][x][y], Obstacle)): raise ValueError(f"Obstacle in the neibours! current: {current.x} {current.y} {current.z} neibour: {x} {y} {z}")
                frontier.append(self.grid[z][x][y])
                self.grid[z][x][y].visited = True
                self.grid[z][x][y].parents.append((current.x, current.y, current.z))
                self.grid[z][x][y].parents += current.parents
                self.grid[z][x][y].g = current.g + 1
                self.grid[z][x][y].h = heuristic_func(x, y)
                self.grid[z][x][y].f = self.grid[z][x][y].g + self.grid[z][x][y].h

                if (x, y) == end:
                    path = [(x, y, z)] + self.grid[z][x][y].parents
                    # reverse path
                    path = path[::-1]
                    self.mark_path_on_grid(path)
                    if self.longest_path == None or len(path) > self.longest_path:
                        self.longest_path = len(path)
                    return True, path
        self.reset_state(reset_graph=False)
        return False, None