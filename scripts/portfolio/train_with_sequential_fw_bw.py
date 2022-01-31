import json
import pandas as pd
import os
import numpy as np
import sys
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.feature_selection import RFECV
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier
import sklearn.model_selection
import sklearn.datasets
import sklearn.metrics
import pickle

from collections import OrderedDict


def get_feature_name(feature_names, feature_idx):
    dump_key = list(feature_names.keys())[0]
    for idx, i in enumerate(feature_names[dump_key]):
        if idx == feature_idx:
            return i


if __name__ == '__main__':

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

    threshold = str(int(sys.argv[4]))
    fw_bw_flag = int(sys.argv[5])
    if fw_bw_flag == 0:
        direction = "forward"
    elif fw_bw_flag == 1:
        direction = "backward"
    elif fw_bw_flag == 2:
        direction = "rfe"
    else:
        direction = "rfecv"

    suffix = "_pickled_013_single_rf" + "/" + "seq/"

    # TRAIN

    competitive_file = "../training_data/" + \
        threshold + "/train_" + train_index + ".csv"

    df = pd.read_csv(competitive_file, index_col=0)

    # print(df)

    df = df[final_name_set]

    config_list = list(final_name_set)
    config_list.sort()
    config = config_list[index]
    df = df[[config]]
    rnd_seed = int(sys.argv[3])
    final_json = "models/" + threshold + suffix + config + "_with_seq_feature_selection_" + train_index + "_" + direction + "_" + \
        str(int(rnd_seed))+"_{}.json"

    features_file = "final_features.json"
    final_json = final_json.format("finalf")

    if os.path.exists(final_json):
        print(final_json, "already exists")
        sys.exit(0)

    with open(features_file, 'r') as f:
        features = json.load(f)

    features = OrderedDict(sorted(features.items(), key=lambda t: t[0]))

    X = []
    y = []
    drop = []
    # clean from splice if any lesft
    for index, row in df.iterrows():
        if "splice" in index:
            drop.append(index)
    df = df.drop(drop, axis="index")
    for index, row in df.iterrows():
        instance = "_".join(index.split("_")[:-1])
        l = []
        for idx, i in enumerate(features[instance]):
            l.append(features[instance][i])
        X.append(l)
        if row[0] > 21600:
            row[0] = np.nan
        y.append(row[0])

    # X, y = sklearn.datasets.load_digits(return_X_y=True)
    X = np.array(X, dtype=float)
    X = np.nan_to_num(X)
    y = np.array(y, dtype=bool)
    y = np.nan_to_num(y)

    print(X)
    print(y)

    print(X.shape)
    print(y.shape)

    X_train, X_validate, y_train, y_validate = \
        sklearn.model_selection.train_test_split(X, y, random_state=1)

    pickled_clf_file = "models/" + threshold + "_pickled_013_single_rf" + "/" + config + "_with_test_" + train_index + "_" + \
        str(int(rnd_seed))+"_finalf.pkl"

    print("using pickled clf from: {}".format(pickled_clf_file))
    with open(pickled_clf_file, "rb") as f:
        clf = pickle.load(f)

    if fw_bw_flag <= 1:
        sfs = SequentialFeatureSelector(
            clf, n_features_to_select=5, direction=direction)
    elif fw_bw_flag == 2:
        sfs = RFE(clf, n_features_to_select=5, step=1)
    else:
        sfs = RFECV(clf, step=1, cv=5)
    sfs.fit(X, y)
    res_supports = sfs.get_support()

    print(res_supports)

    features_file = "final_features.json"

    with open(features_file, 'r') as f:
        features = json.load(f)
    feature_names = OrderedDict(sorted(features.items(), key=lambda t: t[0]))
    
    print(sfs.transform(X).shape)

    d = dict()
    supports = []
    for idx, i in enumerate(res_supports):
        if "True" == str(i):
            supports.append(get_feature_name(feature_names,idx))
    
    d["supported_f"] = supports

    os.makedirs("models/" + threshold + suffix, exist_ok=True)

    with open(final_json, "w") as f:
        json.dump(d, f, indent=1)
