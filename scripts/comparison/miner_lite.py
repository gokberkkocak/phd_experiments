#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
import time
import json
import random
import shlex
import fcntl
import result_reader

VERSION = "0.98.2"  # add smt support with different logic

eclat_timeout = 180
eclat_memory_limit = 15*1024*1024
freq_str = "letting min_freq be {}\n"
eclat_size_command = "eclat -tm -s{} -Z {}"
timeout_command = "timeout_perl -t {} -m {} "
conjure_trans_param_command = "{} translate-param --eprime={} --essence-param={} --eprime-param={} --line-width=2500"
savilerow_native = "savilerow-native"
savilerow_jar = "savilerow"
savilerow_command = "/usr/bin/time -v {} {} {} -run-solver -solutions-to-stdout-one-line -preprocess {} -S0 -dom-flatten-strategy {}"
sat_suffix = " -sat -out-sat {} -sat-family {} -solver-options {}"
# second argument for choosing the smt solver
smt_suffix = " -smt -out-smt {} -{} -boolector-bin boolector -z3-bin z3 -yices2-bin yices-smt2 -smt-seed {}"
smt_lia_suffix = " -smt-lia"
smt_nia_suffix = " -smt-nia"
smt_idl_suffix = " -smt-idl"
interactive_suffix = " -interactive-solver"
one_sol_suffix = " -num-solutions 1"
timelimit_prefix = "timeout {} "
minion_suffix = " -minion -out-minion {} -solver-options \"-varorder static\""
info_suffix = " -out-info {}"
cgroups_suffix = " -cgroups"
mkdir_command = "mkdir -p {}"
rm_command = "rm -rf {}"
essence_suffix = ".param"
eprime_suffix = ".eprime-param"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(VERSION))
    parser.add_argument('--mode', action='store',
                        dest='mode', help='Mode (c ar d r)')
    parser.add_argument('--model', action='store',
                        dest='model', help='Eprime model')
    parser.add_argument('--init-param', action='store',
                        dest='init_param', help='Init param')
    parser.add_argument('--freq', action='store',
                        dest='freq', type=float, help='Freq')
    parser.add_argument('--minion', action='store_const', dest='solver_flag',
                        default='nbc', const='minion', help='Use minion')
    parser.add_argument('--glucose', action='store_const', dest='solver_flag',
                        default='nbc', const='glucose', help='Use glucose')
    parser.add_argument('--nbc', action='store_const', dest='solver_flag',
                        default='nbc', const='nbc', help='Use nbc')
    parser.add_argument('--cadical', action='store_const', dest='solver_flag',
                        default='nbc', const='cadical', help='Use cadical')
    parser.add_argument('--yices2', action='store_const', dest='solver_flag',
                        default='nbc', const='yices2', help='Use yices2')
    parser.add_argument('--z3', action='store_const', dest='solver_flag',
                        default='nbc', const='z3', help='Use z3')
    parser.add_argument('--boolector', action='store_const', dest='solver_flag',
                        default='nbc', const='boolector', help='Use boolector')
    parser.add_argument('--rnd-seed', action='store', dest='rnd_seed',
                        type=int, default=0, help='Random seed for sat, default 0')
    parser.add_argument('--info', action='store', dest='info_location',
                        default='info-files/', help='Info file location, default info-files')
    parser.add_argument('--tmp', action='store', dest='tmp_location',
                        default='tmp/', help='Info file location, default tmp')
    parser.add_argument('--compress-doms', action='store_true', dest='compress_doms',
                        default=False, help='Compress dominance constraints when incomp is available')
    parser.add_argument('--interactive', action='store_true', dest='interactive',
                        default=False, help='Interactive SAT solver usage')
    parser.add_argument('--native', action='store_true', dest='native',
                        default=False, help='Use native compiled SavileRow')
    parser.add_argument('--flatten-strategy', action='store',
                        dest='flatten', default="full", help='Dominance flatten strategy: full(default), semi, basic')
    parser.add_argument('--noblock-dom', action='store_true', dest='noblock_dom',
                        default=False, help='Glucose gets dom nogoods instead of sol block directly')
    parser.add_argument('--cgroups', action='store_true',
                        dest='cgroups_flag', default=False, help='Use Cgroups')
    parser.add_argument('--save-solutions', action='store_true',
                        dest='save_flag', default=False, help='Save solutions to JSON')
    parser.add_argument('--O0', action='store_const',
                        dest='o_flag', default='O2', const='O0', help='Use 00')
    parser.add_argument('--O1', action='store_const',
                        dest='o_flag', default='O2', const='O1', help='Use 01')
    parser.add_argument('--O2', action='store_const',
                        dest='o_flag', default='O2', const='O2', help='Use O2')
    parser.add_argument('--gac', action='store_const',
                        dest='preproc', default='SACBounds_limit', const='GAC', help='Use GAC')
    parser.add_argument('--sac', action='store_const',
                        dest='preproc', default='SACBounds_limit', const='SAC_limit', help='Use SAC_limit')
    parser.add_argument('--ssac', action='store_const',
                        dest='preproc', default='SACBounds_limit', const='SSAC_limit', help='Use SSAC_limit')
    parser.add_argument('--sac-bounds', action='store_const',
                        dest='preproc', default='SACBounds_limit', const='SACBounds_limit', help='Use SACBounds_limit (default)')
    parser.add_argument('--ssac-bounds', action='store_const',
                        dest='preproc', default='SACBounds_limit', const='SSACBounds_limit', help='Use SSACBounds_limit')
    parser.add_argument('--no-preproc', action='store_const',
                        dest='preproc', default='SACBounds_limit', const='None', help='Use None preprocessing')
    parser.add_argument('--smt-bv', action='store_const',
                        dest='smt_logic', default='bv', const='bv', help='Use smt-bv logic (default)')
    parser.add_argument('--smt-lia', action='store_const',
                        dest='smt_logic', default='bv', const='lia', help='Use smt-lia logic')
    parser.add_argument('--smt-nia', action='store_const',
                        dest='smt_logic', default='bv', const='nia', help='Use smt-nia logic')
    parser.add_argument('--smt-idl', action='store_const',
                        dest='smt_logic', default='bv', const='idl', help='Use smt-idl logic')
    parser.add_argument("--one-solution", action='store_true',
                        dest="one_sol", default=False, help="Find only one solution (might not work/might only work on interactive)")
    parser.add_argument("--timelimit", action='store',
                        dest="timeout", default=None, help="Supply timeout")
    parser.add_argument("--dynamic-timeout", action='store',
                        dest="dynamic_t", default=None, help="Supply json file (.json) or db config (.cfg) for dynamic timeout application. Miner will check previous experiments and decide a clever timeout")
    parser.add_argument("--commit-result", action='store_true',
                        dest="commit", default=False, help="Flag for push the results to db after the experiment (dynamic timeout flag should be set for db config).")
    parser.add_argument("--dump-results", action='store',
                        dest="results_file", default=None, help="Supply a results file to appends results. It should dump like a json array each line without delimiter.")
    parser.add_argument("--conjure-bin", action='store',
                        dest="conjure_bin", default="conjure-dominance", help="Conjure binary to use. Default: conjure-dominance")
    parser.add_argument('--sub-mdd', action='store_true', dest='sub_mdd',
                        default=False, help='Use MDD on submodel for SAT')
    args = parser.parse_args()
    args.optuna_id = None
    solve(args)


def solve(args):
    start_time = time.time()
    if "c" != args.mode and "m" != args.mode and "ar" != args.mode and "d" != args.mode and "r" != args.mode:
        sys.exit()
    # start_size, eclat_time = get_start_size_from_eclat(freq, init_param)
    # if start_size == 0:
    #     sys.exit(0)
    # elif start_size == -1:
    #     start_size = get_max_row_card(init_param)
    stats = dict()
    # stats["Eclat time"] = eclat_time
    print(mkdir_command.format(args.tmp_location))
    mkdir_process = subprocess.Popen(mkdir_command.format(
        args.tmp_location).split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(mkdir_process.stdout.readline, b''):
        print(line.decode()[:-1])
    new_essence_param = gen_new_essence_param(
        args.init_param, essence_suffix, args.freq, args.mode, args.optuna_id, args.model)
    init_eprime_param = args.tmp_location + \
        new_essence_param.split(".")[0].split("/")[-1]+eprime_suffix
    #this is different
    print(mkdir_command.format(args.info_location))
    mkdir_process = subprocess.Popen(mkdir_command.format(
        args.info_location).split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(mkdir_process.stdout.readline, b''):
        print(line.decode()[:-1])
    print(mkdir_command.format(args.tmp_location))
    mkdir_process = subprocess.Popen(mkdir_command.format(
        args.tmp_location).split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(mkdir_process.stdout.readline, b''):
        print(line.decode()[:-1])
    low_level_file = args.model.split(".")[0].split("/")[-1]+"__"+new_essence_param.split(
        ".")[0].split("/")[-1]
    if args.o_flag == 'O0':
        low_level_file += "_o0"
    elif args.o_flag == 'O1':
        low_level_file += "_o1"
    else:
        low_level_file += "_o2"
    if args.compress_doms:
        low_level_file += "_compressed_doms"
    if args.noblock_dom:
        low_level_file += "_no_block_dom_v2"
    if args.interactive:
        low_level_file += "_interactive"
    if args.one_sol:
        low_level_file += "_1sol"
    low_level_file += "_" + args.preproc
    info_file = args.info_location + low_level_file
    low_level_file = args.tmp_location + low_level_file
    if "minion" in args.solver_flag:
        info_file = info_file + "_minion"
    elif "nbc" in args.solver_flag:
        info_file = info_file + "_nbc"
    elif "glucose" in args.solver_flag:
        info_file = info_file + "_glucose"
    elif "cadical" in args.solver_flag:
        info_file = info_file + "_cadical"
    elif "z3" in args.solver_flag:
        info_file = info_file + "_z3"
    elif "yices2" in args.solver_flag:
        info_file = info_file + "_yices2"
    elif "boolector" in args.solver_flag:
        info_file = info_file + "_boolector"
    if args.smt_logic == "lia":
        info_file = info_file + "_lia"
    if args.smt_logic == "nia":
        info_file = info_file + "_nia"
    if args.smt_logic == "idl":
        info_file = info_file + "_idl"
    minion_file = low_level_file+".minion"
    dimacs_file = low_level_file+".dimacs"
    smt2_file = low_level_file+".smt2"
    sr_info_file = low_level_file+".info"
    info_file = info_file+"_info.txt"
    new_conjure_command = conjure_trans_param_command.format(args.conjure_bin,
                                                             args.model, new_essence_param, init_eprime_param)
    print_stdout_and_file(new_conjure_command, info_file, log=True)
    conjure_start_time = time.time()
    conjure_process = subprocess.Popen(
        new_conjure_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(conjure_process.stdout.readline, b''):
        print_stdout_and_file(line.decode()[:-1], info_file, log=True)
    conjure_end_time = time.time()
    conjure_process.wait()
    if conjure_process.returncode != 0:
        sys.exit(1)
    # edit eprime file
    # edit_eprime_file(init_eprime_param, start_size)
    stats["Conjure translate param time"] = conjure_end_time - conjure_start_time
    stats["SolverTotalTime Sum"] = 0
    stats["SavileRowTime Sum"] = 0
    stats["SavileRow Command time"] = 0
    stats["Number of solutions"] = 0
    sr_start_time = time.time()
    # choose targeted solver
    if args.interactive:
        sat_rnd_flag = "\"seed={}\""
    else:
        sat_rnd_flag = ""
    if "glucose" in args.solver_flag:
        if sat_rnd_flag == "":
            sat_rnd_flag = "\"-rnd-seed={}\""
        act_sat_suffix = sat_suffix.format(
            dimacs_file, "glucose", sat_rnd_flag.format(args.rnd_seed))
        add_suffix = act_sat_suffix
    elif "nbc" in args.solver_flag:
        if "noincomp" in args.model:
            act_sat_suffix = sat_suffix.format(
                dimacs_file, "nbc_minisat_all", "\"-r {} -n {}\"".format(args.rnd_seed, 1))
        else:
            if sat_rnd_flag == "":
                sat_rnd_flag = "\"-r {}\""
            act_sat_suffix = sat_suffix.format(
                dimacs_file, "nbc_minisat_all", sat_rnd_flag.format(args.rnd_seed))
        add_suffix = act_sat_suffix
    elif "cadical" in args.solver_flag:
        if sat_rnd_flag == "":
            sat_rnd_flag = "\"--seed={}\""
        act_sat_suffix = sat_suffix.format(
            dimacs_file, "cadical", sat_rnd_flag.format(args.rnd_seed))
        add_suffix = act_sat_suffix
    elif "minion" in args.solver_flag:
        add_suffix = minion_suffix.format(minion_file)
    elif "z3" in args.solver_flag or "boolector" in args.solver_flag or "yices2" in args.solver_flag:
        add_suffix = smt_suffix.format(
            smt2_file, args.solver_flag, args.rnd_seed)
        if args.smt_logic == "lia":
            add_suffix += smt_lia_suffix
        elif args.smt_logic == "nia":
            add_suffix += smt_nia_suffix
        elif args.smt_logic == "idl":
            add_suffix += smt_idl_suffix
    if args.one_sol:
        add_suffix += one_sol_suffix
    if args.native:
        savilerow_exec = savilerow_native
    else:
        savilerow_exec = savilerow_jar
    new_savilerow_command = savilerow_command.format(
        savilerow_exec, args.model, init_eprime_param, args.preproc, args.flatten) + add_suffix + info_suffix.format(sr_info_file)
    if args.cgroups_flag:
        new_savilerow_command += cgroups_suffix
    if args.o_flag == 'O0':
        new_savilerow_command += " -O0"
    elif args.o_flag == 'O1':
        new_savilerow_command += " -O1"
    if args.compress_doms:
        new_savilerow_command += " -compress-doms"
    if args.noblock_dom:
        new_savilerow_command += " -noblock-dom"
    if args.sub_mdd:
        new_savilerow_command += " -sat-pb-mdd-sub"
    if args.interactive:
        new_savilerow_command += interactive_suffix
    if args.timeout is not None:
        new_savilerow_command = timelimit_prefix.format(
            int(args.timeout)) + new_savilerow_command
    elif args.dynamic_t is not None and "json" in args.dynamic_t:
        new_savilerow_command = timelimit_prefix.format(
            read_json_and_get_timeout(args.dynamic_t, args)) + new_savilerow_command
    elif args.dynamic_t is not None and "cfg" in args.dynamic_t:
        new_savilerow_command = timelimit_prefix.format(
            read_db_and_get_timeout(args)) + new_savilerow_command
    print_stdout_and_file(new_savilerow_command, info_file, log=True)
    savilerow_process = subprocess.Popen(shlex.split(
        new_savilerow_command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    solutions = []
    solution_level = dict()
    sr_mem_out = False
    # become leader
    os.setpgrp()
    for line in iter(savilerow_process.stdout.readline, b''):
        code, result, result_occ = get_solution(line.decode(), args.mode)
        if code == True:
            add_solution(result, result_occ, solutions,
                         args.mode, args.save_flag)
        else:
            if line.decode().startswith("Looking"):
                print_stdout_and_file("Solutions so far: {}".format(
                    len(solutions)), info_file, log=True)
                level = line.decode().split(": ")[1].strip()
                solution_level[level] = len(solutions)
            if "Killed" in line.decode() or "OutOfMemory" in line.decode():
                sr_mem_out = True
            if len(solutions) > 500000:
                print_stdout_and_file(
                    "ERROR : Too many solutions", info_file, log=True)
                os.killpg(0, 15)
                sys.exit(0)
            print_stdout_and_file(line.decode().strip(), info_file, log=True)
    sr_end_time = time.time()
    stats["SavileRow Command time"] += sr_end_time-sr_start_time
    savilerow_process.wait()
    if savilerow_process.returncode != 0:
        print_stdout_and_file(
            "ERROR : SR non zero exit code", info_file, log=True)
        if savilerow_process.returncode == 124:
            print_stdout_and_file(
                "ERROR: Savile Row timed out.", info_file, log=True)
        success_flag = False
    elif sr_mem_out:
        print_stdout_and_file("ERROR : SR memory out", info_file, log=True)
        success_flag = False
    else:
        success_flag = True
    nc_time_st = time.time()
    # nc_solutions_size = len(exploder.explode_solutions(solutions, init_param))
    stats["Number of solutions"] = len(solutions)
    stats = get_savilerow_stats(
        sr_info_file, stats, args.interactive, solution_level, success_flag)
    if not success_flag:
        stats["Number of solutions"] = None
        stats["SavileRow Command time"] = None
        stats["SolverTotalTime Sum"] = None
        stats["SavileRowTime Sum"] = None
        stats["SolverNodesTotal"] = None
    # check and verify number of solutions
    if success_flag and args.dynamic_t is not None:
        if "cfg" in args.dynamic_t:
            nb_sols = read_db_and_get_nb_solutions(args)
        else:
            nb_sols = read_json_and_get_nb_solutions(args.dynamic_t, args)
        if nb_sols != -1 and stats["Number of solutions"] != nb_sols:
            if "noincomp" in args.model and stats["Number of solutions"] > nb_sols:
                print_stdout_and_file("Expected {} but got {} sols. Probably due to no incomp".format(
                    nb_sols, stats["Number of solutions"]))
            else:
                print_stdout_and_file(
                    "Solution count has been reported differently for this experiment", info_file, log=True)

    stats["Number of frequent solutions"] = None  # nc_solutions_size
    nc_time_end = time.time()
    # stats["Exploding frequent solutions time"] = nc_time_end - nc_time_st
    end_time = time.time()
    stats["Script Total time"] = end_time-start_time
    clean_files(new_essence_param, init_eprime_param,
                minion_file, dimacs_file, smt2_file)
    print_and_store_results(args.freq, args.mode, stats,
                            info_file, solutions, args.save_flag, args.results_file, args)
    # return solutions
    return info_file


def clean_files(new_essence_param, init_eprime_param, minion_file, dimacs_file, smt2_file):
    print(rm_command.format(new_essence_param))
    rm_process = subprocess.Popen(rm_command.format(
        new_essence_param).split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(rm_process.stdout.readline, b''):
        print(line.decode()[:-1])
    print(rm_command.format(init_eprime_param))
    rm_process = subprocess.Popen(rm_command.format(
        init_eprime_param).split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(rm_process.stdout.readline, b''):
        print(line.decode()[:-1])
    print(rm_command.format(minion_file))
    rm_process = subprocess.Popen(rm_command.format(
        minion_file).split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(rm_process.stdout.readline, b''):
        print(line.decode()[:-1])
    print(rm_command.format(dimacs_file))
    rm_process = subprocess.Popen(rm_command.format(
        dimacs_file).split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(rm_process.stdout.readline, b''):
        print(line.decode()[:-1])
    print(rm_command.format(smt2_file))
    rm_process = subprocess.Popen(rm_command.format(
        smt2_file).split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(rm_process.stdout.readline, b''):
        print(line.decode()[:-1])


def edit_eprime_file(init_eprime_param, start_size):
    with open(init_eprime_param, "r") as f:
        lines = f.readlines()

    with open(init_eprime_param, "w") as f:
        f.writelines(lines)
        buff = "letting sizes be [ "
        for i in range(start_size, -1, -1):
            buff += str(i) + ", "
        f.write(buff[:-2]+" ]")


def add_solution(result, result_occ, solutions, mode, save_flag):
    if not save_flag:
        solutions.append(True)
    else:
        sol = {"set_occurrence": result}
        if result_occ is not None:
            sol["count"] = result_occ
        occurrence_sol_to_explicit_sol(sol)
        solutions.append(sol)


def get_solution(line, mode):
    # due to having new models, reading solution might have crashes.
    # since we dont use them, it's okay
    if line.startswith("Solution"):
        try:
            if mode == "c":
                solution = line.strip().split(
                    "freq_items_1_Occurrence be ")[1].split(';int(')[0] + "]"
                if "freq_items_2" in line:
                    solution_occ = line.strip().split(" freq_items_2 be ")[1]
                else:
                    solution_occ = None
            elif mode == "m":
                solution = line.strip().split(
                    "freq_items_Occurrence be ")[1].split(';int(')[0] + "]"
                solution_occ = None
            elif mode == "ar":
                solution = line.strip().split("lhs_freq_items_1_Occurrence be ")[1].split(';int(')[
                    0] + "]" + " -> " + line.strip().split("lhs_freq_items_1_Occurrence be ")[1].split(';int(')[0] + "]"
                solution_occ = line.strip().split("lhs_freq_items_2 be ")[
                    1] + " -> " + line.strip().split("rhs_freq_items_2 be ")[1]
            elif mode == "d":
                solution = line.strip().split(
                    "freq_items_itemset_Occurrence be ")[1].split(';int(')[0] + "]"
                solution_occ = None
            elif mode == "r":
                solution = line.strip().split(
                    "infreq_items_itemset_Occurrence be ")[1].split(';int(')[0] + "]"
                solution_occ = line.strip().split(
                    "infreq_items_support be ")[1].split(';int(')[0] + "]"
            return True, solution, solution_occ
        except:
            return True, None, None
    else:
        return False, False, False


def occurrence_sol_to_explicit_sol(solution):
    explicit_sol = []
    split_sol = solution["set_occurrence"][1:-1].split(", ")
    for i in range(len(split_sol)):
        if split_sol[i] == "true":
            explicit_sol.append(i)
    solution["set"] = explicit_sol
    solution.pop("set_occurrence")


def get_savilerow_stats(sr_info_file, stats, interactive_flag, solution_level, success_flag):
    stats["SATVars"] = dict()
    stats["SATClauses"] = dict()
    stats["SATLearntClauses"] = dict()
    stats["SolverNodes"] = dict()
    stats["SolutionsByLevel"] = dict()
    stats["SolverTimeByLevel"] = dict()
    stats["SolverNodesTotal"] = -1
    if success_flag:
        with open(sr_info_file, "r") as f:
            lines = f.readlines()
        order = -1
        for line in lines:
            if "SolverTotalTime" in line:
                solver_time = line.split(":")[1].split("\n")[0]
                stats["SolverTotalTime Sum"] += float(solver_time)
                stats["SolverTimeByLevel"][order] = solver_time
            elif "SavileRowTotalTime" in line:
                solver_time = line.split(":")[1].split("\n")[0]
                stats["SavileRowTime Sum"] = float(solver_time)
            elif "Partial order" in line:
                order = line.strip().split(": ")[1]
            elif "SATVars" in line:
                a = line.split(":")[1].split("\n")[0]
                stats["SATVars"][order] = a
            elif "SATClauses" in line:
                a = line.split(":")[1].split("\n")[0]
                stats["SATClauses"][order] = a
            elif "SATLearntClauses" in line:
                a = line.split(":")[1].split("\n")[0]
                stats["SATLearntClauses"][order] = a
            elif "SolverSolutionsFound" in line:
                a = line.split(":")[1].split("\n")[0]
                stats["SolutionsByLevel"][order] = a
            elif "SolverNodes" in line:
                a = line.split(":")[1].split("\n")[0]
                stats["SolverNodes"][order] = a
                if interactive_flag:
                    if float(a) > float(stats["SolverNodesTotal"]):
                        stats["SolverNodesTotal"] = a
                else:
                    stats["SolverNodesTotal"] = str(
                        float(a)+float(stats["SolverNodesTotal"]))
        # if sol level dict is empty use the new one
        if not stats["SolutionsByLevel"]:
            stats["SolutionsByLevel"] = solution_level
    return stats


def print_and_store_results(freq, mode, stats, info_file, solutions, save_flag, results_file, args):
    info_txt = "Freq: "+str(freq)+"% Mode: "+mode+"\n"
    info_txt += "Script Total Time: "+str(stats["Script Total time"])+"\n"
    # info_txt += "Eclat time: "+str(stats["Eclat time"])+"\n"
    info_txt += "Conjure translate param time: " + \
        str(stats["Conjure translate param time"])+"\n"
    info_txt += "SavileRow Command time: " + \
        str(stats["SavileRow Command time"])+"\n"
    info_txt += "SavileRowTime Sum: "+str(stats["SavileRowTime Sum"])+"\n"
    info_txt += "SolverTotalTime Sum: "+str(stats["SolverTotalTime Sum"])+"\n"
    info_txt += "SATVars :"+str(stats["SATVars"])+"\n"
    info_txt += "SATClauses :"+str(stats["SATClauses"])+"\n"
    info_txt += "SATLearntClauses :"+str(stats["SATLearntClauses"])+"\n"
    info_txt += "SolutionsByLevel :"+str(stats["SolutionsByLevel"])+"\n"
    info_txt += "SolverTimeByLevel :"+str(stats["SolverTimeByLevel"])+"\n"
    info_txt += "SolverNodes :"+str(stats["SolverNodes"])+"\n"
    info_txt += "SolverNodesTotal :"+str(stats["SolverNodesTotal"])+"\n"
    info_txt += "Number of solutions: "+str(stats["Number of solutions"])+"\n"
    sols_json = info_file.split(".")[0]+".json"
    if save_flag and stats["Number of solutions"] is not None:
        with open(sols_json, "w") as f:
            json.dump(solutions, f, indent=1)
        print("Solutions stored in "+sols_json)
        explode_time = time.time()
        stats["Number of frequent solutions"] = run_exploder(sols_json, args)
        explode_time = time.time() - explode_time
        stats["Exploding frequent solutions time"] = explode_time
        info_txt += "Exploding frequent solutions time: " + \
            str(stats["Exploding frequent solutions time"])+"\n"
        info_txt += "Number of frequent solutions: " + \
            str(stats["Number of frequent solutions"])+"\n"
    print_stdout_and_file(info_txt, info_file)
    print("Info stored in "+info_file)
    if args.commit:
        res = result_reader.process_one_info_file(info_file)
        new_res_file = info_file.split(".")[0]+".json"
        with open(new_res_file, "w") as f:
            json.dump(res, f)
        print("For db access, info also stored in "+new_res_file)
        commit_to_db(args, new_res_file)
    if results_file is not None:
        res = result_reader.process_one_info_file(info_file)
        with open(results_file, "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(res, f)
            f.write("\n")
            fcntl.flock(f, fcntl.LOCK_UN)
        print("Info dumped to "+results_file)


def gen_new_essence_param(init_param, suffix, freq, mode, optuna_id, model):
    freq_text = "f_" + str(freq).replace(".", "-") + \
        "_" + str(int(random.random()*100000))
    if optuna_id is not None:
        freq_text += "_id" + str(optuna_id)
    new_param = "{}_{}{}".format(init_param.split(".")[0], freq_text, suffix)
    with open(init_param, "r") as f:
        lines = f.readlines()
    db_starts = -1
    db_ends = -1
    for i in range(len(lines)):
        line = lines[i]
        if "be mset(" in line or "be sequence(" in line:
            db_starts = i+1
        if line.startswith(")"):
            db_ends = i-1
    row_size = db_ends - db_starts + 1
    # we need adhoc disc-rel set
    db_minValue = 50000
    db_maxValue = -1
    db_maxEntrySize = -1
    if "rel_sub" in init_param or "dis_cost" in init_param:
        if "modded" in model:
            print("Model bug hack inbound")
            for i in range(db_starts, db_ends+1):
                line = lines[i]
                numbs = list(
                    map(int, line.split(" = {")[1].split("}")[0].split(",")))
                if min(numbs) < db_minValue:
                    db_minValue = min(numbs)
                if max(numbs) > db_maxValue:
                    db_maxValue = max(numbs)
                if len(numbs) > db_maxEntrySize:
                    db_maxEntrySize = len(numbs)
            lines.append("\n")
            lines.append("letting {} be {}\n".format(
                "db_minValue", db_minValue))
            lines.append("letting {} be {}\n".format(
                "db_maxValue", db_maxValue))
            lines.append("letting {} be {}\n".format(
                "db_maxEntrySize", db_maxEntrySize))
            lines.append("letting {} be {}".format("db_row_size", row_size))
    # model hack end
    freq_count = int(round(row_size*freq/100))
    with open(new_param, "w") as f:
        f.writelines(lines)
        f.write("\n")
        f.write(freq_str.format(freq_count))
    return new_param


def get_start_size_from_eclat(freq, init_param):
    # hardcode audio temporarily
    if "audio" in init_param:
        return -1, 0
    nb = get_entry_size(init_param)
    occ = round(nb*freq/100)
    index = init_param.rfind("/")
    raw_param = init_param[:index] + \
        init_param[index:].split(".")[0].split("_")[0]+".dat"
    new_eclat_size_command = eclat_size_command.format("-"+str(occ), raw_param)
    new_timeout_command = timeout_command.format(
        eclat_timeout, eclat_memory_limit)
    new_eclat_size_command = new_timeout_command + new_eclat_size_command
    print(new_eclat_size_command)
    eclat_start_time = time.time()
    eclat_process = subprocess.Popen(new_eclat_size_command.split(
    ), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("waiting for eclat to finish")
    size = None
    for line in iter(eclat_process.stdout.readline, b''):
        if "MEM CPU" in line.decode():
            eclat_end_time = time.time()
            eclat_time = eclat_end_time-eclat_start_time
            print("eclat got OOM in {}".format(eclat_time))
            size = -1
        elif "TIMEOUT CPU" in line.decode():
            eclat_end_time = time.time()
            eclat_time = eclat_end_time-eclat_start_time
            print("Eclat got timeout in {}".format(eclat_time))
            size = -1
        elif "FINISHED" in line.decode():
            eclat_end_time = time.time()
            eclat_time = eclat_end_time-eclat_start_time
            print("eclat finished in {}".format(eclat_time))
            break
        else:
            result_line = line
    if "no (frequent) items found" in result_line.decode():
        size = 0
        print("No fis found by eclat in {} s, terminating directly".format(eclat_time))
    if size is None:
        size = int(result_line.decode().split(":")[0].strip())
        print("Maximum cardinality is found as {}".format(size))
    return size, eclat_time


def get_entry_size(init_param):
    index = init_param.rfind("/")
    raw_param = init_param[:index] + \
        init_param[index:].split(".")[0].split("_")[0]+".dat"
    with open(raw_param, "r") as f:
        lines = f.readlines()
        nb = len(lines)
    return nb


def get_max_row_card(param):
    with open(param, "r") as f:
        lines = f.readlines()
    max = 0
    for line in lines:
        count = len(line.split(","))
        if max < count:
            max = count
    return max


def get_item_count(init_param):
    index = init_param.rfind("/")
    raw_param = init_param[:index] + \
        init_param[index:].split(".")[0].split("_")[0]+".dat"
    with open(raw_param, "r") as f:
        lines = f.readlines()
    max_item = -1
    for line in lines:
        for i in line.split():
            if int(i) > max_item:
                max_item = int(i)
    return max_item


def print_stdout_and_file(given_text, given_file, log=False):
    print(given_text)
    if log:
        given_text = "LOG ENTRY: " + given_text
    with open(given_file, "a") as f:
        f.write(given_text + "\n")


def return_experiment_config_id(args):
    # model
    if "closed" in args.model:
        model = "closed"
    elif "gen" in args.model:
        model = "gen"
    elif "relevant" in args.model:
        model = "rel_sub"
    elif "disc" in args.model:
        model = "disc"
    elif "minimal" in args.model:
        model = "min_rare"
    # instance
    instance = args.init_param.split("/")[-1].split(".")[0]
    # freq
    freq = float(args.freq)
    if model != "rel_sub":
        experiment_id = model + "_" + instance + "_" + str(freq)
    else:
        experiment_id = model
        if "complete" in args.model:
            experiment_id += "_complete"
        elif "par_neg" in args.model:
            experiment_id += "_par_neg"
        elif "par_pos" in args.model:
            experiment_id += "_par_pos"
        experiment_id += "_" + instance + "_" + str(freq)
    # config
    # representation
    if "_exp_exp" in args.model:
        representation = "exp_exp"
    elif "_occ_exp" in args.model:
        representation = "occ_exp"
    elif "_exp_occ" in args.model:
        representation = "exp_occ"
    elif "_occ_occ" in args.model:
        representation = "occ_occ"
    else:
        if model == "closed" or model == "gen":
            representation = "occ_occ"
        else:
            representation = "exp_occ"
    # repr smt encoding
    if args.smt_logic == "lia":
        representation += "_lia"
    elif args.smt_logic == "nia":
        representation += "_nia"
    elif args.smt_logic == "idl":
        representation += "_idl"
    # repr rel sub incomparability
    # if model == "rel_sub":
    #     if "complete" in args.model:
    #          representation += "_complete"
    #     elif "par_pos" in args.model:
    #         representation += "_par_pos"
    #     elif "par_neg" in args.model:
    #         representation += "_par_neg"
    # preproc
    preproc = args.preproc
    # solver
    solver = args.solver_flag
    config_id = preproc + "_" + representation + "_" + solver + "_"
    # Incomp
    if "noincomp" in args.model:
        config_id += "0"
    else:
        config_id += "1"
    # interactive
    if args.interactive:
        config_id += "1"
    else:
        config_id += "0"
    # native
    if args.native:
        config_id += "1"
    else:
        config_id += "0"
    # comp
    if args.compress_doms:
        config_id += "1"
    else:
        config_id += "0"
    # order
    if "order" in args.model:
        config_id += "1"
    else:
        config_id += "0"
    # noblockdom
    if args.noblock_dom:
        config_id += "1"
    else:
        config_id += "0"
    # mdd
    if args.sub_mdd:
        config_id += "1"
    else:
        config_id += "0"
    # cgroups
    if args.cgroups_flag:
        config_id += "1"
    else:
        config_id += "0"
    return (experiment_id, config_id)


def read_json_and_get_exact(json_file, args):
    exp, config = return_experiment_config_id(args)
    result_reader_command_sr = "rrr json -i {} time -e {} -c {} -r".format(
        json_file, exp, config)
    result_reader_process = subprocess.Popen(result_reader_command_sr.split(
    ), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result_reader_command_sr)
    value = 21600
    for line in iter(result_reader_process.stdout.readline, b''):
        print(line.decode().strip())
        if "EMPTY" not in line.decode():
            value = float(line.decode().split()[1].strip())
            if "MIN" in line.decode():
                print("LOG: rrr found the exact value: {}".format(value))
            if "MAX" in line.decode():
                print(
                    "LOG: rrr found no values but found a max timeout: {}".format(value))
    return value


def read_db_and_get_exact(args):
    exp, config = return_experiment_config_id(args)
    result_reader_command_sr = "rrr db -d {} time -e {} -c {}".format(
        args.dynamic_t, exp, config)
    result_reader_process = subprocess.Popen(result_reader_command_sr.split(
    ), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result_reader_command_sr)
    value = 21600
    t = "EMPTY"
    for line in iter(result_reader_process.stdout.readline, b''):
        print(line.decode().strip())
        if "EMPTY" not in line.decode() and "DB error" not in line.decode():
            value = float(line.decode().split()[1].strip())
            if "MIN" in line.decode():
                t = "SUCCESS"
                print("LOG: rrr found the exact value: {}".format(value))
            if "MAX" in line.decode():
                t = "TIMEOUT/MEMOUT"
                print(
                    "LOG: rrr found no values but found a max timeout: {}".format(value))
    return value, t


def read_json_and_get_best(json_file, args):
    exp, config = return_experiment_config_id(args)
    result_reader_command_sr = "rrr json -i {} best-time -e {} -r".format(
        json_file, exp)
    result_reader_process = subprocess.Popen(result_reader_command_sr.split(
    ), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result_reader_command_sr)
    value = 21600
    for line in iter(result_reader_process.stdout.readline, b''):
        print(line.decode().strip())
        if "EMPTY" not in line.decode():
            value = float(line.decode().split()[1].strip())
            print("LOG: rrr found the best value: {}".format(value))
    return value


def read_db_and_get_best(args):
    exp, config = return_experiment_config_id(args)
    result_reader_command_sr = "rrr db -d {} best-time -e {}".format(
        args.dynamic_t, exp)
    result_reader_process = subprocess.Popen(result_reader_command_sr.split(
    ), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result_reader_command_sr)
    value = 21600
    for line in iter(result_reader_process.stdout.readline, b''):
        print(line.decode().strip())
        if "EMPTY" not in line.decode() and "DB error" not in line.decode():
            value = float(line.decode().split()[1].strip())
            print("LOG: rrr found the best value: {}".format(value))
    return value


def read_db_and_get_nb_solutions(args):
    exp, config = return_experiment_config_id(args)
    result_reader_command_sr = "rrr db -d {} sol -e {}".format(
        args.dynamic_t, exp)
    result_reader_process = subprocess.Popen(result_reader_command_sr.split(
    ), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result_reader_command_sr)
    value = -1
    for line in iter(result_reader_process.stdout.readline, b''):
        print(line.decode().strip())
        if "EMPTY" not in line.decode() and "error" not in line.decode():
            value = float(line.decode().split()[1].strip())
            support = int(line.decode().split()[4].strip())
            print("LOG: rrr found nb of solutions: {} with support".format(
                value, support))
    return value


def read_json_and_get_nb_solutions(json_file, args):
    exp, config = return_experiment_config_id(args)
    result_reader_command_sr = "rrr json -i {} sol -e {}".format(
        json_file, exp)
    result_reader_process = subprocess.Popen(result_reader_command_sr.split(
    ), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result_reader_command_sr)
    value = -1
    for line in iter(result_reader_process.stdout.readline, b''):
        print(line.decode().strip())
        if "EMPTY" not in line.decode():
            value = float(line.decode().split()[1].strip())
            print("LOG: rrr found nb of solutions: {}".format(value))
    return value


def read_db_and_check_enough(args):
    exp, config = return_experiment_config_id(args)
    result_reader_command_sr = "rrr db -d {} nb-success -e {} -c {}".format(
        args.dynamic_t, exp, config)
    result_reader_process = subprocess.Popen(result_reader_command_sr.split(
    ), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result_reader_command_sr)
    value = 0
    for line in iter(result_reader_process.stdout.readline, b''):
        print(line.decode().strip())
        if "DB error" not in line.decode():
            value = int(line.decode().split()[1].strip())
            print("LOG: rrr found distinct seed successful runs: {}".format(value))
    return value


def run_exploder(json_file, args):
    # exp, config = return_experiment_config_id(args)
    exploder_command_sr = "./scripts/run_w_cgroups.sh timeout 15m exploder-rust {}".format(
        json_file)
    exploder_process = subprocess.Popen(exploder_command_sr.split(
    ), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(exploder_command_sr)
    value = None
    for line in iter(exploder_process.stdout.readline, b''):
        print(line.decode().strip())
        try:
            value = int(line.decode())
            print(
                "LOG: exploder-rust found nb of native freq solutions: {}".format(value))
        except:
            value = None
    return value


def read_json_and_get_timeout(json_file, args):
    min_sr = read_json_and_get_best(json_file, args)
    return min(int(min_sr) * int(2) + 180, 21600)


def read_db_and_get_timeout(args):
    min_sr = read_db_and_get_best(args)
    return min(int(min_sr) * int(2) + 180, 21600)


def commit_to_db(args, new_json_file):
    # exp, config = return_experiment_config_id(args)
    result_reader_command_sr = "rrr db -d {} commit -a {}".format(
        args.dynamic_t, new_json_file)
    result_reader_process = subprocess.Popen(result_reader_command_sr.split(
    ), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result_reader_command_sr)
    for line in iter(result_reader_process.stdout.readline, b''):
        if "panic" in line.decode():
            print(line.decode().strip())
            sys.exit(1)


if __name__ == '__main__':
    main()
