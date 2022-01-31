import json
import sys

filename = sys.argv[1]
with open(filename, "r") as f:
    data = json.load(f)

print("exp, n_g_u, i_g_u, chuffed, openwbo")
for exp in data:
    print(exp, data[exp]["normal_unsat_glucose"]["solver_time"], data[exp]["inter_unsat_glucose"]
          ["solver_time"], data[exp]["chuffed"]["solver_time"], data[exp]["openwbo_glucose"]["solver_time"], sep=",")
