import itertools
from pprint import pprint
import json

# Read the configuration in the JSON file
with open("rank_joule.json") as data_file:
    experiments_object = json.load(data_file)

STRESSES = ['../tuned_enemies/tuned_cache', '../tuned_enemies/tuned_bus', '../tuned_enemies/tuned_memory']
CORES = experiments_object["cache_rank"]["cores"]
# print(STRESSES)
# print(CORES)

ALL_COMBOS = [p for p in itertools.product(STRESSES, repeat=CORES)]

conf_mapping = dict()



result = []

for check in ALL_COMBOS:
    found_counter = False
    # print(check)

    str = "{1: '" + check[0] + "', 2: '" + check[1] + "', 3: '" + check[2] +"'}"

    bus_rank0 = [x[0] for x in experiments_object["bus_rank"]["ranked_list"]].index(str)
    cache_rank0 = [x[0] for x in experiments_object["cache_rank"]["ranked_list"]].index(str)
    memory_rank0 = [x[0] for x in experiments_object["mem_rank"]["ranked_list"]].index(str)
    # print(str)
    # print(bus_rank0, cache_rank0, memory_rank0)

    for check_prime in ALL_COMBOS:
        str2 = "{1: '" + check_prime[0] + "', 2: '" + check_prime[1] + "', 3: '" + check_prime[2] + "'}"
        bus_rank1 = [x[0] for x in experiments_object["bus_rank"]["ranked_list"]].index(str2)
        cache_rank1 = [x[0] for x in experiments_object["cache_rank"]["ranked_list"]].index(str2)
        memory_rank1 = [x[0] for x in experiments_object["mem_rank"]["ranked_list"]].index(str2)

        if bus_rank1 > bus_rank0 and cache_rank1 > cache_rank0 and memory_rank1 > memory_rank0:
            found_counter = True
            break

    if found_counter:
        continue

    result.append((check, cache_rank0, memory_rank0, bus_rank0))

pprint(result)
