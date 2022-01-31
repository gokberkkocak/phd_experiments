import pandas as pd
# import sys
import numpy as np
# import json
import sys

if __name__ == '__main__':
    best_30 = [
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

    # file = "all_edit_no_sol_instances_removed.csv"
    file = "training_data/test_{}_time.csv".format(sys.argv[1])


    df = pd.read_csv(file, index_col=0)
    dft = df.transpose()

    for idx, i in enumerate(df):
        for index, j in enumerate(df[i]):
            if np.isnan(j):
                df[i][index] = 21600

    vbest = dict()
    for idx, i in enumerate(dft):
        min = np.min(dft[i])
        vbest[i] = min

    growing_sbest = dict()

    # for iter in range(30):
    #     # print(dft.to_numpy())
    #     min_indexs = np.nanargmin(dft.to_numpy(), axis=0)
    #     # print('mins', min_indexs)
    #     counts = np.bincount(min_indexs)
    #     winner_of_this_round = np.argmax(counts)
    #     # print('winner', winner_of_this_round)
    #     drop = []
    #     for idx, i in enumerate(dft):
    #         if min_indexs[idx] == winner_of_this_round:
    #             growing_sbest[i] = dft[i][winner_of_this_round]
    #             drop.append(i)
    #     dft = dft.drop(drop, axis = 1)
    #     print("iter {} : {} / {}".format(iter, len(growing_sbest), len(vbest)))

    sbs_order = [0] * 20
    growing_sbest_time = dict()
    current_min = 216000000.0
    for idx, i in enumerate(df):
        if current_min > np.sum(df[i]):
            current_min = np.min([current_min, np.sum(df[i])])
            # print("NEW SBS", i)
            sbs_order[0] = i
            for jdx, j in enumerate(dft):
                growing_sbest_time[j] = df[i][j]
    # print(growing_sbest_time)
    # print("vbest", np.sum(list(vbest.values())))
    # print("sbs", np.sum(list(growing_sbest_time.values())))
    print("vbest", sys.argv[1], "-", np.sum(list(vbest.values())))
    print("sbs", sys.argv[1], "-", np.sum(list(growing_sbest_time.values())))
    sys.exit(1)
    for iter in range(1,20):
        candidates = dict()
        for idx, i in enumerate(df):
            clone = growing_sbest_time.copy()
            for jdx, j in enumerate(dft):
                clone[j] = np.min( [clone[j], df[i][jdx]] )
            if np.sum(list(clone.values())) <= np.sum(list(growing_sbest_time.values())):
                candidates[i] = clone
        min = 216000000.0
        for c in candidates:
            if np.sum(list(candidates[c].values())) < min:
                min = np.sum(list(candidates[c].values()))
                growing_sbest_time = candidates[c]
                sbs_order[iter] = c
        # print(iter, "sum: ", np.sum(list(growing_sbest_time.values())))

    # print(sbs_order)

