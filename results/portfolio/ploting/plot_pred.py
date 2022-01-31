import json
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import matplotlib
import numpy as np
from scipy import stats
import scipy as sp
import scipy.interpolate
import math

json_file = sys.argv[1]
save = True


with open(json_file, "r") as jf:
    json_file = json.load(jf)

# 25 50 66 100 150 for 6
tree = []
for t in range(5):
    temp_t = []
    for s in range(6):
        temp_s = []
        for _ in range(2):
            temp_s.append(0)
        temp_t.append(temp_s)
    tree.append(temp_t)

v_best = []
for t in range(5):
    temp_t = []
    for s in range(6):
        temp_t.append(0)
    v_best.append(temp_t)

sbs = []
for t in range(5):
    temp_t = []
    for s in range(6):
        temp_t.append(0)
    sbs.append(temp_t)


def get_index(i):
    i = int(i)
    if i == 25:
        return 0
    elif i == 50:
        return 1
    elif i == 66:
        return 2
    elif i == 100:
        return 3
    else:
        return 4

# print(tree)


for i in json_file:
    # print(i)
    # print(get_index(i["threshold"]))
    if i["system"] == "finalf":
        tree[get_index(i["threshold"])][int(i["split"])][int(i["rnd"])] = float(i["time"])
    elif i["system"] == "vbest":
        v_best[get_index(i["threshold"])][int(i["split"])] = float(i["time"])
    elif i["system"] == "sbs":
        sbs[get_index(i["threshold"])][int(i["split"])] = float(i["time"])


print("--------")
print(tree)
print("--------")
print(v_best)
print("-------")
print(sbs)
print("-------")

# tree avg and std
time_tree = []
for t in range(5):
    temp_t = []
    for s in range(6):
        temp_t.append(0)
    time_tree.append(temp_t)
std_tree = []
for t in range(5):
    temp_t = []
    for s in range(6):
        temp_t.append(0)
    std_tree.append(temp_t)


for t in range(len(tree)):
    for s in range(len(tree[0])):
        time_tree[t][s] = np.average(tree[t][s])
        std_tree[t][s] = stats.sem(tree[t][s])

print(time_tree)
print(std_tree)

# print(scatter_sol_sorted)
fig, ax = plt.subplots(figsize=(4, 4))
# fig, ax = plt.subplots(figsize=(12,6))
r1 = np.arange(len(tree[0]))
r2 = np.arange(10800)
matplotlib.rc('legend', fontsize=8)

t = sys.argv[2]
i = get_index(int(t))
# print(i)
plt.errorbar(r1, time_tree[i], yerr=std_tree[i], label="pred",
                fmt='x', marker="o", color="blue", alpha=0.5, )
plt.scatter(r1, v_best[i],  label="vbest", marker="o",
            color="green", alpha=0.5, edgecolors="none")
plt.scatter(r1, sbs[i],  label="sbs", marker="o",
            color="red", alpha=0.5, edgecolors="none")

plt.xlabel("Splits")
plt.ylabel("Total runtime in s")
plt.xticks([])
plt.title("Predictions in +{}%".format(t))

# ax.set_aspect(1.0/ax.get_data_ratio()*0.5)
plt.tight_layout()
# Create legend & Show graphic
plt.legend()
save = True
if save:
    plt.savefig(sys.argv[1].split(".")[0]+"-"+str(t)+".pdf", format="pdf")
else:
    plt.show()
