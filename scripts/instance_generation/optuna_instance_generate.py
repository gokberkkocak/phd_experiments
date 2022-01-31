import optuna
import sys
from optuna.importance import get_param_importances
import argparse
import pandas as pd
from datetime import datetime
import traceback

import dat_to_essence_param
import miner_lite
import notify
import random
import json
import os

VERSION = "0.1"

# dict with defaults
args = dict() 
args["mode"] = "c"
args["item_limit"] = 500
args["sample_ratio"] = 0
args["fix_length"] = 0
args["model"] = "models/relevant_subgroups_modded_occ_occ.eprime"
args["solver_flag"] = "yices2"
args["smt_logic"] = "lia"
args["rnd_seed"] = 1
args["info_location"] = "info-files_optuna_gen/"
args["tmp_location"] = "tmp/"
args["cgroups_flag"] = True
args["o_flag"] = "O1"
args["save_flag"] = False
args["compress_doms"] = False
args["noblock_dom"] = False
args["sub_mdd"] = False
args["preproc"] = "GAC"
args["interactive"] = True
args["flatten"] = "full"
args["native"] = False
args["optuna"] = None
args["conjure_bin"] = "conjure-dominance"
args["freq"] = 15
args["timeout"] = 10800
args["disc"] = True

opt_args = dict()
opt_args["util"] = []
opt_args["cost"] = []
for i in range(0,200):
    opt_args["util"].append(random.randint(0, 5))
    opt_args["cost"].append(random.randint(0, 5))

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--version', action='version',
    #                     version='%(prog)s {}'.format(VERSION))
    # parser.add_argument('--timeout', action='store',
    #                 dest='timeout', type=int, default=21600, help='Total tuning time (default: 21600)')
    # parser.add_argument('--jobs', action='store',
    #                 dest='n_jobs', type=int, default=4, help='Parallel jobs (default: 4')
    # parser.add_argument('--trials', action='store',
    #                 dest='n_trials', type=int, default=100, help='Number of trials (default: 1000')   

    files = [
        "data/optuna/anneal.dat", # 0
        "data/optuna/audio.dat",
        "data/optuna/aus.dat",
        "data/optuna/german.dat",
        "data/optuna/heart.dat",
        "data/optuna/hepatit.dat", # 5
        "data/optuna/hypo.dat",
        "data/optuna/krvskp.dat",
        "data/optuna/lymph.dat",
        "data/optuna/tumor.dat",
        "data/optuna/vote.dat", # 10
        "data/optuna/zoo.dat",
        "data/optuna/mushroom.dat"
    ]

    args["input_file"] = files[int(sys.argv[1])]
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=20, n_jobs=2, timeout=21600)
    if study.best_value > 0:
        write_final_instance(study)
    # notify.notify()

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def objective(trial):
    opt_args["min_util"] = trial.suggest_int("min_util", 0, 15)
    opt_args["max_cost"] = trial.suggest_int("max_cost", 0, 15)
    d_args = dotdict(args)
    d_opt_args = dotdict(opt_args)
    output_file = dat_to_essence_param.instance_gen(d_args, d_opt_args)
    d_args.init_param = output_file

    try:
        info_file = miner_lite.solve(d_args)
        nb = -1
        with open(info_file, "r") as f:
            lines = f.readlines()
        for line in lines:
            if "Number of solutions" in line:
                if nb == -1:
                    nb = int(line.strip().split(":")[1])
            if "SavileRow Command time" in line:
                sr_total_time = float(line.strip().split(":")[1])
        objective = 0
        if nb > 1 and nb < 1000:
            objective = 10000
        elif nb >= 1000 and nb < 10000:
            objective = 4000
        if nb > 1:
            objective += sr_total_time / float(nb)
        return objective
    except Exception: 
        traceback.print_exc()
        return 0

def write_final_instance(study):
    df = study.trials_dataframe()
    best_params = study.best_params
    importance_dict = get_param_importances(study)

    instance = args["input_file"].split("/")[-1].split(".")[0]
    folder = "data/optuna/final/" + instance + "/"
    os.makedirs(folder, exist_ok=True)
    seed = str(random.randint(0, 50000))
    final_filename = folder + args["model"].split("/")[-1][0] + "_" + seed 
    opt_args["min_util"] = best_params["min_util"]
    opt_args["max_cost"] = best_params["max_cost"]
    d_args = dotdict(args)
    d_opt_args = dotdict(opt_args)
    output_file = dat_to_essence_param.instance_gen(d_args, d_opt_args)
    os.rename(output_file, final_filename +".param")
    df.to_json(final_filename + ".json")
    with open(final_filename + "_imp.json", "w") as f:
        json.dump(importance_dict, f)

if __name__ == "__main__":
    main()