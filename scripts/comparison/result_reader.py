import json
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats
import re
import random


def main():
    test()
    # if (len(sys.argv) < 2):
    #     sys.exit()
    # json_file = sys.argv[1]
    # results_file = sys.argv[2]
    # read_results_to_json(json_file, results_file)


def read_results_to_json(json_file, results_file):
    exps = []
    count = 0
    with open(results_file, "r") as f:
        lines = f.readlines()
    count = len(lines)
    for line in lines:
        res = json.loads(line)
        exps.append(res)
    process_all_old(exps, json_file)
    print("{} experiments processed".format(count))


def process_all_old(exps, json_file):
    tree_str = dict()
    for entry, value in exps:
        # model
        if "closed" in entry:
            model = "closed"
        elif "gen" in entry:
            model = "gen"
        elif "relevant" in entry:
            model = "rel_sub"
        elif "disc" in entry:
            model = "disc"
        elif "minimal" in entry:
            model = "min_rare"

        # instance
        instance = str(str(entry.split("__")[1]).split("_")[0:2])
        instance = re.sub("(\"|\'|\[|\])", "", instance)
        instance = instance.replace(", ", "_")
        if "extra" in entry:
            instance += "_" + str(str(entry.split("__")[1]).split("_")[2])
        # freq
        freq = float(instance.split("_")[-1])

        # config
        # representation
        if "_exp_exp" in entry:
            representation = "exp_exp"
        elif "_occ_exp" in entry:
            representation = "occ_exp"
        elif "_exp_occ" in entry:
            representation = "exp_occ"
        elif "_occ_occ" in entry:
            representation = "occ_occ"
        else:
            if model == "closed" or model == "gen":
                representation = "occ_occ"
            else:
                representation = "exp_occ"

        # preproc
        if "prec-" in entry:
            preproc = entry.split("_prec-")[1].split("-")[0]
        else:
            preproc = "SACBounds_limit"

        # solver
        if "minion" in entry:
            solver = "minion"
        elif "nbc" in entry:
            solver = "nbc"
        elif "glucose" in entry:
            solver = "glucose"
        elif "cadical" in entry:
            solver = "cadical"

        config_id = preproc + "_" + representation + "_" + solver + "_"

        # Incomp
        if "noincomp" in entry:
            incomp = False
            config_id += "0"

        else:
            incomp = True
            config_id += "1"
        # interactive
        if "interactive" in entry:
            interactive = True
            config_id += "1"
        else:
            interactive = False
            config_id += "0"

        # native
        if "native" in entry:
            native = True
            config_id += "1"
        else:
            native = False
            config_id += "0"
        # comp
        if "compress" in entry:
            compress = True
            config_id += "1"
        else:
            compress = False
            config_id += "0"
        # order
        if "order" in entry:
            order = True
            config_id += "1"
        else:
            order = False
            config_id += "0"
        # noblockdom
        if "noblock" in entry:
            noblock = True
            config_id += "1"
        else:
            noblock = False
            config_id += "0"
        # mdd
        if "mdd" in entry:
            mdd = True
            config_id += "1"
        else:
            mdd = False
            config_id += "0"
        
        #cgroups
        cgroups = True
        config_id += "1"

        experiment_id = model + "_" + instance + "_" + str(freq)
        if experiment_id not in tree_str:
            tree_str[experiment_id] = dict()
            tree_str[experiment_id]["model"] = model
            tree_str[experiment_id]["instance"] = instance
            tree_str[experiment_id]["freq"] = freq
            tree_str[experiment_id]["configs"] = dict()
        if config_id not in tree_str[experiment_id]["configs"]:
            tree_str[experiment_id]["configs"][config_id] = dict()
            tree_str[experiment_id]["configs"][config_id]["preprocess"] = preproc
            tree_str[experiment_id]["configs"][config_id]["representation"] = representation
            tree_str[experiment_id]["configs"][config_id]["solver"] = solver
            tree_str[experiment_id]["configs"][config_id]["incomparability"] = incomp
            tree_str[experiment_id]["configs"][config_id]["interactive"] = interactive
            tree_str[experiment_id]["configs"][config_id]["native"] = native
            tree_str[experiment_id]["configs"][config_id]["compressed"] = compress
            tree_str[experiment_id]["configs"][config_id]["ordered"] = order
            tree_str[experiment_id]["configs"][config_id]["no_solution_blocking"] = noblock
            tree_str[experiment_id]["configs"][config_id]["mdd"] = mdd
            tree_str[experiment_id]["configs"][config_id]["cgroups"] = cgroups
            tree_str[experiment_id]["configs"][config_id]["solve_information"] = []

        if not value["memout"] and "sols" in value and value["sols"] != 0 and "sr_time" in value and value["sr_time"] is not None and "solver_time" in value and value["solver_time"] is not None and "nodes-total" in value and value["nodes-total"] != 0 and value["nodes-total"] != 1 and value["nodes-total"] is not None:
            result = dict()
            total_solver_time = value["solver_time"]
            total_sr_time = value["sr_time"]
            total_nodes = value["nodes-total"]
            number_of_sols = value["sols"]
            seed = None
            if value["file_size"] == -1:
                file_size = None
            else:
                file_size = value["file_size"]
            memory_limit = 8 * 1024 * 1024
            time_limit = 6 * 60 *60 
            exit_type = "SUCCESS"
            machine_info = "eno_or_ferry"
            level = dict()
            # level_nodes
            if "nodes" in value and "-1" not in value["nodes"]:
                level_nodes = dict()
                t_dict = json.loads(value["nodes"])
                total_nodes = 0
                prev_level_sol = 0
                for i in t_dict:
                    total_nodes += int(float(t_dict[i]))
                    if interactive:
                        total_nodes -= prev_level_sol
                    level_nodes[i] = total_nodes - prev_level_sol
                    if interactive:
                        prev_level_sol = int(float(t_dict[i]))
                    else:
                        prev_level_sol = total_nodes
            else:
                level_nodes = None
            # level sols
            if "sollevel" in value and "-1" not in value["sollevel"]:
                t_value = re.sub("(\[|\])", "", value["sollevel"])
                t_dict = json.loads(t_value)
                error = False
                for key in t_dict:
                    t_dict[key] = int(float(t_dict[key]))
                    if t_dict[key] < 0 or t_dict[key] > 2**64-1:
                        error = True
                if t_dict and not error:
                    level_sols = t_dict
                else:
                    level_sols = None
            else:
                level_sols = None
            # level vars
            if "satv" in value and "-1" not in value["satv"]:
                t_value = re.sub("(|\[|\])", "", value["satv"])
                t_dict = json.loads(t_value)
                error = False
                for key in t_dict:
                    t_dict[key] = int(float(t_dict[key]))
                if t_dict:
                    level_vars = t_dict
                else:
                    level_vars = None
            else:
                level_vars = None
            # level clauses
            if "satc" in value and "-1" not in value["satc"]:
                t_value = re.sub("(\[|\])", "", value["satc"])
                t_dict = json.loads(t_value)
                error = False
                for key in t_dict:
                    t_dict[key] = int(float(t_dict[key]))
                    if t_dict[key] < 0 or t_dict[key] > 2**64-1:
                        error = True
                if t_dict and not error:
                    level_clauses = t_dict
                else:
                    level_clauses = None
            else:
                level_clauses = None
            # level learnt clauses
            if "satlc" in value and "-1" not in value["satlc"]:
                t_value = re.sub("(\[|\])", "", value["satlc"])
                t_dict = json.loads(t_value)
                error = False
                for key in t_dict:
                    t_dict[key] = int(float(t_dict[key]))
                    if t_dict[key] < 0 or t_dict[key] > 2**64-1:
                        error = True
                if t_dict and not error:
                    level_learnt_clauses = t_dict
                else:
                    level_learnt_clauses = None
            else:
               level_learnt_clauses = None
            # level solve time
            level_solve_time = None


            level["nodes"] = level_nodes
            level["cumulative_nb_solutions"] = level_sols
            level["nb_vars"] = level_vars
            level["nb_clauses"] = level_clauses
            level["nb_learnt_clauses"] = level_learnt_clauses
            level["solver_time"] = level_solve_time

            # result
            result["total_solver_time"] = total_solver_time
            result["total_sr_time"] = total_sr_time
            result["total_nodes"]= total_nodes
            result["nb_solutions"] = number_of_sols
            result["seed"] = seed
            result["file_size"] = file_size
            result["type"] = exit_type
            result["memory_limit"] = memory_limit
            result["time_limit"] = time_limit
            result["machine_info"] = machine_info
            result["level_info"] = level
            
            tree_str[experiment_id]["configs"][config_id]["solve_information"].append(result)

    # sanitise and remove wrong solution ones
    for exp in tree_str:
        exp_sols = -1
        sol_votes = dict()
        for config in tree_str[exp]["configs"]:
            for solve in tree_str[exp]["configs"][config]["solve_information"]:
                if solve["nb_solutions"] != 0 and solve["nb_solutions"] != 1 and tree_str[exp]["configs"][config]["incomparability"] == True:
                    if solve["nb_solutions"] in sol_votes:
                        sol_votes[solve["nb_solutions"]] += 1
                    else:
                        sol_votes[solve["nb_solutions"]] = 1
        max_votes = -1
        for votes in sol_votes:
            if max_votes < sol_votes[votes]:
                exp_sols = votes
                max_votes = sol_votes[votes] 

        # remove wrong sols
        for config in tree_str[exp]["configs"]:
            new_solve_info = []
            for solve in tree_str[exp]["configs"][config]["solve_information"]:
                if (solve["nb_solutions"] != 0 and solve["nb_solutions"] != 1 and solve["nb_solutions"] == exp_sols) or tree_str[exp]["configs"][config]["incomparability"] == False:
                    new_solve_info.append(solve)
            tree_str[exp]["configs"][config]["solve_information"] = new_solve_info
            
    experiment_store = dict()
    experiment_store["experiments"] = tree_str
    df = pd.DataFrame.from_dict(experiment_store)
    with open(json_file, "w") as f:
        df.to_json(f, indent=2)


def process_one_info_file(filepath):
    with open(filepath, "r") as f:
        lines = f.readlines()

    experiment = dict() # some oo would be nice but lazy to do that in python

    # model
    if "closed" in filepath:
        model = "closed"
    elif "gen" in filepath:
        model = "gen"
    elif "relevant" in filepath:
        model = "rel_sub"
    elif "disc" in filepath:
        model = "disc"
    elif "minimal" in filepath:
        model = "min_rare"
    experiment["model"] = model

    # instance
    instance = filepath.split("_f_")[0].split("/")[-1].split("__")[1]
    experiment["instance"] = instance
    # freq
    freq = float(filepath.split("_f_")[1].split("_")[0].replace("-","."))
    experiment["freq"] = freq

    if model != "rel_sub":
        experiment_id = model + "_" + instance + "_" + str(freq)
    else:
        experiment_id = model
        if "complete" in filepath:
            experiment_id += "_complete"
        elif "par_neg" in filepath:
            experiment_id += "_par_neg"
        elif "par_pos" in filepath:
            experiment_id += "_par_pos"   
        experiment_id += "_" + instance + "_" + str(freq)
    experiment["exp_id"] = experiment_id
    experiment["config"] = dict()
    # config
    # representation
    if "_exp_exp" in filepath:
        representation = "exp_exp"
    elif "_occ_exp" in filepath:
        representation = "occ_exp"
    elif "_exp_occ" in filepath:
        representation = "exp_occ"
    elif "_occ_occ" in filepath:
        representation = "occ_occ"
    else:
        if model == "closed" or model == "gen":
            representation = "occ_occ"
        else:
            representation = "exp_occ"
    if "_lia_" in filepath:
        representation += "_lia"
    elif "_nia_" in filepath:
        representation += "_nia"
    elif "_idl_" in filepath:
        representation += "_idl"  
    experiment["config"]["representation"] = representation
    # preproc
    for line in lines:
        if "SSACBounds_limit" in line:
            preproc = "SSACBounds_limit"
            break
        elif "SACBounds_limit" in line:
            preproc = "SACBounds_limit"
            break
        elif "GAC" in line:
            preproc = "GAC"
            break
        elif "-preprocess None" in line:
            preproc = "None"
            break
    else:
        preproc = "SACBounds_limit"
    experiment["config"]["preprocess"] = preproc

    # solver
    if "minion" in filepath:
        solver = "minion"
    elif "nbc" in filepath:
        solver = "nbc"
    elif "glucose" in filepath:
        solver = "glucose"
    elif "cadical" in filepath:
        solver = "cadical"
    elif "boolector" in filepath:
        solver = "boolector"
    elif "_z3_" in filepath:
        solver = "z3"
    elif "yices2" in filepath:
        solver = "yices2"
    experiment["config"]["solver"] = solver
    config_id = preproc + "_" + representation + "_" + solver + "_"

    # Incomp
    if "noincomp" in filepath:
        incomp = False
        config_id += "0"
    else:
        incomp = True
        config_id += "1"
    experiment["config"]["incomparability"] = incomp
    # interactive
    if "interactive" in filepath:
        interactive = True
        config_id += "1"
    else:
        interactive = False
        config_id += "0"
    experiment["config"]["interactive"] = interactive
    # native
    if "native" in filepath:
        native = True
        config_id += "1"
    else:
        native = False
        config_id += "0"
    experiment["config"]["native"] = native
    # comp
    if "compress" in filepath:
        compress = True
        config_id += "1"
    else:
        compress = False
        config_id += "0"
    experiment["config"]["compressed"] = compress
    # order
    if "order" in filepath:
        order = True
        config_id += "1"
    else:
        order = False
        config_id += "0"
    experiment["config"]["ordered"] = order
    # noblockdom
    if "noblock" in filepath:
        noblock = True
        config_id += "1"
    else:
        noblock = False
        config_id += "0"
    experiment["config"]["no_solution_blocking"] = noblock
    # mdd
    if "mdd" in filepath:
        mdd = True
        config_id += "1"
    else:
        mdd = False
        config_id += "0"
    experiment["config"]["mdd"] = mdd
    #cgroups
    for line in lines:
        if "cgroups" in line:
            cgroups = True
            config_id += "1"
            break
    else:
        cgroups = False
        config_id += "0"
    experiment["config"]["cgroups"] = cgroups

    experiment["config_id"] = config_id
    # result 
    result = dict()

    # exit code
    for line in lines:
        if "Exit status: 0" in line:
            exit_status = "SUCCESS"
            break
    for line in lines:
        if "Exception in thread" in line or "OutOfMemory" in line or "Killed" in line:
            exit_status = "MEMOUT"
            break
        elif "ERROR: Savile Row timed out." in line:
            exit_status = "TIMEOUT"
            break
        elif "Exit status:" in line:
            if "0" not in line:
                exit_status = "CRASHED"
        elif "Solution count has been reported differently" in line:
            exit_status = "DOUBTED"
            break
    result["type"] = exit_status


    # sols
    for line in lines:
        if "Number of solutions" in line and "None" not in line:
            sols = int(line.strip().split(": ")[1])
            break
    else:
        sols = None
    # SUCCESS CHECK
    if (result["type"] == "SUCCESS" or result["type"] == "DOUBTED") and sols is None:
        result["type"] = "CRASHED"
        print("LOG: Something is wrong with this experiment. Considering crash.")
    elif result["type"] == "SUCCESS" or result["type"] == "DOUBTED":
        result["nb_solutions"] = sols

    # solver time
    for line in lines:
        if "SolverTotalTime" in line and "None" not in line:
            total_solver_time = float(line.strip().split(": ")[1])
            break
    else:
        total_solver_time = None
    result["type"] == "SUCCESS"
    # SUCCESS CHECK
    if (result["type"] == "SUCCESS" or result["type"] == "DOUBTED") and sols is None:
        result["type"] = "CRASHED"
        print("LOG: Something is wrong with this experiment. Considering crash.")
    elif result["type"] == "SUCCESS" or result["type"] == "DOUBTED":
        result["total_solver_time"] = total_solver_time

    # sr time
    for line in lines:
        if "SavileRow Command time" in line and "None" not in line:
            total_sr_time = float(line.strip().split(": ")[1])
            break
    else:
        total_sr_time = None
    # SUCCESS CHECK
    if (result["type"] == "SUCCESS" or result["type"] == "DOUBTED") and sols is None:
        result["type"] = "CRASHED"
        print("LOG: Something is wrong with this experiment. Considering crash.")
    elif result["type"] == "SUCCESS" or result["type"] == "DOUBTED":
        result["total_sr_time"] = total_sr_time

    # total nodes
    for line in lines:
        if "SolverNodesTotal" in line and "None" not in line and "-1" not in line:
            total_nodes = int(float(line.strip().replace("\'", "\"").split("SolverNodesTotal :")[1]))
            break
    else:
        total_nodes = None
    # SUCCESS CHECK
    if (result["type"] == "SUCCESS" or result["type"] == "DOUBTED") and sols is None:
        result["type"] = "CRASHED"
        print("LOG: Something is wrong with this experiment. Considering crash.")
    elif result["type"] == "SUCCESS" or result["type"] == "DOUBTED":
        result["total_nodes"] = total_nodes

    # file size
    for line in lines:
        if "Dimacs file size:" in line or "Minion file size: " in line or "SMT file size:" in line:
            file_size = int(line.strip().split("size: ")[1].split(" ")[0])
            break
    else:
        file_size = None
    result["file_size"] = file_size
    
    # seed 
    for line in lines:
        if interactive and "seed=" in line and "Command being timed" not in line:
            seed = float(line.strip().split("seed=")[1].split("\"")[0])
            break
        elif not interactive and (solver == "glucose" or solver == "cadical") and "seed=" in line:
            seed = float(line.strip().split("seed=")[1].split("\"")[0])
            break
        elif not interactive and solver == "nbc" and " -r " in line:
            seed = float(line.strip().split(" -r ")[1].split(" ")[0])
            break
        elif "-smt-seed" in line:
            seed = float(line.strip().split("-smt-seed ")[1].split(" ")[0])
            break
    else:
        seed = None
    result["seed"] = seed

    # time_limit
    for line in lines:
        if "-timelimit" in line:
            timelimit = int(float(line.strip().split("-timelimit ")[1].split(" ")[0]))
            break
        elif "timeout " in line:
            timelimit = int(float(line.strip().split("timeout ")[1].split(" ")[0]))
            break
    else:
        timelimit = None
    result["time_limit"] = timelimit

    # mem_limit hack
    with open(os.path.join(os.getenv("HOME"),".local/bin/savilerow"), "r") as f:
        s_lines = f.readlines()
    for s_line in s_lines:
        if "Xmx" in s_line:
            memlimit = s_line.strip().split("-Xmx")[1].split(" ")[0]
            if memlimit[-1] == "G":
                memlimit = int(memlimit[:-1]) * 1024 * 1024
            break
    else:
        memlimit = None
    result["memory_limit"] = memlimit

    if result["type"] == "MEMOUT" or result["type"] == "CRASHED":
        for line in lines:
            if "Script Total Time" in line:
                crash_time = float(line.strip().split(": ")[1])
                break
        else:
            crash_time = None
        result["crash_time"] = crash_time

    machine_info = os.uname()[1]
    # machine_info = os.uname().nodename
    result["machine_info"] = machine_info
    if result["type"] == "SUCCESS" or result["type"] == "DOUBTED":
        # explode freq itemsets
        for line in lines:
            if "Number of frequent solutions" in line and "None" not in line:
                nb_freq_sols = int(line.strip().split(": ")[1])
                break
        else:
            nb_freq_sols = None
        result["freq_nb_solutions"] = nb_freq_sols

        result["level_info"] = dict()
        # level
        # nodes
        for line in lines:
            if "SolverNodes" in line and "SolverNodesTotal" not in line:
                nodes = line.strip().replace("\'", "\"").split("SolverNodes :")[1]
                nodes = re.sub("(\[|\])", "", nodes)
                level_nodes = json.loads(nodes)
                for key in level_nodes:
                    level_nodes[key] = int(float(level_nodes[key]))
                break
        else:
            level_nodes = None
        result["level_info"]["nodes"] = level_nodes
        #vars
        for line in lines:
            if "SATVars" in line:
                vars = line.strip().replace("\'", "\"").split("SATVars :")[1]
                vars = re.sub("(\[|\])", "", vars)
                level_vars = json.loads(vars)
                for key in level_vars:
                    level_vars[key] = int(float(level_vars[key]))
                break
        else:
            level_vars = None
        result["level_info"]["nb_vars"] = level_vars
        # clauses
        for line in lines:
            if "SATClauses" in line:
                clauses = line.strip().replace("\'", "\"").split("SATClauses :")[1]
                clauses = re.sub("(\[|\])", "", clauses)
                level_clauses = json.loads(clauses)
                for key in level_clauses:
                    level_clauses[key] = int(float(level_clauses[key]))
                break
        else:
            level_clauses = None
        result["level_info"]["nb_clauses"] = level_clauses
        # learnt clauses
        for line in lines:
            if "SATLearntClauses" in line:
                learnt_clauses = line.strip().replace("\'", "\"").split("SATLearntClauses :")[1]
                learnt_clauses = re.sub("(\[|\])", "", learnt_clauses)
                level_learnt_clauses = json.loads(learnt_clauses)
                for key in level_learnt_clauses:
                    level_learnt_clauses[key] = int(float(level_learnt_clauses[key]))
                break
        else:
            level_learnt_clauses = None
        result["level_info"]["nb_learnt_clauses"] = level_learnt_clauses
        # solution by level
        for line in lines:
            if "SolutionsByLevel" in line:
                cumulative_sols = line.strip().replace("\'", "\"").split("SolutionsByLevel :")[1]
                cumulative_sols = re.sub("(\[|\])", "", cumulative_sols)
                level_cumulative_sols = json.loads(cumulative_sols)
                for key in level_cumulative_sols:
                    level_cumulative_sols[key] = int(float(level_cumulative_sols[key]))
                break
        else:
            level_cumulative_sols = None
        result["level_info"]["cumulative_nb_solutions"] = level_cumulative_sols
        # solver time by level
        for line in lines:
            if "SolverTimeByLevel" in line:
                level_solver_time = line.strip().replace("\'", "\"").split("SolverTimeByLevel :")[1]
                level_solver_time = re.sub("(\[|\])", "", level_solver_time)
                level_solver_time = json.loads(level_solver_time)
                for key in level_solver_time:
                    level_solver_time[key] = float(level_solver_time[key])
                break
        else:
            level_solver_time = None
        result["level_info"]["solver_time"] = level_solver_time


    experiment["config"]["solve_information"] = [result]
    return experiment

if __name__ == '__main__':
    main()
