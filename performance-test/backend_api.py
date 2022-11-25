import requests
import time
from functools import wraps
import json

def timeit(my_func):
    @wraps(my_func)
    def timed(*args, **kw):
    
        tstart = time.time()
        output = my_func(*args, **kw)
        tend = time.time()
        diff = (tend - tstart)* 1000
        print('"{}" took {:.3f} ms to execute'.format(my_func.__name__, diff))
        return output, diff
    return timed

def call_counter(my_func):
    def helper(*args, **kwargs):
        helper.calls += 1
        print(f"\n========> Test {my_func.__name__}")
        print(f"Test number: {helper.calls}")
        return my_func(*args, **kwargs)
    helper.calls = 0
    return helper

class System:
    def __init__(self, backend_url, system="home_system") -> None:
        self.system = system
        self.backend = f"http://{backend_url}/backend"

    def get_info(self):
        raw_info = requests.get(f"{self.backend}/get-info?system_id={self.system}")
        return raw_info.json()

    def get_agents(self):
        agents = self.get_info()["agents"]
        return agents

    def get_leader(self):
        leader = self.get_info()["leader"]
        return leader

    def get_map(self):
        cur_map = self.get_info()["map"]
        return cur_map

    def get_paths(self):
        paths = requests.get(f"{self.backend}/get_paths?system_id={self.system}")
        return paths.json()

    def find_steps_from_paths(self, path):
        num_of_steps = len(path) + 1
        for step in path[::-1]:
            if step == path[-1]:
                num_of_steps -= 1
            else: break
        return num_of_steps

    def extract_paths_details(self, paths):
        paths_found = [path for path in paths.values() if path != "not found"]
        len_path_sum = sum([self.find_steps_from_paths(path) for path in paths_found])
        num_of_found_paths=len(paths_found)
        percentage_of_path_found=num_of_found_paths/len(paths)*100
        print(f"Paths found: {num_of_found_paths}")
        print(f"% of paths found: {percentage_of_path_found}%")
        print(f"Sum of paths length: {len_path_sum}")
        return num_of_found_paths, percentage_of_path_found, len_path_sum



    @timeit
    def wait_for_paths(self):
        agents = self.get_agents()
        paths = self.get_paths()
        while not all(agent in paths for agent in agents):
            time.sleep(0.1)
            paths = self.get_paths()

        print("Calculation completed")
        return paths
    
    def trigger_ca_star_local(self):
        requests.get(f"{self.backend}/sequence_calculate?system_id={self.system}")
        return None

    def trigger_ca_star_cloud(self):
        requests.get(f"{self.backend}/sequence_calculate_cloud?system_id={self.system}")
        return None

    def replace_agents(self, cur_map):
        agents = self.get_agents()
        for agent_old, agent_new in zip(["agent-1", "agent-0", "agent-2"], agents):
            for i, row in enumerate(cur_map):
                for j, cell in enumerate(row):
                    if cell == f"{agent_old}-start": 
                            cur_map[i][j] = f"{agent_new}-start"
                    elif cell == f"{agent_old}-end":
                            cur_map[i][j] = f"{agent_new}-end"
        return cur_map


    def load_map(self, map_name):
        requests.get(f"{self.backend}/clear_paths?system_id={self.system}")
        time.sleep(1)
        with open(f"./maps/{map_name}.json") as map_file:
            raw_map = json.load(map_file)
            new_map = self.replace_agents(raw_map)
            print(f"Map name: {map_name}, Map size: {len(new_map)}")
            requests.post(
                f"{self.backend}/adopt_map?system_id={self.system}",
                data=json.dumps(new_map),
                headers={"Content-Type": "application/json"})
        
        # TODO: Test if map is the same 
        time.sleep(2)
    def extract_averages(self, results, name):
        transpose = list(zip(*results))
        print(f"""\n-------> Algorithm: {name} <-------
        Average time: {sum(transpose[0])/len(transpose[0]):.{1}f}ms
        Average number of paths found: {sum(transpose[1])/len(transpose[1]):.{1}f}
        Average percentage of paths found: {sum(transpose[2])/len(transpose[2]):.{1}f}%
        Average path length: {sum(transpose[3])/len(transpose[3]):.{1}f} tiles
        """)