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

    threshold = str(int(sys.argv[2]))
    # file = "all_edit_no_sol_instances_removed.csv"
    file = "training_data/" + threshold + "/train_{}_time.csv".format(sys.argv[1])


    df = pd.read_csv(file, index_col=0)


    for idx, i in enumerate(df):
        for index, j in enumerate(df[i]):
            if np.isnan(j):
                df[i][index] = 21600

    dft = df.transpose()

    vbest = dict()
    for idx, i in enumerate(dft):
        min = np.min(dft[i])
        vbest[i] = min

    growing_sbest = dict()

    sbs_order = [0] * 20
    current_min = 216000000.0
    for idx, i in enumerate(df):
        if current_min > np.sum(df[i]):
            current_min = np.min([current_min, np.sum(df[i])])
            # print("NEW SBS", i)
            sbs_order[0] = i

    
    file = "training_data/" + threshold + "/test_{}_time.csv".format(sys.argv[1])
    df = pd.read_csv(file, index_col=0)
    for idx, i in enumerate(df):
        for index, j in enumerate(df[i]):
            if np.isnan(j):
                df[i][index] = 21600
    dft = df.transpose()

    vbest = dict()
    for idx, i in enumerate(dft):
        min = np.min(dft[i])
        vbest[i] = min

    growing_sbest_time = np.sum(df[sbs_order[0]])

    print("vbest",threshold, sys.argv[1], "-", np.sum(list(vbest.values())), sep=",")
    print("sbs",threshold, sys.argv[1], "-", growing_sbest_time, sep=",")
