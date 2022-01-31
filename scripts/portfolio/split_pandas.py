import json
import pandas as pd
import os
import sys
import numpy as np

from collections import OrderedDict

if __name__ == '__main__':

    seq = str(int(sys.argv[1]))  # want str but should check if int

    threshold = "150"

    train_file = "all_edit_comp_"+ threshold +"_10secs_removed_0_no_sol_instances_removed.csv"
    train_file_time = "all_edit_no_sol_instances_removed.csv"

    df = pd.read_csv(train_file, index_col=0)

    dft = df.transpose()

    cols = []
    for col in dft.columns:
        cols.append(col)

    np.random.shuffle(cols)
    ratio = 0.8

    train_cols = cols[:int(len(cols)*ratio)]
    test_cols = cols[int(len(cols)*ratio):]
    print(list(train_cols))
    print(list(test_cols))

    train = dft[train_cols]
    test = dft[test_cols]

    df_train = train.transpose()
    df_test = test.transpose()

    print(df_train)
    print(df_test)

    os.makedirs("training_data/"+ threshold +"/", exist_ok=True)

    df_train.to_csv("training_data/"+ threshold +"/train_" + seq + ".csv")
    df_test.to_csv("training_data/"+ threshold +"/test_" + seq + ".csv")

    # time info

    df = pd.read_csv(train_file_time, index_col=0)
    dft = df.transpose()

    print(dft)

    train = dft[train_cols]
    test = dft[test_cols]

    df_train = train.transpose()
    df_test = test.transpose()

    df_train.to_csv("training_data/"+ threshold +"/train_" + seq + "_time.csv")
    df_test.to_csv("training_data/" + threshold + "/test_" + seq + "_time.csv")
