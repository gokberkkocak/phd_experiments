import os
import sys
import json


mode = int(sys.argv[1])

mode_str = "fw" if mode == 0 else "bw"

print(mode_str)

# Open a file
path = "../models"
files = os.listdir(path)
count = 0


imp_dict = dict()


for f in files:
    if f.endswith(".json") and mode_str in f and "e1" not in f:
        # print(f)
        with open(path + "/" + f) as json_file:
            count += 1
            data = json.load(json_file)
            if mode_str == "fw":
                data = data[1:6]
            else :
                data = data[-6:]
            for tuple in data:
                if tuple[0] not in imp_dict:
                    imp_dict[tuple[0]] = 0
                imp_dict[tuple[0]] += 1


avg_dict = dict()
for d in imp_dict:
    avg_dict[d] = imp_dict[d] #/ count

print("count: ", count)

avg_data_i_sorted = list(
    reversed(sorted(avg_dict.items(), key=lambda x: x[1])))


def print_nice(data):
    print("key, value")
    for d in data:
        print(d[0], d[1], sep=",")


print_nice(avg_data_i_sorted[:5])
