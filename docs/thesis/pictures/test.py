import os
from backend_api import System
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--system_id', type=str, required=True)
parser.add_argument('--json', action='store_true')
args = parser.parse_args()
BACKEND_URL = os.environ.get('BACKEND_URL')

def maybe_print(string):
    if not args.json: print(string)

maybe_print("================== Test Setup ==================")
system = System(
    backend_url=BACKEND_URL,
    system=args.system_id,
    json_output=args.json)
maps = ["5","7","9","11","13","15","17","19"]
algorithms = ["a_star", "a_star_cloud", "ca_star", "ca_star_cloud"]


maybe_print("================== Test Suite ==================")
results = {}
for algorithm in algorithms:
    results[algorithm] = []
    for map_name in maps:
        single_results = system.test_algorithm(map_name, algorithm)
        results[algorithm].append(single_results)

maybe_print("================== Total results ==================")
for algo, result in results.items():
    system.extract_averages(result, algo)
system.finish_test()
maybe_print("================== Test End ==================")
