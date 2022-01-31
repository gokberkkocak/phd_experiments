import os, sys, json
import numpy as np

path = "../models/100_pickled_013/seq_first"
dirs = os.listdir( path )

array = []
for f in dirs: 
    if "rfecv" in f:
        with open(os.path.join(path, f), "r") as json_file:
            s_data = json.load(json_file)
            lens = len(s_data["supported_f"])
            if lens < 12:
                array.append(lens)

print(np.median(array))
print(np.mean(array))