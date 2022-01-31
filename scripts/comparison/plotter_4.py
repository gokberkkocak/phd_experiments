import json
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import matplotlib
import numpy as np
from scipy import stats
import math


def process_config(new_tree_str, exp, config):

    if (config in new_tree_str[exp]):
        if new_tree_str[exp][config]["total_solver_time_best"] is not None:
            sol = float(new_tree_str[exp][config]["total_solver_time_best"])
            sr = float(new_tree_str[exp][config]["total_sr_time_best"])
        else:
            sol = np.NaN
            sr = np.NaN
    else:
        sol = np.NaN
        sr = np.NaN
    return (sol, sr)


json_file = sys.argv[1]
if len(sys.argv) > 4:
    if "save" in sys.argv[4]:
        save = True


with open(json_file, "r") as jf:
    new_tree_str = json.load(jf)


scatter = []

new_tree_str = new_tree_str["store"]

configs = ["None_occ_occ_nbc_11000001",
           "None_occ_occ_yices2_11000001", "None_occ_occ_lia_yices2_11000001", "None_occ_occ_z3_11000001", "None_occ_occ_lia_z3_11000001", "None_occ_occ_nia_z3_11000001", "None_occ_occ_idl_z3_11000001", "None_occ_occ_boolector_11000001"]

for exp in new_tree_str:
    print(exp)
    if sys.argv[2] in exp and "minimal" not in exp:
        # min_res = process_config(new_tree_str, exp, "minion")
        # min_n_res = process_config(new_tree_str, exp, "minion_noincomp")
        # nbc_res = process_config(new_tree_str, exp, "nbc")
        # nbc_n_res = process_config(new_tree_str, exp, "nbc_noincomp")
        # glu_res = process_config(new_tree_str, exp, "glucose")
        # glu_n_res = process_config(new_tree_str, exp, "glucose_noincomp")
        # min_n_ord_red = process_config(new_tree_str, exp, "minion_noincomp_ordered")
        # glu_n_ord_red = process_config(new_tree_str, exp, "glucose_noincomp_ordered")
        # min_comp = process_config(new_tree_str, exp, "minion_compressed")
        # nbc_comp = process_config(new_tree_str, exp, "nbc_compressed")
        # nbc_int_res = process_config(new_tree_str, exp, "nbc_interactive")
        # glu_int_res = process_config(new_tree_str, exp, "glucose_interactive")
        # glu_int_nb_res = process_config(new_tree_str, exp, "glucose_interactive_noblock") # 13

        nbc_int_res = process_config(
            new_tree_str, exp, configs[0])
        yices_bv_int_res = process_config(
            new_tree_str, exp, configs[1])
        yices_lia_int_res = process_config(
            new_tree_str, exp, configs[2])
        z3_bv_int_res = process_config(
            new_tree_str, exp, configs[3])
        z3_lia_int_res = process_config(
            new_tree_str, exp, configs[4])
        z3_nia_int_res = process_config(
            new_tree_str, exp, configs[5])
        z3_idl_int_res = process_config(
            new_tree_str, exp, configs[6])
        boolector_bv_int_res = process_config(
            new_tree_str, exp, configs[7])
        sol_sr = (exp, nbc_int_res, yices_bv_int_res, yices_lia_int_res, z3_bv_int_res,
                  z3_lia_int_res, z3_nia_int_res, z3_idl_int_res, boolector_bv_int_res)
        print(sol_sr)
        # sol_sr = (exp, min_res, min_n_res, nbc_res, nbc_n_res, glu_res, glu_n_res, min_n_ord_red, glu_n_ord_red, min_comp, nbc_comp, nbc_int_res, glu_int_res, glu_int_nb_res)

        # if (not np.isnan(nbc_int_res[0]) and not np.isnan(nbc_res[0])):
        #     if nbc_int_res[0] > nbc_res[0]:
        #       print(exp)
        # sol = (exp, sat_sol, sat_n_sol, min_sol, min_n_sol, sat_sol_err, sat_n_sol_err, min_sol_err, min_n_sol_err, min_sols, min_n_sols, sat_sols, sat_n_sols)
        # sr = (exp, sat_sr, sat_n_sr, min_sr, min_n_sr, sat_sr_err, sat_n_sr_err, min_sr_err, min_n_sr_err, min_sols, min_n_sols, sat_sols, sat_n_sols)

        have_something = False
        for i in range(1, len(sol_sr)):
            # if (not np.isnan(sol_sr[i][0])) and not np.isnan(min_res[0]):
            if (not np.isnan(sol_sr[i][0])):
                if sol_sr[i][0] < 21600 and sol_sr[i][0] > 0.001:
                    have_something = True
        if have_something:
            scatter.append(sol_sr)

# scatter_sorted = sorted(scatter_sr, key=lambda x: x[1])
# print(scatter[1])
new_configs = []
for config in configs:
    config = "_".join(config.split("_")[3:-1])
    new_configs.append(config)
configs = new_configs

print(scatter)
sort_key = 1
time = 0

if sort_key == 0:
    scatter_sorted = sorted(scatter, key=lambda x: x[sort_key])
else:
    # solver time
    scatter_sorted = sorted(scatter, key=lambda x: float(
        'inf') if math.isnan(x[sort_key][0]) else x[sort_key][time])
    # nodes
    # scatter_sorted = sorted(scatter, key=lambda x: float('inf') if math.isnan(x[sort_key][5]) else x[sort_key][5])
    # nb
    # scatter_sorted = sorted(scatter, key=lambda x: float('inf') if math.isnan(x[sort_key][4]) else x[sort_key][4])
    # size
    # scatter_sorted = sorted(scatter, key=lambda x: float('inf') if math.isnan(x[sort_key][6]) else x[sort_key][6])

print(scatter_sorted[0])
index = 0
for i in scatter_sorted:
    print(str(index) + ' ' + i[0])
    index += 1

# print(scatter_sol_sorted)
fig, ax = plt.subplots(figsize=(10, 4))
# fig, ax = plt.subplots(figsize=(12,6))
r1 = np.arange(len(scatter_sorted))
r2 = np.arange(10800)
matplotlib.rc('legend', fontsize=8)




# plt.scatter(r1, [row[2][p] for row in scatter_sorted],60, label="Minion CDP_default_order", marker="s", color="green",alpha=0.5, edgecolors ="none")
# plt.scatter(r1, [row[7][p] for row in scatter_sorted],60, label="Minion CDP_level_order", marker="s", color="red",alpha=0.5, edgecolors ="none")
plt.scatter(r1, [row[1][time] for row in scatter_sorted], 60, label=configs[0], marker="x", color="blue", alpha=0.5, edgecolors="none")
plt.scatter(r1, [row[2][time] for row in scatter_sorted], 60, label=configs[1], marker="x", color="orange", alpha=0.5, edgecolors="none")
plt.scatter(r1, [row[3][time] for row in scatter_sorted], 60, label=configs[2], marker="+", color="green", alpha=0.5, edgecolors="none")
plt.scatter(r1, [row[4][time] for row in scatter_sorted], 60, label=configs[3], marker="+", color="grey", alpha=0.5, edgecolors="none")
plt.scatter(r1, [row[5][time] for row in scatter_sorted], 60, label=configs[4], marker="o", color="magenta", alpha=0.5, edgecolors="none")
plt.scatter(r1, [row[6][time] for row in scatter_sorted], 60, label=configs[5], marker="o", color="orange", alpha=0.5, edgecolors="none")
plt.scatter(r1, [row[7][time] for row in scatter_sorted], 60, label=configs[6], marker="x", color="red", alpha=0.5, edgecolors="none")
plt.scatter(r1, [row[8][time] for row in scatter_sorted], 60, label=configs[7], marker="+", color="cyan", alpha=0.5, edgecolors="none")
# plt.scatter(r1, [row[6][p] for row in scatter_sorted],60, label="SAT CDP_default_order", marker="+", color="cyan",alpha=0.5, edgecolors ="none")
# plt.scatter(r1, [row[8][p] for row in scatter_sorted],60, label="SAT CDP_level_order", marker="+", color="grey",alpha=0.5, edgecolors ="none")
# plt.scatter(r1, [row[3][p] for row in scatter_sorted],60, label="SAT CDP+I", marker="o", color="black",alpha=0.5, edgecolors ="none")
# plt.scatter(r1, [row[10][p] for row in scatter_sorted],60, label="SAT CDP+I (reformulated)", marker="o", color="magenta", alpha=0.5, edgecolors ="none")
# plt.scatter(r1, [row[11][p] for row in scatter_sorted],60, label="SAT NBC CDP+I (int)", marker="o", color="green", alpha=0.5, edgecolors ="none")
# plt.scatter(r1, [row[12][p] for row in scatter_sorted],60, label="SAT Glucose CDP+I (int)", marker="o", color="red", alpha=0.5, edgecolors ="none")
# plt.scatter(r1, [row[13][p] for row in scatter_sorted],60, label="SAT Glucose CDP+I (int/nb)", marker="o", color="cyan", alpha=0.5, edgecolors ="none")

# plt.scatter(r1, [row[4][0] for row in scatter_sorted],60, label="nbc incomp", marker="s", color="orange")
# plt.scatter(r1, [row[5][0] for row in scatter_sorted],60, label="glucose", marker="s", color="maroon")

# plt.xticks(r1, [x[0] for x in scatter_sorted], rotation='vertical')

# plt.scatter([row[1] for row in scatter_sr_sorted], [row[2] for row in scatter_sr_sorted], 60, marker="x", color="black")
# plt.plot(r2)


plt.yscale('log')

p = time
if p == 0:
    # plt.title("solver time")
    plt.ylabel("Solver Time in seconds")
if p == 1:
    # plt.title("solver time")
    plt.ylabel("SR Time in seconds")
# if p == 2:
#     plt.title("total time")
#     plt.ylabel("time in secs")
# elif p == 4:
#     plt.title("nb of sols")
# elif p == 5:
#     plt.title("Total search nodes")
# elif p == 6:
#     plt.title("End File Size")

plt.xlabel("Instances")

plt.xticks([])

# ax.set_aspect(1.0/ax.get_data_ratio()*0.5)
plt.tight_layout()
# Create legend & Show graphic
plt.legend()
save = True
if save:
    if sort_key == 3 or sort_key == 10:
        plot_v += "_sorted"
    plt.savefig(sys.argv[2]+"_"+".pdf", format="pdf")

else:
    plt.show()
