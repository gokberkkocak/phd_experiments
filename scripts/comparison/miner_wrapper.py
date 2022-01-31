#!/usr/bin/env python3

import sys
import traceback
import random

import miner_lite

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def main():
    script = sys.argv[0]
    instance_file = sys.argv[1]
    line_number = int(sys.argv[2])
    with open(instance_file, "r") as f:
        lines = f.readlines()
    if line_number >= len(lines):
        print("out of lines")
        sys.exit(0)
    instance = lines[line_number].strip()
    config_number = int(sys.argv[3])
    # solver 0..1 ac 0..3 model 0..3
    # use base 4 
    seed = random.randint(0,100)
    # dict with defaults
    args = dict()
    if config_number >= 192:
        model = 1
        solver = 0
        ac = 0
        args["interactive"] = False
    else:
        model = config_number % 4
        ac = int(config_number/4) % 4
        solver = int(config_number/16)
        args["interactive"] = True
    print("TESTING instance_no:{}, solver:{}, ac:{}, model:{}".format(line_number, solver, ac, model))
    args["init_param"] = instance
    if "data/gen" in instance:
        base_model = "hu_gen_fis"
        args["mode"] = "c"
    elif "data/cost" in instance:
        base_model = "hu_closed_cost_util_freqmining"
        args["mode"] = "c"
    elif "data/rare" in instance:
        base_model = "hu_minimal_rare_fis"
        args["mode"] = "r"
    elif "data/dis" in instance:
        base_model = "hu_disc_mining_modded"
        args["mode"] = "d"
    elif "data/rel" in instance:
        base_model = "relevant_subgroups_modded"
        args["mode"] = "d"
    if model == 0:
        if args["mode"] == "c":
            args["model"] = "models/"+base_model+"_exp_occ"
        else:
            args["model"] = "models/"+base_model
    elif model == 1:
        args["model"] = "models/"+base_model+"_exp_exp"
    elif model == 2:
        args["model"] = "models/"+base_model+"_occ_exp"
    elif model == 3:
        if args["mode"] == "c":
            args["model"] = "models/"+base_model
        else:
            args["model"] = "models/"+base_model+"_occ_occ"
    # for rsd model variations
    if "data/rel" in instance:
        try:
            incomp_flag = int(sys.argv[4])
        except:
            incomp_flag = 0
        if incomp_flag == 1:
            args["model"] += "_complete"
        if incomp_flag == 2:
            args["model"] += "_par_pos"
        if incomp_flag == 3:
            args["model"] += "_par_neg"
    args["model"] += ".eprime"    
    args["freq"] = int(instance.split("/")[-1].split(".param")[0].split("_")[-1])
    if solver == 0:
        args["solver_flag"] = "nbc"
    elif solver == 1:
        args["solver_flag"] = "glucose"
    elif solver == 2:
        args["solver_flag"] = "cadical"
    elif solver == 3:
        args["solver_flag"] = "z3"
        args["smt_logic"] = "bv"
    elif solver == 4:
        args["solver_flag"] = "boolector"      
        args["smt_logic"] = "bv"  
    elif solver == 5:
        args["solver_flag"] = "yices2"    
        args["smt_logic"] = "bv"
    elif solver == 6:
        args["solver_flag"] = "z3"    
        args["smt_logic"] = "lia"
    elif solver == 7:
        args["solver_flag"] = "yices2"    
        args["smt_logic"] = "lia"
    elif solver == 8:
        args["solver_flag"] = "z3"    
        args["smt_logic"] = "nia"
    elif solver == 9:
        args["solver_flag"] = "z3"    
        args["smt_logic"] = "idl"
    elif solver == 10:
        args["solver_flag"] = "yices2"    
        args["smt_logic"] = "idl"
    elif solver == 11:
        args["solver_flag"] = "minion"    
    args["rnd_seed"] = seed
    args["info_location"] = "info-files_smac/"
    args["tmp_location"] = "tmp/"
    args["cgroups_flag"] = True
    args["o_flag"] = "O2"
    args["save_flag"] = False
    args["compress_doms"] = False
    args["noblock_dom"] = False
    args["sub_mdd"] = False
    if ac == 0:
        args["preproc"] = "SACBounds_limit"
    elif ac == 1:
        args["preproc"] = "GAC"
    elif ac == 2:
        args["preproc"] = "SSACBounds_limit"
    elif ac == 3:
        args["preproc"] = "None"
    args["flatten"] = "full"
    args["native"] = False
    args["optuna"] = None
    args["results_file"] = "result_dump.json"
    args["dynamic_t"] = "mariadb.cfg"
    args["commit"] = True
    args["conjure_bin"] = "conjure-dominance"
    d_args = dotdict(args)
    nb_success = miner_lite.read_db_and_check_enough(d_args)
    # if we have more than n success don't run
    MIN_WANTED = 3
    if nb_success >= MIN_WANTED:
        sys.exit(0)
    APPLY_TIMEOUT = True
    if APPLY_TIMEOUT:
        proposed_timeout = miner_lite.read_db_and_get_timeout(d_args)
        print("Proposed timeout: {}".format(proposed_timeout))
        value, t = miner_lite.read_db_and_get_exact(d_args)
        print(value)
        # if we already run this and got timeout.
        if value >= proposed_timeout and "TIMEOUT" in t:
            print("")
            sys.exit(0)
        args["timeout"] = proposed_timeout
    else:
        args["timeout"] = 21600
    d_args = dotdict(args)
    # run a couple of times
    run_n_times = MIN_WANTED - nb_success
    for _ in range(run_n_times):
        try:
            info_file = miner_lite.solve(d_args)
            seed = random.randint(0,100)
            args["rnd_seed"] = seed
            d_args = dotdict(args)
        except Exception: 
            traceback.print_exc()


if __name__ == "__main__":
    main()