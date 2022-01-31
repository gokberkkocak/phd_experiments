import pandas as pd
import sys
import numpy as np
import json

# all_edit_no_sol_instances_removed.csv
df = pd.read_csv("all_edit_no_sol_instances_removed.csv", index_col=0)

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
    map[i]["times"] = []
    for index, j in enumerate(df[i]):
        if np.isnan(j):
            map[i]["times"].append(216000)
        else:
            map[i]["times"].append(int(j*10))

total_set = set(range(238))



print("letting configs be function")
print("(")
for v in map:
    print("{} --> sequence {},".format(map[v]["id"], map[v]["times"]).replace("[","(").replace("]",")"))
print(")")

print("letting total_set be {}".format(total_set))
