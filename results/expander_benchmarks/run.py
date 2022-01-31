#!/usr/bin/env python3
import sys
import random
import subprocess
import time
import shlex
import os


def main():
    for i in range(3):
        process(i)


def process(i: int):
    command_str = "/usr/bin/time -v ./expander-rs {} {} {}"

    input = sys.argv[1]  # 0..=2
    hasher = sys.argv[2]  # 0..=3
    algo = sys.argv[3]  # 0..=3

    input_size = ""
    if input == "0":
        input_size = "easy"
    elif input == "1":
        input_size = "medium"
    elif input == "2":
        input_size = "hard"

    input_file = "data/example_{}.json".format(input_size)

    hasher_flag = ""
    if hasher == "0":
        hasher_flag = "--fnv-hasher"
    elif hasher == "1":
        hasher_flag = "--fx-hasher"
    elif hasher == "2":
        hasher_flag = "--std-hasher"
    elif hasher == "3":
        hasher_flag = "--aes-hasher"

    algo_flag = ""
    if algo == "0":
        algo_flag = "--vec-expander"
    elif algo == "1":
        algo_flag = "--bit-man-expander"
    elif algo == "2":
        algo_flag = "--bit-vec-expander"
    elif algo == "3":
        algo_flag = "--hash-only-expander"

    os.makedirs('info_files', exist_ok=True)
    gok_info_file = "info_files/" + input_size + "_" + \
        hasher_flag[2:-7] + "_" + algo_flag[2:-9] + "_" + str(i) + "_gok.info"

    if os.path.exists(gok_info_file):
        print("File already exists")
        return

    real_command_str = command_str.format(hasher_flag, algo_flag, input_file)
    print(real_command_str)
    start = time.time()
    command_process = subprocess.Popen(shlex.split(
        real_command_str), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    n = 0
    m = 0
    for line in iter(command_process.stdout.readline, b''):
        l = line.decode().strip()
        print(l)
        if "Total nb of item-sets" in l:
            n = int(l.split("Total nb of item-sets: ")[-1].strip())
        elif "Maximum resident set size (kbytes):" in l:
            m = int(l.split("Maximum resident set size (kbytes): ")
                    [-1].strip())
    end = time.time()
    script_time = end - start

    with open(gok_info_file, "w") as f:
        f.write("nb={}\n".format(n))
        f.write("max_ram_kb={}\n".format(m))
        f.write("TOTAL_TIME={} \n".format(script_time))
    print("Info stored in {}".format(gok_info_file))


if __name__ == '__main__':
    main()
