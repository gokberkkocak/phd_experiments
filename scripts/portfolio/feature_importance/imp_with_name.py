import os, sys, json
import numpy as np

# for scikit-learn forwards backwards rfe and rfecv

path = "../models/100_pickled_013/seq_first"
dirs = os.listdir( path )

name = sys.argv[1]
count = 0
imp_dict = dict()
for f in dirs: 
    if name in f:
        with open(os.path.join(path, f), "r") as json_file:
            count += 1
            s_data = json.load(json_file)["supported_f"]
            for key in s_data:
                if key in imp_dict:
                    imp_dict[key] += 1
                else:
                    imp_dict[key] = 0

avg_dict = dict()
for d in imp_dict:
    avg_dict[d] = imp_dict[d] / count

avg_data_i_sorted = list(reversed(sorted(avg_dict.items(),key= lambda x:x[1])))

def print_nice(data):
    print("key, value")
    for d in data:
        print(d[0],d[1], sep=",")

print_nice(avg_data_i_sorted[:5])