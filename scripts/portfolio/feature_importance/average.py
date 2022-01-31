import os, sys, json

# fanova

# Open a file
path = "100"
dirs = os.listdir( path )

count = 0
data = dict()
data["individual"] = dict()
data["pairwise"] = dict()

for file in dirs:
   with open(os.path.join(path, file), "r") as json_file:
        count += 1
        s_data = json.load(json_file)
        for key in s_data["individual"]:
            if key not in data["individual"]:
                data["individual"][key] = []
            data["individual"][key].append(s_data["individual"][key]["individual importance"])
        for p_data in s_data["pairwise"]:
            pairs = p_data["pair"]
            pairs.sort()
            pair_key = str(pairs[0]) + "-" + str(pairs[1])
            if pair_key not in data["pairwise"]:
                data["pairwise"][pair_key] = []
            data["pairwise"][pair_key].append(p_data["importance"])
            
# print(data)

avg_data = dict()
avg_data["individual"] = dict()
avg_data["pairwise"] = dict()

for d in data["individual"]:
    avg_data["individual"][d] = sum(data["individual"][d]) / count

for d in data["pairwise"]:
    avg_data["pairwise"][d] = sum(data["pairwise"][d]) / count


def print_nice(data):
    print("key value")
    for d in data:
        print(d[0],d[1])

avg_data_i_sorted = list(reversed(sorted(avg_data["individual"].items(),key= lambda x:x[1])))
print_nice(avg_data_i_sorted[:5])

avg_data_p_sorted = list(reversed(sorted(avg_data["pairwise"].items(),key= lambda x:x[1])))
print_nice(avg_data_p_sorted[:5])
