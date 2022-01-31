#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import math
import miner_lite as miner
import json
import random

miner_command = "python3 scripts/miner_lite.py c {} {} {}"

def main():
    if len(sys.argv) < 4:
        sys.exit()
    model = sys.argv[1]
    init_param = sys.argv[2]
    freq = int(sys.argv[3])
    density = int(sys.argv[4])
    utils, costs = read_util_cost(init_param)
    min_util_ub, max_cost_ub = get_ub_values(utils, costs, freq, init_param)
    create_params(init_param, model, freq, min_util_ub, max_cost_ub, density)

def read_util_cost(init_param):
    with open(init_param, "r") as f:
        lines = f.readlines()
    for line in lines:
        if "letting utility_values" in line:
            utils = [ int(a) for a in line[:-1].split("be [")[1].split(";")[0].split(", ")] 
        elif "letting cost_values" in line:
            costs = [ int(a) for a in line[:-1].split("be [")[1].split(";")[0].split(", ")]
    return utils, costs


def get_ub_values(utils, costs, freq, init_param):
    nb_items = len(utils)
    sum_utils = sum(utils)
    sum_costs = sum(costs)
    size, temp = miner.get_start_size_from_eclat(freq, init_param)
    if size == -1:
        size = miner.get_max_row_card(init_param)
    max_cost_ub = math.ceil(size/nb_items * sum_costs) + 10
    min_util_ub = math.ceil(size/nb_items * sum_utils) + 10
    print("Util bound {} and Cost bound {}".format(min_util_ub, max_cost_ub))
    return min_util_ub, max_cost_ub

def create_params(init_param, model, freq, min_util_ub, max_cost_ub, density):
    instance_counter = 0
    params = []
    lines = []
    for u in range(0, min_util_ub, density):
        for c in range(0, max_cost_ub, density):
            new_param = create_param(init_param, u, c, instance_counter)
            new_exp = {"id" : instance_counter, "util" : u, "cost" : c, "param" : new_param }
            params.append(new_exp)
            instance_counter += 1
            command = miner_command.format(model, new_param, freq) + "\n"
            lines.append(command)
    print("{} instances created for testing".format(instance_counter))
    json_file = "experiment_{}.json".format(os.getpid())
    with open(json_file, "w") as f:
        json.dump(params, f, indent=1)
    print("Experiments dumped in {}".format(json_file))
    txt_file = "experiment_{}.txt".format(os.getpid())
    with open(txt_file, "w") as f:
        random.shuffle(lines)
        f.writelines(lines)
    print("Experiments ready in {}".format(txt_file))
    

def create_param(init_param, util, cost, nb):
    with open(init_param, "r") as f:
        lines = f.readlines()
    new_param = init_param.split(".")[0] + "_{}{}".format(nb, miner.essence_suffix) 
    with open(new_param, "w") as f:
        f.writelines(lines)
        f.write("letting min_utility be {}\n".format(util))
        f.write("letting max_cost be {}\n".format(cost))
    return new_param

if __name__ == '__main__':
    main()