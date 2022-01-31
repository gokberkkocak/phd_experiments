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
    sr_str = "savilerow-native rcpsp.eprime eprime_params/{}"
    yices_smt = " -smt -yices2 -yices2-bin yices-smt2"
    z3_smt = " -smt -z3 -z3-bin z3"
    interactive = " -interactive-solver"
    linear_strategy = " -opt-strategy linear"
    unsat_strategy = " -opt-strategy unsat"
    suffix = "{} -out-minion {} -out-smt {} -out-chuffed {} -out-info {} -out-solution {} -run-solver -cgroups -O0"

    with open("params.txt", "r") as f:
        files = f.readlines()

    param = files[int(sys.argv[1])].strip()
    random_nb = random.randint(1, 1000)

    mode = int(sys.argv[2])
    file_suffix = "temp_files/" + param.split(".")[0] + "_{}_r_" + str(random_nb) + ".{}"

    def suffix_gen(mode_name, random_str, solver_str):
        minion_file = file_suffix.format(mode_name, "minion")
        smt_file = file_suffix.format(mode_name, "smt2")
        info_file = file_suffix.format(mode_name, "info")
        fzn_file = file_suffix.format(mode_name, "fzn")
        solution_file = file_suffix.format(mode_name, "solution")
        my_suffix = suffix.format(solver_str, minion_file, smt_file, fzn_file, info_file, solution_file)
        return my_suffix, info_file, solution_file

    if mode == 0:
        suffix, info_file, solution_file = suffix_gen("normal_bisect_yices", "\"-rnd-seed={}\"", yices_smt)
    elif mode == 1:
        suffix += linear_strategy
        suffix, info_file, solution_file = suffix_gen("normal_linear_yices", "\"-rnd-seed={}\"", yices_smt)
    elif mode == 2:
        suffix += unsat_strategy
        suffix, info_file, solution_file = suffix_gen("normal_unsat_yices", "\"-rnd-seed={}\"", yices_smt)
    elif mode == 3:
        suffix += interactive
        suffix, info_file, solution_file = suffix_gen("inter_bisect_yices", "\"-seed={}\"", yices_smt)
    elif mode == 4:
        suffix += linear_strategy + interactive
        suffix, info_file, solution_file = suffix_gen("inter_linear_yices", "\"-seed={}\"", yices_smt)
    elif mode == 5:
        suffix += unsat_strategy + interactive
        suffix, info_file, solution_file = suffix_gen("inter_unsat_yices", "\"-seed={}\"", yices_smt)
    elif mode == 6:
        suffix, info_file, solution_file = suffix_gen("z3", "\"-rnd-seed={}\"", z3_smt)
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

    gok_info_file = "info_files_native/" + info_file.split("/")[1].split(".")[0]+".txt"
    with open(gok_info_file, "w") as f:
        f.write("{}\n".format(command_str))
        if satisfiable:
            f.writelines(sol_lines)
        f.writelines(info_lines)
        f.write("TOTAL TIME: {} \n".format(script_time))
    print("Info stored in {}".format(gok_info_file))

if __name__ == '__main__':
    main()