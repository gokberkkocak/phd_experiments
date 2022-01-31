import json
import pandas as pd
import os
import numpy as np
import sys
import autosklearn.classification
import sklearn.model_selection
import sklearn.datasets
import sklearn.metrics

from collections import OrderedDict

if __name__ == '__main__':


    sets = [[1, 3, 5, 9, 11, 13, 14, 15, 17, 18, 19, 20, 21, 23, 26, 28],
            [1, 3, 5, 7, 9, 11, 13, 15, 17, 18, 19, 20, 21, 23, 26, 28],
            [1, 3, 5, 6, 11, 13, 14, 15, 17, 18, 19, 20, 21, 23, 26, 28],
            [1, 3, 5, 6, 7, 11, 13, 15, 17, 18, 19, 20, 21, 23, 26, 28]]

    # final_set: set[int] = set()
    final_set = set()

    for s in sets:
        final_set.update(s)

    # print(final_set)

    config_name_file = "config_hits.json"

    with open(config_name_file, "r") as f:
        d = json.load(f)

    final_name_set = set()
    for config_name in d:
        id = d[config_name]["id"]
        if id in final_set:
            final_name_set.add(config_name)

    # print(final_name_set)

    train_file = "all_edit_no_sol_instances_removed.csv"

    df = pd.read_csv(train_file, index_col=0)

    # print(df)

    df = df[final_name_set]

    index = int(sys.argv[1])
    config_list = list(final_name_set)
    config_list.sort()
    config = config_list[index]
    df = df[[config]]



    features_file = "training/features.json"
    with open(features_file, 'r') as f:
        features = json.load(f)

    features = OrderedDict(sorted(features.items(), key=lambda t: t[0]))

    X = []
    y = []
    for index, row in df.iterrows():
        if "splice" in index:
            continue
        index = index.replace("extra_", "")
        instance = "_".join(index.split("_")[-3:-1])
        l = []
        for i in features[instance]:
            l.append(features[instance][i])
        X.append(l)
        y.append(row[0])

    # X, y = sklearn.datasets.load_digits(return_X_y=True)
    X = np.array(X, dtype=float)
    y = np.array(y, dtype=float)

    print(X)
    print(y)

    print(X.shape)
    print(y.shape)

    X_train, X_test, y_train, y_test = \
        sklearn.model_selection.train_test_split(X, y, random_state=1)

    print(X_test)
    print(y_test)

    pd.DataFrame(X_train).to_csv(config+"_x_train.csv")
    pd.DataFrame(y_train).to_csv(config+"_y_train.csv")
    pd.DataFrame(X_test).to_csv(config+"_x_test.csv")
    pd.DataFrame(y_test).to_csv(config+"_y_test.csv")

    # # automl = autosklearn.classification.AutoSklearnClassifier()
    # automl = autosklearn.classification.AutoSklearnClassifier(
    #     # ensemble_size=1,
    #     time_left_for_this_task=600,
    #     per_run_time_limit=150,
    #     # tmp_folder='/tmp/autosklearn_parallel_1_example_tmp',
    #     # output_folder='/tmp/autosklearn_parallel_1_example_out',
    #     n_jobs=10,
    #     # Each one of the 4 jobs is allocated 3GB
    #     memory_limit=24096,
    #     seed=rnd_seed,
    # )

    # automl.fit(X_train, y_train)

    # # print(automl.cv_results_)

    # d = dict()
    # d["stats"] = automl.sprint_statistics()

    # d["models"] = automl.show_models()

    # y_hat = automl.predict(X_test)

    # d["accuracy_score"] = sklearn.metrics.accuracy_score(y_test, y_hat)

    # os.makedirs('models', exist_ok=True)

    # with open(final_json, "w") as f:
    #     json.dump(d, f, indent=1)
