import pandas as pd
import sys
import numpy as np

best_configs = [
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

# all_edit_comp_25_10secs_removed_0
df = pd.read_csv(sys.argv[1], index_col=0)


print(df)

to_remove = []
for i, row in df.iterrows():
    # for time csv
    # if all(np.isnan(i) for i in row):
    if row.sum() == 0:
        to_remove.append(i)

print(to_remove)

df = df.drop(to_remove, axis="index")

print(df)

df.to_csv(sys.argv[1].split(".")[0]+"_no_sol_instances_removed.csv")