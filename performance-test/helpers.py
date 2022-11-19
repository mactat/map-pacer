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
        
        print('"{}" took {:.3f} ms to execute'.format(my_func.__name__, (tend - tstart) * 1000))
        return output
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
    def __init__(self, backend_url) -> None:
        self.backend = f"http://{backend_url}/backend"

    def get_info(self):
        raw_info = requests.get(f"{self.backend}/get-info")
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
        paths = requests.get(f"{self.backend}/get_paths")
        return paths.json()

    def extract_paths_details(self, paths):
        paths_found = [path for path in paths.values() if path != "not found"]
        len_path_sum = sum([len(path) for path in paths_found])
        print(f"Paths found: {len(paths_found)}")
        print(f"% of paths found: {len(paths_found)/len(paths)*100}%")
        print(f"Sum of paths length: {len_path_sum}")


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
        requests.get(f"{self.backend}/sequence_calculate")
        return None

    def trigger_ca_star_cloud(self):
        requests.get(f"{self.backend}/sequence_calculate_cloud")
        return None
    
    def load_map(self, map_name):
        requests.get(f"{self.backend}/clear_paths")
        with open(f"./maps/{map_name}.json") as map_file:
            new_map = json.load(map_file)
            print(f"Map name: {map_name}, Map size: {len(new_map)}")
            requests.post(
                f"{self.backend}/adopt_map",
                data=json.dumps(new_map),
                headers={"Content-Type": "application/json"})
        
        # TODO: Test if map is the same 
        time.sleep(2)