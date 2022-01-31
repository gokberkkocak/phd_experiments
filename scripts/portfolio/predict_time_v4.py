# this came from growing sbs run on train data on time.
from ntpath import join
import pandas as pd
import numpy as np
import os
import json
import sys


threshold = sys.argv[2]

def sbs(index):
    file = "../training_data/" + threshold + "/train_" + str(index) + ".csv"

    comp = pd.read_csv(file, index_col=0)
    a = dict()
    for i in comp:
        csum = np.sum(comp[i])
        a[i] = csum

    a = reversed(sorted(a.items(), key=lambda x: x[1]))
    sbs_train_order = []
    for t in a:
        sbs_train_order.append(t[0])
    return sbs_train_order


def predict(index, random, available_features):
    
    if len(available_features) == 0:
        if threshold== "150":
            suffix = "_pickled_013"
        else:
            suffix = ""
    else:
        subfolder = len(available_features)
        suffix = "_" + "_".join(available_features)
        suffix = "/" + str(subfolder) + "/" + suffix 
    file = "../training_data/" + threshold + \
        "/test_" + str(index) + "_time.csv"

    times = pd.read_csv(file, index_col=0)
    times = times[[]]

    # UNION
    if threshold == "100":
        feature_pattern = "finalf_100"
    else:
        feature_pattern = "finalf"
    pattern = str(index) + "_" + str(random)+"_" + \
        feature_pattern+"_predictions.csv"
    # print(pattern)
    for f in os.listdir("models/" + threshold + suffix):
        if pattern in f:
            path = os.path.join("models/" + threshold + suffix, f)
            # print(path)
            df1 = pd.read_csv(path, index_col=0)
            times = df1.merge(times, how='left', left_index=True,
                              right_index=True, suffixes=(False, False))
            # print(times)
    # print(df)

    # ONLY PREDS

    pred = []
    for i in times:
        if "pred" in i:
            pred.append(i)

    df = times[pred]

    pred_file = "models/" + threshold + \
        suffix + "/preds_{}_{}.csv".format(index, random)
    df.to_csv(pred_file)
    sbs_train_order = sbs(index)
    # print(sbs_train_order)
    # TEST FILE

    file = "../training_data/" + threshold + \
        "/test_" + str(index) + "_time.csv"

    times = pd.read_csv(file, index_col=0)

    pred_time = []
    pred_ones = set()
    for idx, i in enumerate(df.iterrows()):
        # print(idx)
        for config in sbs_train_order:
            # column = config
            # config = config[:-11]
            column = config + "_prediction"
            # print(column)
            if column in df:
                pred_ones.add(column)
                if df[column][idx] == 1:
                    a = times[config][idx]
                    # print(column, a)
                    if np.isnan(a):
                        a = 21600
                    pred_time.append(a)
                    break
        else:
            pred_time.append(21600)

    # print(json.dumps({ "i": index, "rand": random, "array": list(pred_ones)}))
    # print(pred_time)
    # print(len(pred_time))
    count = 0
    for p in pred_time:
        if p >= 21500:
            count += 1
    # print("Timeout count", count)
    # print("FIN")

    print(feature_pattern.split("_")[0], threshold , index, random, sum(pred_time), sep=",")
    return sum(pred_time)


if __name__ == "__main__":
    train_set_index = int(sys.argv[1])
    ## no extra args means full set
    available_features = list(map(str, sorted(list(map(int, sys.argv[3:])))))
    predict(train_set_index, 0, available_features)
    predict(train_set_index, 1, available_features)
