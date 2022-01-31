import pandas as pd
import sys
import numpy as np
import json

# all_edit_comp_25_10secs_removed_0_no_sol
df = pd.read_csv(sys.argv[1], index_col=0)

best_configs = [
    "GAC_exp_occ_cadical_11000001",
    "GAC_exp_occ_nbc_11000001",
    "GAC_occ_occ_cadical_11000001",
    "GAC_occ_occ_glucose_11000001",
    "GAC_occ_occ_nbc_11000001",
    "None_exp_occ_glucose_11000001",
    "None_exp_occ_nbc_11000001",
    "None_occ_occ_cadical_11000001",
    "None_occ_occ_glucose_11000001",
    "None_occ_occ_nbc_11000001",
    "SACBounds_limit_exp_occ_glucose_11000001",
    "SACBounds_limit_exp_occ_glucose_11100101",
    "SACBounds_limit_exp_occ_nbc_11000001",
    "SACBounds_limit_exp_occ_nbc_11100001",
    "SACBounds_limit_occ_occ_cadical_11000001",
    "SACBounds_limit_occ_occ_glucose_11000001",
    "SACBounds_limit_occ_occ_glucose_11100001",
    "SACBounds_limit_occ_occ_glucose_11100101",
    "SACBounds_limit_occ_occ_lia_yices2_11000001",
    "SACBounds_limit_occ_occ_nbc_11000001",
    "SACBounds_limit_occ_occ_nbc_11100001",
    "SSACBounds_limit_exp_occ_nbc_11000001",
    "SSACBounds_limit_occ_occ_cadical_11000001",
    "SSACBounds_limit_occ_occ_nbc_11000001",
    "None_exp_occ_cadical_11000001",
    "SACBounds_limit_exp_occ_glucose_11100001",
    "SSACBounds_limit_occ_occ_glucose_11000001",
    "SSACBounds_limit_occ_occ_lia_yices2_11000001",
    "SSACBounds_limit_exp_occ_glucose_11000001"]

df = df[best_configs]

# print (df)

map = dict()

for idx, i in enumerate(df):
    map[i] = dict()
    map[i]["id"] = idx
    map[i]["set"] = []
    for index, j in enumerate(df[i]):
        if j == 1:
            map[i]["set"].append(index)

with open(sys.argv[1].split(".")[0]+".json", 'w') as f:
    json.dump(map, f)

total_set = set(range(238))

elements_set = set()

for i in map:
    for el in map[i]:
        elements_set.add(el)

# print(total_set)
# print(elements_set)
# print(total_set == elements_set)

print("letting configs be function")
print("(")
for v in map:
    print("{} --> {},".format(map[v]["id"], set(map[v]["set"])))
print(")")

print("letting total_set be {}".format(total_set))
