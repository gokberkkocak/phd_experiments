import sys
import json
import pandas as pd
import os
import numpy as np
from collections import OrderedDict

from fanova import fANOVA
import fanova.visualizer

import ConfigSpace
from ConfigSpace.hyperparameters import UniformFloatHyperparameter

final_name_set = [
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
    # "SACBounds_limit_exp_occ_glucose_11100101",
    "SACBounds_limit_exp_occ_nbc_11000001",
    # "SACBounds_limit_exp_occ_nbc_11100001",
    "SACBounds_limit_occ_occ_cadical_11000001",
    "SACBounds_limit_occ_occ_glucose_11000001",
    # "SACBounds_limit_occ_occ_glucose_11100001",
    # "SACBounds_limit_occ_occ_glucose_11100101",
    "SACBounds_limit_occ_occ_lia_yices2_11000001",
    "SACBounds_limit_occ_occ_nbc_11000001",
    # "SACBounds_limit_occ_occ_nbc_11100001",
    "SSACBounds_limit_exp_occ_nbc_11000001",
    "SSACBounds_limit_occ_occ_cadical_11000001",
    "SSACBounds_limit_occ_occ_nbc_11000001",
    "None_exp_occ_cadical_11000001",
    # "SACBounds_limit_exp_occ_glucose_11100001",
    "SSACBounds_limit_occ_occ_glucose_11000001",
    "SSACBounds_limit_occ_occ_lia_yices2_11000001",
    "SSACBounds_limit_exp_occ_glucose_11000001"]

index = int(sys.argv[1])
train_index = str(int(sys.argv[2]))
rnd_seed = str(int(sys.argv[3]))
threshold = str(int(sys.argv[4]))

features_file = "final_features.json"


with open(features_file, 'r') as f:
    features = json.load(f)

features = OrderedDict(sorted(features.items(), key=lambda t: t[0]))

preds_file = "../training_data/" + threshold + \
    "/preds_" + train_index + "_" + rnd_seed + ".csv"

df = pd.read_csv(preds_file, index_col=0)

# df = df[final_name_set]
config_list = list(final_name_set)
config_list.sort()
config = config_list[index]
df = df[[config+"_prediction"]]  # reduce to one config prediction
y_hat = df

X = pd.DataFrame.from_dict(features, orient="index")
drop = ["utility_values_1_geometricMean", "cost_values_1_geometricMean"]
X = X.drop(drop, axis="columns")

column_dict = dict()
for idx, i in enumerate(X.columns):
    column_dict[idx] = i
# print(X)

X = np.array(X, dtype=float)
y_hat = np.array(y_hat, dtype=float)


# create an instance of fanova with trained forest and ConfigSpace
f = fANOVA(X=X, Y=y_hat)


importance_dict = dict()
importance_dict["individual"] = dict()
for i in range(43):
    # marginal of particular parameter:
    dims = (i, )
    res = f.quantify_importance(dims)
    importance_dict["individual"][column_dict[i]] = res[dims]

# getting the 10 most important pairwise marginals sorted by importance
best_margs = f.get_most_important_pairwise_marginals(n=10)

best_margs_altered = []

for t in best_margs.items():
    pair = t[0]
    f = column_dict[int(pair[0].split("x_")[1])]
    s = column_dict[int(pair[1].split("x_")[1])]

    best_margs_altered.append({"pair": (f, s), "importance": t[1]})

importance_dict["pairwise"] = best_margs_altered

os.makedirs(os.path.join("importance", threshold), exist_ok=True)

final_json = "importance/" + threshold + "/" + \
    config + "_" + train_index + "_" + rnd_seed + ".json"

with open(final_json, "w") as f:
    json.dump(importance_dict, f, indent=2)
