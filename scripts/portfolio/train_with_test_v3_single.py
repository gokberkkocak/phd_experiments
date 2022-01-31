import json
import pandas as pd
import os
import numpy as np
import sys
# import autosklearn.classification
from sklearn.ensemble import RandomForestClassifier
import sklearn.model_selection
import sklearn.datasets
import sklearn.metrics
import pickle

from collections import OrderedDict

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

    competitive_file = "../training_data/" + threshold + "/train_" + train_index + ".csv"

    df = pd.read_csv(competitive_file, index_col=0)

    # print(df)

    df = df[final_name_set]

    config_list = list(final_name_set)
    config_list.sort()
    config = config_list[index]
    df = df[[config]]

    rnd_seed = int(sys.argv[3])
    final_json = "models/" + threshold + "_pickled_013_single_rf/" + config+"_with_test_" + train_index + "_" + \
        str(int(rnd_seed))+"_{}.json"

    features_file = "final_features.json"
    final_json = final_json.format("finalf")

    with open(features_file, 'r') as f:
        features = json.load(f)

    if os.path.exists(final_json):
        print(final_json, "already exists")
        sys.exit(0)

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
        for i in features[instance]:
                l.append(features[instance][i])
        X.append(l)
        if row[0] > 21600:
            row[0] = np.nan
        y.append(row[0])

    np.nan_to_num(X)

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

    # automl = autosklearn.classification.AutoSklearnClassifier()
    clf = RandomForestClassifier(
        n_estimators=100,
        random_state=rnd_seed,
        n_jobs=10,
    )

    clf.fit(X_train, y_train)

    # print(automl.cv_results_)

    d = dict()
    # d["stats"] = clf.sprint_statistics()

    # d["models"] = clf.show_models()

    y_hat = clf.predict(X_validate)

    d["validate_accuracy_score"] = sklearn.metrics.accuracy_score(
        y_validate, y_hat)

    os.makedirs('models', exist_ok=True)
    os.makedirs("models/" + threshold + "_pickled_013_single_rf/", exist_ok=True)

    # TEST

    test_file = "../training_data/" + threshold + "/test_" + train_index +".csv"

    df = pd.read_csv(test_file, index_col=0)
    df = df[[config]]
    X_test = []
    y_test = []
    drop = []
    # clean from splice if any lesft
    for index, row in df.iterrows():
        if "splice" in index:
            drop.append(index)
    df = df.drop(drop, axis="index")
    for index, row in df.iterrows():
        instance = "_".join(index.split("_")[:-1])
        l = []
        for i in features[instance]:
            l.append(features[instance][i])
        X_test.append(l)
        if row[0] > 21600:
            row[0] = np.nan
        y_test.append(row[0])

    X_test = np.nan_to_num(X_test)
    y_test = np.nan_to_num(y_test)

    y_hat_test = clf.predict(X_test)

    d["test_accuracy_score"] = sklearn.metrics.accuracy_score(
        y_test, y_hat_test)

    # WRITE

    with open(final_json, "w") as f:
        json.dump(d, f, indent=1)

    # WRITE PREDICTIONS
    df[config+"_prediction"] = list(map(int, y_hat_test))

    df.to_csv(final_json.split(".")[0]+"_predictions.csv")

    # PICKLE
    with open(final_json.split(".")[0]+".pkl", 'wb') as f:
        pickle.dump(clf, f)