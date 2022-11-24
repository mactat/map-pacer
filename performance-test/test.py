import os
from backend_api import System, call_counter

BACKEND_URL = os.environ.get('BACKEND_URL')


@call_counter
def test_ca_star_local(map_name):
    system.load_map(map_name)
    system.trigger_ca_star_local()
    paths, time = system.wait_for_paths()
    system.extract_paths_details(paths)
    return time, *system.extract_paths_details(paths)


@call_counter
def test_ca_star_cloud(map_name):
    system.load_map(map_name)
    system.trigger_ca_star_cloud()
    paths, time = system.wait_for_paths()
    return time, *system.extract_paths_details(paths)


print("================== Test Setup ==================")
system = System(BACKEND_URL)
maps = ["small", "small_2", "two_traped", "spider", "big_and_empty"]

print(f"Number of agents {len(system.get_agents())}")
print(f"Leader: {system.get_leader()}")

print("================== Test Suite ==================")
ca_star_res, ca_star_cloud_res = [], []
for map_name in maps:
    ca_star_res.append(test_ca_star_local(map_name))
    ca_star_cloud_res.append(test_ca_star_cloud(map_name))

print("================== Total results ==================")
system.extract_averages(ca_star_res, "CA* local")
system.extract_averages(ca_star_cloud_res, "CA* cloud")

print("================== Test End ==================")
