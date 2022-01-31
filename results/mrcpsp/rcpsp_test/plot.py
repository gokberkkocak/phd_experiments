#!/usr/bin/env python3
import json
import sys
import matplotlib.pyplot as plt
import numpy as np

TYPE = "solver_time"

with open("results_native.json", "r") as json_file:
    results = json.load(json_file)

scatter = []
for instance in results:
    row = []
    row.append(instance)
    row.append(results[instance]["normal_bisect_glucose"][TYPE]) # 1 
    row.append(results[instance]["normal_linear_glucose"][TYPE]) # 2
    row.append(results[instance]["normal_unsat_glucose"][TYPE]) # 3 
    row.append(results[instance]["inter_bisect_glucose"][TYPE]) # 4
    row.append(results[instance]["inter_linear_glucose"][TYPE]) # 5 
    row.append(results[instance]["inter_unsat_glucose"][TYPE]) # 6 
    row.append(results[instance]["openwbo_glucose"][TYPE]) # 7
    row.append(results[instance]["chuffed"][TYPE]) # 8 
    scatter.append(row)

SORT_KEY = 6

scatter = sorted(scatter, key=lambda x: x[SORT_KEY])

fig, ax = plt.subplots(figsize=(10,4))

r1 = np.arange(len(scatter))

colors = ["blue", "green", "black", "orange", "magenta", "cyan", "red", "lime"]
names = ["normal_bisect_glucose", "normal_linear_glucose", "normal_unsat_glucose", "inter_bisect_glucose", "inter_linear_glucose", "inter_unsat_glucose", "openwbo_glucose", "chuffed"]

for i in range(1,9):
    plt.scatter(r1, [row[i] for row in scatter],60, label=names[i-1], marker=".", color=colors[i-1] ,alpha=0.8, edgecolors ="none")

plt.title(TYPE)
plt.ylabel("time in secs")
plt.xlabel("Instances")
plt.yscale('log')
plt.xticks([])
plt.legend()
plt.tight_layout()
plt.savefig("results.pdf", format="pdf")
