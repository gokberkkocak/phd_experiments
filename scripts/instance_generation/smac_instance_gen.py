import logging
import traceback
from datetime import datetime

import numpy as np
from ConfigSpace.hyperparameters import UniformIntegerHyperparameter

# Import ConfigSpace and different types of parameters
from smac.configspace import ConfigurationSpace
from smac.facade.smac_hpo_facade import SMAC4HPO
# Import SMAC-utilities
from smac.scenario.scenario import Scenario

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
args["freq"] = 1
args["solver_flag"] = "nbc"
args["rnd_seed"] = 1
args["info_location"] = "info-files_smac/"
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
args["smac"] = "solver"

# fixed util-cost func
util = [2,5,0,2,1,5,2,1,1,0,4,3,4,1,0,2,1,0,3,0,3,4,4,1,5,3,0,0,5,2,3,4,5,1,1,5,4,5,3,0,4,0,3,3,1,4,5,5,3,1,5,3,0,3,0,0,1,2,5,1,3,4,5,0,5,4,3,0,4,2,3,2,0,1,3,3,0,0,1,2,4,3,2,3,1,3,1,5,5,4,5,2,4,1,0,4,4,5,2,5,5,2,1,2,0,5,1,4,0,3,3,1,1,1,2,1,0,2,3,1,2,5,4,1,5,5,5,4,2,5,2,1,1,3,4,1,2,3,3,0,3,5,5,2,5,4,3,2,0,2,0,3,3,2,3,0,0,1,1,3,1,4,5,5,3,4,1,0,3,2,4,0,3,1,0,1,1,5,4,2,3,1,3,3,4,3,2,3,3,1,2,3,4,5,1,5,1,5,0,2,4,4,4,2,5,3,0,2,5,4,4,1,1,1,2,1,0,1,0,0,3,2,2,3,3,5,2,4,5,0,0,0,1,5,0,1,5,3,2,0,2,3,2,5,3,2,4,2,2,4,1,3,0,5,4,5,5,4,5,1,0,2,3,3,4,0,5,0,0,2,3,5,1,2,4,1,5,0,2,2,1,4,0,3,0,5,2,5,5,4,1,3,0,2,0,3,3,4,5,4,3,2,0,1,2,3,3,2,0,3,5,2,3,4,5,5,4,2,4,5,0,1,3,5,3,3,3,5,3,2,4,5,3,0,2,1,3,1,2,5,0,0,3,4,1,4,0,1,3,5,3,3,3,1,4,0,2,5,0,0,4,5,0,4,2,5,5,3,3,4,3,0,0,2,5,5,1,0,3,3,5,0,1,4,3,4,2,2,5,1,2,2,5,5,1,4,5,2,4,2,2,2,5,0,4,5,0,5,1,5,3,2,2,4,4,4,0,1,1,3,3,3,3,4,2,2,4,3,3,0,0,3,0,5,3,4,2,1,4,4,4,0,5,5,4,2,2,0,1,0,0,2,1,3,0,2,5,4,0,2,5,1,3,5,1,5,5,3,0,3,4,3,4,2,3,3,4,2,3,0,1,1,0,3,0,5,2,3,0,5,2,3,2,2,2,5,1,0,3,5]
cost = [4,4,4,3,1,5,4,2,3,0,1,5,0,2,4,2,2,0,0,4,0,4,3,4,5,4,4,2,5,2,0,0,1,4,1,5,3,1,3,0,1,0,2,4,3,5,0,4,1,1,0,3,1,3,1,3,2,1,3,3,3,0,3,5,4,1,5,3,2,4,0,2,0,2,1,3,0,5,2,1,2,0,4,2,3,3,0,4,0,1,1,1,1,4,3,0,2,0,2,1,3,4,4,5,1,1,1,4,0,4,5,4,5,1,3,1,5,3,0,1,0,3,5,5,5,1,4,0,3,0,2,3,3,3,2,1,2,4,5,3,2,4,4,5,1,0,4,5,5,2,0,0,5,1,1,0,0,2,3,5,4,4,2,1,5,3,2,0,5,3,5,5,2,5,0,1,5,1,1,4,3,1,5,2,4,0,0,4,3,1,5,0,2,3,2,1,0,1,5,2,3,4,3,5,2,3,5,1,4,4,3,4,0,5,0,3,0,5,0,4,0,5,5,4,4,4,1,1,2,0,1,1,5,5,0,3,3,3,5,3,5,1,1,1,2,3,3,4,4,5,1,2,2,5,3,1,4,5,0,4,3,1,0,2,2,1,2,0,3,3,3,1,3,3,2,5,2,3,1,0,1,0,0,2,3,4,0,1,4,3,2,4,5,3,5,4,0,4,0,3,0,1,4,3,2,1,3,4,4,1,3,3,5,2,2,1,2,1,2,1,3,0,5,2,5,0,0,4,4,3,5,3,5,0,5,4,4,5,1,3,2,2,1,0,4,0,1,1,1,5,5,2,2,0,1,1,2,2,3,5,0,0,1,1,1,3,4,0,2,4,5,2,4,3,3,5,5,0,1,5,1,0,5,4,1,4,5,2,5,4,3,3,5,3,5,3,0,2,0,3,5,4,2,2,0,5,1,0,5,4,1,5,3,0,4,3,3,1,3,1,5,3,1,5,5,1,1,1,0,4,0,0,4,3,5,4,1,5,2,2,2,5,2,1,1,4,4,3,0,5,0,0,3,2,5,1,4,2,2,5,2,0,5,4,4,3,1,4,5,0,2,1,3,1,0,0,3,2,3,5,4,4,2,2,4,2,4,1,0,3,3,2,4,5,1,4,0,3,3,5]

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def objective(x):
    opt_args = dict()
    opt_args["util"] = []
    opt_args["cost"] = []
    for i in range(args["item_limit"]):
        opt_args["util"].append(util[i])
        opt_args["cost"].append(cost[i])
        # was generating here before, can rewrite
    opt_args["min_util"] = x["min_util"]
    opt_args["max_cost"] = x["max_cost"]

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
            if "SolverNodes" in line:
                if "-1" in line:
                    nb = 0
            if "SolverTotalTime Sum" in line:
                solver_time = float(line.strip().split(":")[1])
            if "SavileRow Command time" in line:
                sr_total_time = float(line.strip().split(":")[1])
        if d_args.smac == "sr":
            if nb == 0:
                return 2**32
            return -sr_total_time / float(nb)
        elif d_args.smac == "solver":
            if nb == 0:
                return 2**32
            return -solver_time / float(nb)
    except Exception: 
        traceback.print_exc()
        return 2**32

def main():
    logging.basicConfig(level=logging.INFO) 
    # Build Configuration Space which defines all parameters and their ranges
    cs = ConfigurationSpace()
    x0 = UniformIntegerHyperparameter("min_util", 0, 100, default_value=100)
    x1 = UniformIntegerHyperparameter("max_cost", 100, 800, default_value=100)
    cs.add_hyperparameters([x0, x1])

    # Scenario object
    scenario = Scenario({"run_obj": "quality",  # we optimize quality (alternatively runtime)
                        "runcount-limit": 20,  # max. number of function evaluations; for this example set to a low number
                        "cs": cs,  # configuration space
                        "deterministic": "true"
                        })

    # Example call of the function
    # It returns: Status, Cost, Runtime, Additional Infos
    # def_value = objective(cs.get_default_configuration())
    # print("Default Value: %.2f" % def_value)

    # Optimize, using a SMAC-object
    # print("Optimizing! Depending on your machine, this might take a few minutes.")
    smac = SMAC4HPO(scenario=scenario,
                    rng=np.random.RandomState(42),
                    tae_runner=objective)

    smac.optimize()
    notify.notify()

if __name__ == "__main__":
    main()