import pandas as pd
# import sys
import numpy as np
# import json

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
    file = "training_data/test_0_time.csv"


    df = pd.read_csv(file, index_col=0)

    for idx, i in enumerate(df):
        for index, j in enumerate(df[i]):
            if np.isnan(j):
                df[i][index] = 21600

    df_30 = df[best_30]

    win_count = 0
    win_total = 0

    total_time_30 = 0
    total_time = 0

    for idx, i in enumerate(df.iterrows()):
        min_30 = np.min(df_30.iloc[idx])
        min = np.min(df.iloc[idx])
        total_time_30 += min_30
        total_time += min
        if min_30 - min > 0.1:
            win_count += 1
        win_total += 1

    print("30 is enough on: {} / {}".format(win_total-win_count,win_total))
    print("Percentage :", format((win_total-win_count)/win_total))
    print("-"*50)
    print("30 total sum: {} ".format(total_time_30))
    print("Oracle total sum: {} ".format(total_time))
    print("Time ratio: {}".format( total_time / total_time_30))