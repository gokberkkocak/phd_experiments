# this came from growing sbs run on train data on time.
import pandas as pd
import numpy as np
import os
sbs_train_order = [
    ['GAC_occ_occ_nbc_11000001', 'GAC_occ_occ_glucose_11000001', 'SSACBounds_limit_occ_occ_nbc_11000001', 'SACBounds_limit_exp_occ_glucose_11100001', 'None_exp_occ_glucose_11000001', 'SACBounds_limit_occ_occ_nbc_11000001', 'SSACBounds_limit_exp_occ_nbc_11000001', 'SACBounds_limit_occ_occ_glucose_11000001', 'SACBounds_limit_exp_occ_nbc_11000001', 'SSACBounds_limit_exp_occ_glucose_11000001',
     'GAC_exp_occ_nbc_11000001', 'SACBounds_limit_exp_occ_glucose_11100101', 'None_occ_occ_glucose_11000001', 'SACBounds_limit_occ_occ_nbc_11100001', 'None_exp_occ_nbc_11000001', 'SACBounds_limit_exp_occ_glucose_01000001', 'None_exp_occ_cadical_11000001', 'SACBounds_limit_exp_occ_nbc_11100001', 'GAC_exp_occ_cadical_11000001', 'SACBounds_limit_exp_occ_glucose_11000001'],
    ['GAC_occ_occ_nbc_11000001', 'GAC_occ_occ_glucose_11000001', 'None_occ_occ_nbc_11000001', 'SACBounds_limit_occ_occ_glucose_11000001', 'SACBounds_limit_occ_occ_nbc_11000001', 'SACBounds_limit_exp_occ_glucose_01000001', 'SACBounds_limit_exp_occ_glucose_11100101', 'None_occ_occ_glucose_11000001', 'SACBounds_limit_exp_occ_glucose_11000001', 'SACBounds_limit_occ_occ_nbc_11100001',
        'SACBounds_limit_occ_occ_cadical_11000001', 'SACBounds_limit_occ_occ_glucose_11100101', 'SACBounds_limit_exp_occ_nbc_11100001', 'None_exp_occ_nbc_11000001', 'SACBounds_limit_occ_occ_lia_yices2_11000001', 'GAC_exp_occ_nbc_11000001', 'SSACBounds_limit_exp_occ_nbc_11000001', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001'],
    ['SACBounds_limit_exp_occ_nbc_11010001', 'None_occ_occ_glucose_11000001', 'SACBounds_limit_exp_occ_glucose_11100001', 'None_exp_occ_glucose_11000001', 'SACBounds_limit_occ_occ_glucose_11000001', 'SACBounds_limit_occ_occ_nbc_11000001', 'SSACBounds_limit_exp_occ_glucose_11000001', 'GAC_exp_occ_nbc_11000001', 'SACBounds_limit_occ_occ_nbc_11100001', 'GAC_occ_occ_nbc_11000001',
        'SACBounds_limit_occ_occ_cadical_11000001', 'SACBounds_limit_exp_occ_glucose_11000001', 'SACBounds_limit_exp_occ_nbc_11100001', 'SACBounds_limit_occ_occ_lia_yices2_11000001', 'GAC_exp_occ_glucose_11000001', 'SACBounds_limit_occ_occ_glucose_11100101', 'SSACBounds_limit_occ_occ_cadical_11000001', 'SACBounds_limit_exp_occ_glucose_11100101', 'None_exp_occ_nbc_11000001', 'GAC_exp_exp_boolector_10000001'],
    ['SACBounds_limit_occ_occ_nbc_11000001', 'SSACBounds_limit_occ_occ_nbc_11000001', 'SSACBounds_limit_exp_occ_glucose_11000001', 'SACBounds_limit_occ_occ_glucose_11000001', 'SACBounds_limit_exp_occ_nbc_11000001', 'SACBounds_limit_exp_occ_glucose_11100101', 'GAC_exp_occ_cadical_11000001', 'SACBounds_limit_exp_occ_nbc_11100001', 'SACBounds_limit_occ_occ_cadical_11000001',
        'SACBounds_limit_occ_occ_nbc_11100001', 'SACBounds_limit_exp_occ_glucose_11000001', 'None_occ_occ_glucose_11000001', 'GAC_occ_occ_nbc_11000001', 'SACBounds_limit_occ_occ_glucose_11100101', 'SACBounds_limit_occ_occ_lia_yices2_11000001', 'None_occ_occ_nbc_11000001', 'None_exp_occ_cadical_11000001', 'GAC_occ_occ_glucose_11000001', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001'],
    ['GAC_occ_occ_nbc_11000001', 'GAC_occ_occ_glucose_11000001', 'SACBounds_limit_exp_occ_nbc_11100001', 'SACBounds_limit_occ_occ_glucose_11000001', 'SACBounds_limit_exp_occ_nbc_11000001', 'GAC_exp_occ_cadical_11000001', 'SACBounds_limit_occ_occ_nbc_11000001', 'SACBounds_limit_exp_occ_glucose_11000001', 'SACBounds_limit_occ_occ_nbc_11100001', 'SACBounds_limit_exp_occ_glucose_11100101',
        'SACBounds_limit_occ_occ_lia_yices2_11000001', 'None_occ_occ_nbc_11000001', 'SACBounds_limit_occ_occ_cadical_11000001', 'SACBounds_limit_occ_occ_glucose_11100101', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001'],
    ['SACBounds_limit_occ_occ_nbc_11000001', 'SACBounds_limit_exp_occ_nbc_11100001', 'SSACBounds_limit_occ_occ_nbc_11000001', 'SACBounds_limit_occ_occ_glucose_11000001', 'GAC_exp_occ_nbc_11000001', 'SACBounds_limit_exp_occ_glucose_11100101', 'SACBounds_limit_occ_occ_nbc_11100001', 'GAC_exp_occ_glucose_11000001', 'SACBounds_limit_occ_occ_lia_yices2_11000001', 'None_occ_occ_nbc_11000001',
        'SACBounds_limit_occ_occ_glucose_11100001', 'SACBounds_limit_occ_occ_glucose_11100101', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001', 'GAC_exp_exp_boolector_10000001']
]


def predict(index, random):
    file = "training_data/test_" + str(index) + "_time.csv"

    times = pd.read_csv(file, index_col=0)
    times = times[[]]
    # print(times)

    # UNION
    feature_pattern = "cmf"
    pattern = str(index) + "_" + str(random)+"_" + \
        feature_pattern+"_predictions.csv"
    # print(pattern)
    for f in os.listdir("training/models/"):
        if pattern in f:
            path = os.path.join("training/models", f)
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

    # df.to_csv("preds.csv")

    # TEST FILE

    file = "training_data/test_" + str(index) + "_time.csv"

    times = pd.read_csv(file, index_col=0)

    pred_time = []

    for idx, i in enumerate(df.iterrows()):
        # print(idx)
        for config in sbs_train_order[index]:
            column = config+"_prediction"
            if column in df:
                if df[column][idx] == 1:
                    a = times[config][idx]
                    # print(column, a)
                    if np.isnan(a):
                        a = 21600
                    pred_time.append(a)
                    break
        else:
            pred_time.append(21600)

    # print(pred_time)
    # print(len(pred_time))
    count = 0
    for p in pred_time:
        if p >= 21500:
            count += 1
    # print("Timeout count", count)
    print(feature_pattern, index, random, sum(pred_time), sep=",")


def predict_all():
    print("predictor, training_split, rnd, sum_time")
    for i in range(6):
        for r in range(2):
            predict(i, r)


if __name__ == "__main__":
    predict_all()
