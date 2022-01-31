#!/usr/bin/env python3
import sys
import random
import subprocess
import time
import shlex

def main():
    for i in range(3):
        process()

def process():
    sr_str = "savilerow rcpsp.eprime eprime_params/{}"
    sat = " -sat"
    maxsat = " -maxsat"
    chuffed = " -chuffed"
    interactive = " -interactive-solver"
    linear_strategy = " -opt-strategy linear"
    unsat_strategy = " -opt-strategy unsat"
    suffix = "{} -out-minion {} -out-sat {} -out-chuffed {} -out-info {} -out-solution {} -solver-options {} -run-solver -cgroups -O0"

    with open("params.txt", "r") as f:
        files = f.readlines()

    param = files[int(sys.argv[1])].strip()
    random_nb = random.randint(1, 1000)

    # 0 normal + bisect
    # 1 normal + linear
    # 2 normal + unsat
    # 3 inter + bisect
    # 4 inter + linear
    # 5 inter + unsat
    # 6 maxsat
    # 7 chuffed
    # 8 minion
    mode = int(sys.argv[2])
    file_suffix = "temp_files/" + param.split(".")[0] + "_{}_r_" + str(random_nb) + ".{}"
    minion_file = ""

    def suffix_gen(mode_name, random_str, solver_str):
        minion_file = file_suffix.format(mode_name, "minion")
        sat_file = file_suffix.format(mode_name, "dimacs")
        info_file = file_suffix.format(mode_name, "info")
        fzn_file = file_suffix.format(mode_name, "fzn")
        solution_file = file_suffix.format(mode_name, "solution")
        my_suffix = suffix.format(solver_str, minion_file, sat_file, fzn_file, info_file, solution_file, random_str.format(random_nb))
        return my_suffix, info_file, solution_file

    if mode == 0:
        suffix, info_file, solution_file = suffix_gen("normal_bisect_glucose", "\"-rnd-seed={}\"", sat)
    elif mode == 1:
        suffix += linear_strategy
        suffix, info_file, solution_file = suffix_gen("normal_linear_glucose", "\"-rnd-seed={}\"", sat)
    elif mode == 2:
        suffix += unsat_strategy
        suffix, info_file, solution_file = suffix_gen("normal_unsat_glucose", "\"-rnd-seed={}\"", sat)
    elif mode == 3:
        suffix += interactive
        suffix, info_file, solution_file = suffix_gen("inter_bisect_glucose", "\"-seed={}\"", sat)
    elif mode == 4:
        suffix += linear_strategy + interactive
        suffix, info_file, solution_file = suffix_gen("inter_linear_glucose", "\"-seed={}\"", sat)
    elif mode == 5:
        suffix += unsat_strategy + interactive
        suffix, info_file, solution_file = suffix_gen("inter_unsat_glucose", "\"-seed={}\"", sat)
    elif mode == 6:
        suffix, info_file, solution_file = suffix_gen("openwbo_glucose", "\"-rnd-seed={}\"", maxsat)
    elif mode == 7:
        suffix, info_file, solution_file = suffix_gen("chuffed", "\"--rnd-seed {}\"", chuffed)
    elif mode == 8:
        suffix, info_file, solution_file = suffix_gen("minion", "\"\"", "")
    else:
        sys.exit(1)

    command_str = sr_str.format(param) + suffix

    print(command_str)
    start = time.time()
    command_process = subprocess.Popen(shlex.split(command_str), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    satisfiable = False
    for line in iter(command_process.stdout.readline, b''):
        print(line.decode()[:-1])
        if "Created solution file" in line.decode().strip():
            satisfiable = True
    end = time.time()
    script_time = end - start

    if satisfiable:
        with open(solution_file, "r") as f:
            sol_lines = f.readlines()

    with open(info_file, "r") as f:
        info_lines = f.readlines()

    gok_info_file = "info_files/" + info_file.split("/")[1].split(".")[0]+".txt"
    with open(gok_info_file, "w") as f:
        f.write("{}\n".format(command_str))
        if satisfiable:
            f.writelines(sol_lines)
        f.writelines(info_lines)
        f.write("TOTAL TIME: {} \n".format(script_time))
    print("Info stored in {}".format(gok_info_file))

if __name__ == '__main__':
    main()