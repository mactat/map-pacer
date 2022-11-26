import os
from backend_api import System
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--system_id', type=str, required=True)
args = parser.parse_args()
BACKEND_URL = os.environ.get('BACKEND_URL')


print("================== Test Setup ==================")
system = System(BACKEND_URL, args.system_id)
maps = ["small", "small_2", "two_traped", "spider", "big_and_empty"]
algorithms = ["a_star", "a_star_cloud", "ca_star", "ca_star_cloud"]

print(f"Number of agents {len(system.get_agents())}")
print(f"Leader: {system.get_leader()}")

print("================== Test Suite ==================")
results = {}
for algorithm in algorithms:
    results[algorithm] = []
    for map_name in maps:
        single_results = system.test_algorithm(map_name, algorithm)
        results[algorithm].append(single_results)

print("================== Total results ==================")
for algo, result in results.items():
    system.extract_averages(result, algo)

print("================== Test End ==================")
