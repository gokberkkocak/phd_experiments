#!/usr/bin/env python3
import json
import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

TYPE = "solver_time"
show = ['normal','inter'][0]

with open("results_native.json", "r") as json_file:
    results = json.load(json_file)

print(len(results.keys()))

scatter = []
for instance in results:
    row = []
    try:
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
        print("ski")

SORT_KEY = 6

scatter = sorted(scatter, key=lambda x: x[SORT_KEY])

fig, ax = plt.subplots(figsize=(8,4))

r1 = np.arange(len(scatter))

#colors = ["lime", "green", "black", "orange", "magenta", "cyan", "red", "blue"]
colors = ["orange", "magenta", "cyan",  "orange", "magenta", "cyan",  "red", "blue"]
names = ["normal_bisect_yices", "normal_linear_yices", "normal_unsat_yices", "inter_bisect_yices", "inter_linear_yices", "inter_unsat_yices", "z3", "chuffed"]
markers = ['o','v','+',    'o','v','+',     'x','*']

if show == 'inter':
    r = range(4,9)
else:
    r = list(range(1,4))
    r.extend(range(7,9))
for i in r:
    plt.scatter(r1, [row[i] for row in scatter],30, label=names[i-1], marker=markers[i-1], color=colors[i-1] ,alpha=0.5, edgecolors ="none")
    #plt.scatter(r1, [row[i] for row in scatter],50, label=names[i-1], marker=markers[i-1], color='blue', alpha=0.5, edgecolors ="none")


plt.title('')
plt.ylabel("Time (s)",fontsize=12)
plt.xlabel("Instances",fontsize=12)
plt.yscale('log')
plt.xticks([])
plt.yticks([0.2,1,10,50,150])
ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
plt.minorticks_off()

matplotlib.rcParams.update({'legend.fontsize':12,'legend.markerscale':1.5})
ax.legend(labels=['yices-bisect','yices-linear','yices-UNSAT','z3','Chuffed'], loc='center left',bbox_to_anchor=(1,0.5)) # for i in range(4,9) only

plt.tight_layout()
plotFormat = ['pdf','png'][0]
plt.savefig("results-" + show + '.' + plotFormat, format=plotFormat)
