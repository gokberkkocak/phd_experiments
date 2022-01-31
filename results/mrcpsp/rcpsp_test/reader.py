#!/usr/bin/env python3
import os
import json
import numpy as np

result_db = dict()
for f in os.listdir("info_files"):
    instance = f.split("_")[0] + "_" + f.split("_")[1]
    config = "_".join(f.split(".")[0].split("_")[2:-2])
    with open(os.path.join("info_files", f)) as info_file:
        lines =info_file.readlines()
    for line in lines:
        if "TOTAL TIME" in line:
            total_time = float(line.split("TOTAL TIME: ")[1].strip())
        if "SolverTotalTime" in line:
            solver_time = float(line.split("SolverTotalTime:")[1].strip())

    if  instance not in result_db:
        result_db[instance] = dict()
    if  config not in result_db[instance]:
        result_db[instance][config] = dict()
    
    if "solver_time" not in result_db[instance][config]:
        result_db[instance][config]["total_time"] = []
        result_db[instance][config]["solver_time"] = []
    result_db[instance][config]["total_time"].append(total_time)
    result_db[instance][config]["solver_time"].append(solver_time)

for instance in result_db:
    for config in result_db[instance]:
        result_db[instance][config]["total_time"] = np.mean(result_db[instance][config]["total_time"])
        result_db[instance][config]["solver_time"] = np.mean(result_db[instance][config]["solver_time"])

with open("results.json", "w") as json_file:
    json.dump(result_db, json_file, indent=1)