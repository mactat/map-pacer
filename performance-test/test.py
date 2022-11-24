import os
from backend_api import System, call_counter

BACKEND_URL = os.environ.get('BACKEND_URL')


@call_counter
def test_ca_star_local(map_name):
    system.load_map(map_name)
    system.trigger_ca_star_local()
    paths = system.wait_for_paths()
    system.extract_paths_details(paths)


@call_counter
def test_ca_star_cloud(map_name):
    system.load_map(map_name)
    system.trigger_ca_star_cloud()
    paths = system.wait_for_paths()
    system.extract_paths_details(paths)


print("================== Test Setup ==================")
system = System(BACKEND_URL)
maps = ["small", "small_2", "two_traped", "spider", "big_and_empty"]

print(f"Number of agents {len(system.get_agents())}")
print(f"Leader: {system.get_leader()}")

print("================== Test Suite ==================")
for map_name in maps:
    test_ca_star_local(map_name)
    test_ca_star_cloud(map_name)

print("================== Test End ==================")
