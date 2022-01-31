#!/usr/bin/env python3
import json
import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

TYPE = "solver_time"

with open("results_native.json", "r") as json_file:
    results = json.load(json_file)

scatter = []
for instance in results:
    try:
        row = []
        row.append(instance)
        row.append(results[instance]["normal_bisect_yices"][TYPE]) # 1 
        row.append(results[instance]["normal_linear_yices"][TYPE]) # 2
        row.append(results[instance]["normal_unsat_yices"][TYPE]) # 3 
        row.append(results[instance]["inter_bisect_yices"][TYPE]) # 4
        row.append(results[instance]["inter_linear_yices"][TYPE]) # 5 
        row.append(results[instance]["inter_unsat_yices"][TYPE]) # 6 
        row.append(results[instance]["z3"][TYPE]) # 7
        row.append(results[instance]["chuffed"][TYPE]) # 8 
        scatter.append(row)
    except:
        print("s")

SORT_KEY = 6

scatter = sorted(scatter, key=lambda x: x[SORT_KEY])

labels = ['yices-bisect','yices-linear','yices-UNSAT']
plotFormat = ['pdf','png'][0]
for i in range(1,4):
    fig, ax = plt.subplots(figsize=(3.5,3.5))
    plt.scatter([row[i] for row in scatter], [row[i+3] for row in scatter], 70, marker=".", color='blue', alpha=0.6, edgecolors='none')
    plt.plot(range(0,150), range(0,150), color='red')
    plt.title(labels[i-1])
    plt.xlim([0.2, 150])
    plt.ylim([0.2, 150])   
    plt.ylabel("With native interaction",fontsize=12)
    plt.xlabel("Without native interaction",fontsize=12)
    plt.yscale('log')
    plt.xscale('log')
    ticks = [0.2,1,10,40,150]
    plt.xticks(ticks)
    plt.yticks(ticks)
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    plt.minorticks_off()
    plt.tight_layout()
    plt.savefig(labels[i-1]+'.' + plotFormat, format=plotFormat)

