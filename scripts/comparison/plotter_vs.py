import json
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import matplotlib
import numpy as np
from scipy import stats
import math



def process_solver(new_tree_str, exp, given_key):
    if (given_key in new_tree_str[exp]):
        sol = float(new_tree_str[exp][given_key]["solver_time_mean"])
        sol_err = float(new_tree_str[exp][given_key]["solver_time_mean_error"])
        sr = float(new_tree_str[exp][given_key]["sr_time_v_best"])
        sr_err = float(new_tree_str[exp][given_key]["sr_time_mean_error"])
        nb_sols = new_tree_str[exp][given_key]["sols"]
        nodes = new_tree_str[exp][given_key]["nodes"]
        satc = new_tree_str[exp][given_key]["satc"]
        satv = new_tree_str[exp][given_key]["satv"]
        file_size = new_tree_str[exp][given_key]["file_size"]
        ratio = np.divide(satc, satv)
    else:
        sol = 21600
        sol_err = np.nan
        sr = np.nan
        sr_err = np.nan
        nb_sols = np.nan
        nodes = np.nan
        file_size = np.nan
        ratio = np.nan
    if nb_sols == -1:
        sol = 21600
        sol_err = np.nan
        sr = np.nan
        sr_err = np.nan
        nb_sols = np.nan
        nodes = np.nan
        file_size = np.nan
        ratio = np.nan
    if np.isnan(sol):
        sol = 21600
    return (sol, sol_err, sr, sr_err, nb_sols, nodes, file_size, ratio)



json_file = sys.argv[1]
save=False
if len(sys.argv) > 4:
    if "save" in sys.argv[4]:
        save=True
        

with open(json_file, "r") as jf:
    new_tree_str = json.load(jf)

scatter = []

for exp in new_tree_str:
    if sys.argv[2] in exp and "minimal" not in exp:
        min_res = process_solver(new_tree_str, exp, "minion") # 1
        min_n_res = process_solver(new_tree_str, exp, "minion_noincomp") # 2
        nbc_res = process_solver(new_tree_str, exp, "nbc") # 3
        nbc_n_res = process_solver(new_tree_str, exp, "nbc_noincomp") # 4  
        glu_res = process_solver(new_tree_str, exp, "glucose") # 5
        glu_n_res = process_solver(new_tree_str, exp, "glucose_noincomp") # 6
        min_n_ord_red = process_solver(new_tree_str, exp, "minion_noincomp_ordered") # 7
        glu_n_ord_red = process_solver(new_tree_str, exp, "glucose_noincomp_ordered") # 8
        min_comp = process_solver(new_tree_str, exp, "minion_compressed") # 9 
        nbc_comp = process_solver(new_tree_str, exp, "nbc_compressed") # 10
        nbc_int_res = process_solver(new_tree_str, exp, "nbc_interactive") # 11
        glu_int_res = process_solver(new_tree_str, exp, "glucose_interactive") # 12
        glu_int_nb_res = process_solver(new_tree_str, exp, "glucose_interactive_noblock") # 13
        sol_sr = (exp, min_res, min_n_res, nbc_res, nbc_n_res, glu_res, glu_n_res, min_n_ord_red, glu_n_ord_red, min_comp, nbc_comp, nbc_int_res, glu_int_res, glu_int_nb_res)

        # sol = (exp, sat_sol, sat_n_sol, min_sol, min_n_sol, sat_sol_err, sat_n_sol_err, min_sol_err, min_n_sol_err, min_sols, min_n_sols, sat_sols, sat_n_sols)
        # sr = (exp, sat_sr, sat_n_sr, min_sr, min_n_sr, sat_sr_err, sat_n_sr_err, min_sr_err, min_n_sr_err, min_sols, min_n_sols, sat_sols, sat_n_sols)
        
        # print
        if (not np.isnan(nbc_comp[0]) and not np.isnan(nbc_res[0])):
            if nbc_comp[0] > nbc_res[0]:
                print("reform wins", nbc_comp[0], nbc_res[0])
            elif nbc_comp[0] < nbc_res[0]:
                print("nore wins", nbc_comp[0], nbc_res[0])


        have_something = False
        for i in range(1, len(sol_sr)):
            if (not np.isnan(sol_sr[i][0])):
                if sol_sr[i][0] < 21600 and sol_sr[i][0] > 0.001:
                    have_something = True
        if have_something:
            scatter.append(sol_sr)
        # scatter_sr.append(sr)

# print(scatter[1])

# scatter_sorted = sorted(scatter_sr, key=lambda x: x[1])

sort_key = 0
if len(sys.argv) > 5:
    if "sort" in sys.argv[5]:
        sort_key = 11

if sort_key == 0:
    scatter_sorted = sorted(scatter, key=lambda x: x[sort_key])
else:
    scatter_sorted = sorted(scatter, key=lambda x: float('inf') if math.isnan(x[sort_key][0]) else x[sort_key][0])


# print(scatter_sorted)

# print(scatter_sol_sorted)
# fig, ax = plt.subplots(figsize=(15,5))
# fig, ax = plt.subplots(figsize=(3,3))
fig, ax = plt.subplots(figsize=(5,5))
r1 = np.arange(len(scatter_sorted))
r2 = np.arange(10800)
matplotlib.rc('legend', fontsize=8)


# (sol, sol_err, sr, sr_err, nb_sols)
#  0    1       2       3       4

plot_v = sys.argv[3] 
if "nb" in plot_v:
    p = 4
elif "solver" in plot_v:
    p = 0
elif "total" in plot_v:
    p = 2 

x = int(sys.argv[6])
y = int(sys.argv[7])

if "cdp" in sys.argv[5]:
    plt.scatter([row[6][p] for row in scatter_sorted], [row[2][p] for row in scatter_sorted],60, label="CDP", marker="x", color="green",  alpha=0.5, edgecolors ="none")
    plt.scatter([row[3][p] for row in scatter_sorted], [row[1][p] for row in scatter_sorted],60, label="CDP+I", marker="+", color="purple",  alpha=0.5, edgecolors ="none")
elif 'comp' in sys.argv[5]:
    plt.scatter([row[9][p] for row in scatter_sorted], [row[1][p] for row in scatter_sorted],60, label="Minion", marker="x", color="blue",  alpha=0.5, edgecolors ="none")
    plt.scatter([row[10][p] for row in scatter_sorted], [row[3][p] for row in scatter_sorted],60, label="SAT", marker="+", color="red",  alpha=0.5, edgecolors ="none")
elif 'level' in sys.argv[5]:
    plt.scatter([row[2][p] for row in scatter_sorted], [row[7][p] for row in scatter_sorted],60, label="Minion", marker="x", color="blue",  alpha=0.5, edgecolors ="none")
    # plt.scatter([row[5][p] for row in scatter_sorted], [row[8][p] for row in scatter_sorted],60, label="SAT", marker="+", color="red",  alpha=0.5, edgecolors ="none")
elif "inter" in sys.argv[5]:
    # plt.scatter([row[12][p] for row in scatter_sorted], [row[2][p] for row in scatter_sorted],60, label="NBC/Gluc(i)", marker="+", color="purple",  alpha=0.5, edgecolors ="none")
    # plt.scatter([row[11][p] for row in scatter_sorted], [row[2][p] for row in scatter_sorted],60, label="NBC/NBC(i)", marker="x", color="green",  alpha=0.5, edgecolors ="none")
    plt.scatter([row[x][p] for row in scatter_sorted], [row[y][p] for row in scatter_sorted],60, label="Comparison", marker="x", color="red",  alpha=0.5, edgecolors ="none")
else:    
    plt.scatter([row[1][p] for row in scatter_sorted], [row[7][p] for row in scatter_sorted],60, label="Minion", marker="x", color="blue", alpha=0.5, edgecolors ="none")
    plt.scatter([row[3][p] for row in scatter_sorted], [row[6][p] for row in scatter_sorted],60, label="SAT", marker="+", color="red",  alpha=0.5, edgecolors ="none")



max_point = int( np.nanmax([row[12][p] if (np.isnan(row[7][p])) else 21600  for row in scatter_sorted] ))
# max_point = int( np.nanmax([row[6][p] if (np.isnan(row[7][p])) else np.NaN  for row in scatter_sorted] ))
# max_point = int( np.nanmax([row[6][p] if (np.isnan(row[7][p])) else np.NaN  for row in scatter_sorted] ))
plt.plot(range(-1,max_point), range(-1,max_point))

# plt.scatter(r1, [row[4][0] for row in scatter_sorted],60, label="nbc incomp", marker="s", color="orange")
# plt.scatter(r1, [row[5][0] for row in scatter_sorted],60, label="glucose", marker="s", color="maroon")
# plt.scatter(r1, [row[6][p] for row in scatter_sorted],60, label="glucose D", marker="s", color="red")


# plt.scatter([row[1] for row in scatter_sr_sorted], [row[2] for row in scatter_sr_sorted], 60, marker="x", color="black")
# plt.plot(r2)

plt.xlim([0.05, 30000])
plt.ylim([0.05, 30000])

if "log" in plot_v:
    plt.yscale('log')
    plt.xscale('log')
if p == 0:
    # plt.title("CDP vs CDP+I Comparison on solver time")
    if "cdp" in sys.argv[5]:
        plt.ylabel("Minion")
    elif 'comp' in sys.argv[5]:
        plt.ylabel("CDP+I")
    elif "inter" in sys.argv[5]:
        plt.ylabel("CDP+I normal")
    else:
        plt.ylabel("CDP-level-order")
if p == 2:
    plt.title("total time")
    plt.ylabel("solver time CDP")
elif p == 4:
    plt.title("nb of sols")



if "cdp" in sys.argv[5]:
    plt.xlabel("SAT")
elif 'comp' in sys.argv[5]:
    plt.xlabel("CDP+I with reformulation")
elif "level" in sys.argv[5]:
    plt.xlabel("CDP-level-order")
    plt.ylabel("CDP-default-order")
elif "inter" in sys.argv[5]:
    if x == 1:
        plt.xlabel("CDP+I Minion")
    elif x == 2:
        plt.xlabel("CDP Minion Default")
    elif x == 3:
        plt.xlabel("CDP+I NBC")
    elif x == 4:
        plt.xlabel("CDP NBC")
    elif x == 5:
        plt.xlabel("CDP+I Glucose")
    elif x == 6:
        plt.xlabel("CDP Glucose")
    elif x == 7:
        plt.xlabel("CDP Minion Ordered")
    elif x == 8:
        plt.xlabel("CDP+I Glucose ordered (no block)")
    elif x == 9:
        plt.xlabel("CDP+I Minion reform")
    elif x == 10:
        plt.xlabel("CDP+I NBC reform")
    elif x == 11:
        plt.xlabel("CDP+I NBC inter ")
    elif x == 12:
        plt.xlabel("CDP+I glucose inter")
    elif x == 13:
        plt.xlabel("CDP+I glucose no block")
    if y == 1:
        plt.ylabel("CDP+I Minion")
    elif y == 2:
        plt.ylabel("CDP Minion Default")
    elif y == 3:
        plt.ylabel("CDP+I NBC")
    elif y == 4:
        plt.ylabel("CDP NBC")
    elif y == 5:
        plt.ylabel("CDP+I Glucose")
    elif y == 6:
        plt.ylabel("CDP Glucose")
    elif y == 7:
        plt.ylabel("CDP Minion Ordered")
    elif y == 8:
        plt.ylabel("CDP+I Glucose ordered (no block)")
    elif y == 9:
        plt.ylabel("CDP+I Minion reform")
    elif y == 10:
        plt.ylabel("CDP+I NBC reform")
    elif y == 11:
        plt.ylabel("CDP+I NBC inter ")
    elif y == 12:
        plt.ylabel("CDP+I glucose inter")
    elif y == 13:
        plt.ylabel("CDP+I glucose no block")

else:
    plt.xlabel("CDP+I")


# print(max_point)

# plt.ylim(0, max_point)


# ax.set_aspect(1.0/ax.get_data_ratio()*0.5)
plt.tight_layout()
# Create legend & Show graphic
plt.legend()
if save:
    if  sort_key ==3:
       plot_v += "_sorted" 
    plt.savefig(sys.argv[2]+"_"+str(x)+"_vs_"+str(y)+"_"+plot_v+".pdf",format="pdf")

else:
    plt.show()
