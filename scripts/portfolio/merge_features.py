import json

ef = "essence_features.json"
mf = "cheap_mining_features.json"

with open(ef, "r") as fw:
	ef_data = json.load(fw)

with open(mf, "r") as fw:
    mf_data = json.load(fw)

for i in ef_data:
	ef_data[i].update(mf_data[i])

with open("cmf+ef_features.json", "w") as f:
    json.dump(ef_data, f)
