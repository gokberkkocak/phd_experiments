import sys
import numpy as np
import pandas as pd

import json

from competitive import comp_winners

# with open(sys.argv[1], 'r') as f:
#     lines = f.readlines()

# names = lines[0].strip().split(",")
# names = names[1:]

df = pd.read_csv(sys.argv[1], index_col=0)
comp_count = comp_winners(sys.argv[1])
dominated_dict = dict()
for i in df:
    for j in df:
        if i != j and comp_count[i] >= comp_count[j]:
            count = 0
            for k in range(len(df[i])):
                if df[i][k] == 1 and df[j][k] == 1:
                    count += 1
            if j not in dominated_dict:
                dominated_dict[j] = dict()
            dominated_dict[j][i] = count / comp_count[j]

# import json
# print(json.dumps(dominated_dict))
df = pd.DataFrame(dominated_dict)
df.to_csv(sys.argv[1].split(".")[0]+"_domination.csv")

# remove full dominated
to_remove = set()
for i in dominated_dict:
    for j in dominated_dict[i]:
        if dominated_dict[i][j] == 1:
            to_remove.add(i)

for i in to_remove:
    dominated_dict.pop(i)
    for j in dominated_dict:
        if i in dominated_dict[j]:
            dominated_dict[j].pop(i)

df = pd.DataFrame(dominated_dict)
df.to_csv(sys.argv[1].split(".")[0]+"_domination_removed.csv")
