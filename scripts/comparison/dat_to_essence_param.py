#!/usr/bin/env python3

import argparse
import sys
import random
import os

VERSION = "0.1"

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(VERSION))
    parser.add_argument('--input', action='store',
                    dest='input_file', help='Input')
    parser.add_argument("--disc", action="store_true",
                    dest='disc', default=False, help="Whether disc or not")
    parser.add_argument("--ratio", action="store",
                    dest='sample_ratio', type=float, default=0, help="Sample ratio")
    parser.add_argument("--item-limit", action="store",
                    dest='item_limit', type=int, default=-1, help="Item limit")
    parser.add_argument("--fix-length", action="store",
                    dest="fix_length", type=int, default=0, help="Fix length on itemsets")

    args = parser.parse_args()
    instance_gen(args, dict())

def instance_gen(args, opt_args):
    
    output_file = ".".join(args.input_file.split(".")[:-1]) + "/"
    os.makedirs(output_file, exist_ok=True)
    # if args.disc:
    #     output_file += "_disc"
    # else:
    #     output_file += "_closed"
    # if args.sample_ratio > 0:
    #     output_file += "_" + str(int(args.sample_ratio * 100000))
    # if args.item_limit != -1:
    #     output_file += "_i" + str(args.item_limit)
    # if args.fix_length != 0:
    #     output_file += "_f" + str(args.fix_length)

    # input
    with open(args.input_file, "r") as f:
        lines = f.readlines()

    global_max = -1
    global_min = 9999
    # mset = []

    nb_lines = len(lines)

    out_lines = []

    if args.sample_ratio is not None and args.sample_ratio != 0:
        rows = sampling(nb_lines, args.sample_ratio * nb_lines)

    super_type = "sequence" if args["disc"] else "mset" 
    out_lines.append("letting db be {}(\n".format(super_type))

    density_arr = []
    db_row_size = 0
    db_maxEntrySize = 0
    for i, line in enumerate(lines):
        arr = line.strip().split()
        i_arr = [int(i) for i in arr]
        # item limit
        if args.item_limit != -1:
            i_arr_2 = list(filter(lambda x: x < args.item_limit, i_arr))
            arr = [str(i) for i in i_arr_2]
            i_arr = [int(i) for i in arr]
        # fix length
        if args.fix_length != 0:
            if len(arr) > args.fix_length:
                columns = sampling(len(arr), args.fix_length)
                arr_2 = []
                for j, el in enumerate(arr):
                    if j in columns:
                        arr_2.append(el)
                arr = arr_2
                i_arr = [int(i) for i in arr]
            else:
                arr = []
                i_arr = [int(i) for i in arr]
        # after modification if elm left
        if len(arr) > 0 and ((args.sample_ratio != 0 and i in rows) or args.sample_ratio == 0):
            db_row_size += 1
            db_maxEntrySize = max(db_maxEntrySize, len(arr))
            local_max = max(i_arr)
            local_min = min(i_arr)
            global_min = min(local_min, global_min)
            global_max = max(local_max, global_max)
            density_arr.append(len(arr))
            if not args.disc:
                out_lines.append("{{{}}},\n".format(",".join(arr)))
            else:
                # class is just the sum % 2 to not randomness
                out_lines.append("record {{itemset = {{{}}}, class = {}}},\n".format(",".join(arr), sum(i_arr) % 2))

    out_lines.append(")\n")

    if args["disc"]:
        # we need adhoc disc-rel set
        print("Model bug hack inbound")
        out_lines.append("letting {} be {}\n".format(
            "db_minValue", global_min))
        out_lines.append("letting {} be {}\n".format(
            "db_maxValue", global_max))
        out_lines.append("letting {} be {}\n".format(
            "db_maxEntrySize", db_maxEntrySize))
        out_lines.append("letting {} be {}".format("db_row_size", db_row_size))
        out_lines.append("\n")

    density = (sum(density_arr)/global_max)/len(density_arr)



    util_text = "letting utility_values be ["
    cost_text = "letting cost_values be ["
    util_sum_text = "letting min_utility be {}\n"
    cost_sum_text = "letting max_cost be {}\n"
    t = 0
    if "util" in opt_args and "cost" in opt_args:
        u = [ str(i) for i in opt_args.util[global_min:global_max+1]]
        c = [ str(i) for i in opt_args.cost[global_min:global_max+1]]
        util_text += "{}; int({}..{})]\n".format(",".join(u), global_min, global_max)
        cost_text += "{}; int({}..{})]\n".format(",".join(c), global_min, global_max)
    else:
        for i in range(global_max-global_min+1):
            # value = random.randint(0, 25)
            # if value!=0:
            #     value=math.ceil(value/5)
            value=random.randint(0, 5)
            t += value
            util_text += str(value) + ", "

            value=random.randint(0, 5)
            cost_text += str(value) + ", "

        util_text = util_text[:-2] +  "; int({}..{})]\n".format(global_min, global_max)
        cost_text = cost_text[:-2] +  "; int({}..{})]\n".format(global_min, global_max)

    out_lines.append(util_text)
    out_lines.append(cost_text)

    output_file += "init_h_" + str(hash(frozenset(out_lines)))
    output_file += "_d_{:1.4f}".format(density).replace(".","-")

    if "min_util" in opt_args and "max_cost" in opt_args:
        out_lines.append(util_sum_text.format(opt_args.min_util))
        out_lines.append(cost_sum_text.format(opt_args.max_cost))
    else:
        out_lines.append(util_sum_text.format(int(1*t/8)))
        out_lines.append(cost_sum_text.format(int(3*t/8)))

    output_file += "_h_" + str(hash(frozenset(out_lines)))

    output_file += ".essence-param"

    with open(output_file, "w") as f:
        f.writelines(out_lines)

    return output_file


def sampling(n, k):
    # return random_sampling(n,k)
    return frozenset([i for i in range(int(k))])

def random_sampling(n, k):
    out = set()
    while(k > len(out)):
        new = random.randint(0,n)
        out.add(new)
    return frozenset(out)

if __name__ == "__main__":
    main()