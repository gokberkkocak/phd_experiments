import optuna
from optuna.importance import get_param_importances
import argparse
import pandas as pd
from datetime import datetime
import traceback

import dat_to_essence_param
import miner_lite
import notify

VERSION = "0.1"

# dict with defaults
args = dict() 
args["input_file"] = "data/big/T10I4D100K.dat" 
args["item_limit"] = 500
args["sample_ratio"] = 0.01
args["fix_length"] = 0
args["mode"] = "c"
args["model"] = "models/hu_closed_cost_util_freqmining.eprime"
args["models"] = ["models/hu_closed_cost_util_freqmining.eprime", "models/hu_closed_cost_util_freqmining_exp_exp.eprime", "models/hu_closed_cost_util_freqmining_occ_explicit.eprime", "models/hu_closed_cost_util_freqmining_explicit_occ.eprime"]
args["freq"] = 1
args["solver_flag"] = "nbc"
args["rnd_seed"] = 1
args["info_location"] = "info-files_optuna/"
args["tmp_location"] = "tmp/"
args["cgroups_flag"] = False
args["o_flag"] = "O2"
args["save_flag"] = False
args["compress_doms"] = False
args["noblock_dom"] = False
args["sub_mdd"] = False
args["preproc"] = "SACBounds_limit"
args["interactive"] = True
args["flatten"] = "full"
args["native"] = False
args["optuna"] = None

# fixed util-cost func
util = [2,5,0,2,1,5,2,1,1,0,4,3,4,1,0,2,1,0,3,0,3,4,4,1,5,3,0,0,5,2,3,4,5,1,1,5,4,5,3,0,4,0,3,3,1,4,5,5,3,1,5,3,0,3,0,0,1,2,5,1,3,4,5,0,5,4,3,0,4,2,3,2,0,1,3,3,0,0,1,2,4,3,2,3,1,3,1,5,5,4,5,2,4,1,0,4,4,5,2,5,5,2,1,2,0,5,1,4,0,3,3,1,1,1,2,1,0,2,3,1,2,5,4,1,5,5,5,4,2,5,2,1,1,3,4,1,2,3,3,0,3,5,5,2,5,4,3,2,0,2,0,3,3,2,3,0,0,1,1,3,1,4,5,5,3,4,1,0,3,2,4,0,3,1,0,1,1,5,4,2,3,1,3,3,4,3,2,3,3,1,2,3,4,5,1,5,1,5,0,2,4,4,4,2,5,3,0,2,5,4,4,1,1,1,2,1,0,1,0,0,3,2,2,3,3,5,2,4,5,0,0,0,1,5,0,1,5,3,2,0,2,3,2,5,3,2,4,2,2,4,1,3,0,5,4,5,5,4,5,1,0,2,3,3,4,0,5,0,0,2,3,5,1,2,4,1,5,0,2,2,1,4,0,3,0,5,2,5,5,4,1,3,0,2,0,3,3,4,5,4,3,2,0,1,2,3,3,2,0,3,5,2,3,4,5,5,4,2,4,5,0,1,3,5,3,3,3,5,3,2,4,5,3,0,2,1,3,1,2,5,0,0,3,4,1,4,0,1,3,5,3,3,3,1,4,0,2,5,0,0,4,5,0,4,2,5,5,3,3,4,3,0,0,2,5,5,1,0,3,3,5,0,1,4,3,4,2,2,5,1,2,2,5,5,1,4,5,2,4,2,2,2,5,0,4,5,0,5,1,5,3,2,2,4,4,4,0,1,1,3,3,3,3,4,2,2,4,3,3,0,0,3,0,5,3,4,2,1,4,4,4,0,5,5,4,2,2,0,1,0,0,2,1,3,0,2,5,4,0,2,5,1,3,5,1,5,5,3,0,3,4,3,4,2,3,3,4,2,3,0,1,1,0,3,0,5,2,3,0,5,2,3,2,2,2,5,1,0,3,5]
cost = [4,4,4,3,1,5,4,2,3,0,1,5,0,2,4,2,2,0,0,4,0,4,3,4,5,4,4,2,5,2,0,0,1,4,1,5,3,1,3,0,1,0,2,4,3,5,0,4,1,1,0,3,1,3,1,3,2,1,3,3,3,0,3,5,4,1,5,3,2,4,0,2,0,2,1,3,0,5,2,1,2,0,4,2,3,3,0,4,0,1,1,1,1,4,3,0,2,0,2,1,3,4,4,5,1,1,1,4,0,4,5,4,5,1,3,1,5,3,0,1,0,3,5,5,5,1,4,0,3,0,2,3,3,3,2,1,2,4,5,3,2,4,4,5,1,0,4,5,5,2,0,0,5,1,1,0,0,2,3,5,4,4,2,1,5,3,2,0,5,3,5,5,2,5,0,1,5,1,1,4,3,1,5,2,4,0,0,4,3,1,5,0,2,3,2,1,0,1,5,2,3,4,3,5,2,3,5,1,4,4,3,4,0,5,0,3,0,5,0,4,0,5,5,4,4,4,1,1,2,0,1,1,5,5,0,3,3,3,5,3,5,1,1,1,2,3,3,4,4,5,1,2,2,5,3,1,4,5,0,4,3,1,0,2,2,1,2,0,3,3,3,1,3,3,2,5,2,3,1,0,1,0,0,2,3,4,0,1,4,3,2,4,5,3,5,4,0,4,0,3,0,1,4,3,2,1,3,4,4,1,3,3,5,2,2,1,2,1,2,1,3,0,5,2,5,0,0,4,4,3,5,3,5,0,5,4,4,5,1,3,2,2,1,0,4,0,1,1,1,5,5,2,2,0,1,1,2,2,3,5,0,0,1,1,1,3,4,0,2,4,5,2,4,3,3,5,5,0,1,5,1,0,5,4,1,4,5,2,5,4,3,3,5,3,5,3,0,2,0,3,5,4,2,2,0,5,1,0,5,4,1,5,3,0,4,3,3,1,3,1,5,3,1,5,5,1,1,1,0,4,0,0,4,3,5,4,1,5,2,2,2,5,2,1,1,4,4,3,0,5,0,0,3,2,5,1,4,2,2,5,2,0,5,4,4,3,1,4,5,0,2,1,3,1,0,0,3,2,3,5,4,4,2,2,4,2,4,1,0,3,3,2,4,5,1,4,0,3,3,5]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(VERSION))
    parser.add_argument('--solver', action='store_const',
                    dest='time', const="solver", default="solver", help='Use solver time for the optimisation function (default)')
    parser.add_argument('--sr', action='store_const',
                    dest='time', const="sr", default="solver", help='Use sr time for the optimisation function')
    parser.add_argument('--timeout', action='store',
                    dest='timeout', type=int, default=21600, help='Total tuning time (default: 21600)')
    parser.add_argument('--jobs', action='store',
                    dest='n_jobs', type=int, default=8, help='Parallel jobs (default: 8')
    parser.add_argument('--trials', action='store',
                    dest='n_trials', type=int, default=1000, help='Number of trials (default: 1000')                
    p_args = parser.parse_args()
    args["optuna"] = p_args.time
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=p_args.n_trials, n_jobs=p_args.n_jobs, timeout=p_args.timeout)
    trials_file = "trials_" + datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + ".csv"
    df = study.trials_dataframe()
    df.to_csv(trials_file)
    importance_dict = get_param_importances(study)
    print(importance_dict)
    notify.notify()

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def objective(trial):

    opt_args = dict()
    opt_args["util"] = []
    opt_args["cost"] = []
    for i in range(0,500):
        # u = trial.suggest_int("util_{}".format(i), 0, 5)
        opt_args["util"].append(util[i])
        # c = trial.suggest_int("cost_{}".format(i), 0, 5)
        opt_args["cost"].append(cost[i])
    opt_args["min_util"] = trial.suggest_int("min_util", 0, 100)
    opt_args["max_cost"] = trial.suggest_int("max_cost", 0, 100)

    d_args = dotdict(args)
    d_opt_args = dotdict(opt_args)
    output_file = dat_to_essence_param.instance_gen(d_args, d_opt_args)
    d_args.init_param = output_file
    # d_args.preproc = trial.suggest_categorical("preprocessing", ["SACBounds_limit", "GAC", "SSACBounds_limit"])
    try:
        info_file = miner_lite.solve(d_args)
        nb = -1
        with open(info_file, "r") as f:
            lines = f.readlines()
        for line in lines:
            if "Number of solutions" in line:
                if nb == -1:
                    nb = int(line.strip().split(":")[1])
            if "SolverNodes" in line:
                if "-1" in line:
                    nb = 0
            if "SolverTotalTime Sum" in line:
                solver_time = float(line.strip().split(":")[1])
            if "SavileRow Command time" in line:
                sr_total_time = float(line.strip().split(":")[1])
        if nb == 0:
            nb = float('inf')
        if d_args.optuna == "sr":
            return sr_total_time / float(nb)
        elif d_args.optuna == "solver":
            return solver_time / float(nb)
    except Exception: 
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    main()