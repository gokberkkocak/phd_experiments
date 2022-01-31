import sys
import numpy as np
import pandas as pd

def main():
    with open(sys.argv[1], 'r') as f:
        lines = f.readlines()

    names = lines[0].strip().split(",")
    names = names[1:]
    cleaned = comp(lines, 1.5, 10)
    comp_dict = comp_winners(cleaned)
    df = pd.DataFrame.from_dict(comp_dict,  orient='index', columns=["count"])
    df.to_csv(cleaned.split(".")[0]+"_ranking.csv")

def comp(lines: str, ratio: float, min_time: int):
    new_lines = []
    new_lines.append(lines[0])
    for line in lines[1:]:
        values = line.split(",")
        comp = []
        comp.append(values[0])
        values = values[1:]
        values = np.array(values)
        values = values.astype(float)
        min_value = np.nanmin(values)
        for i in values:
            if i < min_time or i <= min_value * (1+ratio):
                comp.append("1")
            else:
                comp.append("0")
        new_lines.append(str(comp).replace(
            "[", "").replace("]", "").replace("\'", "")+"\n")

    new_name = sys.argv[1].split(
        ".")[0] + "_comp_{}_{}secs.csv".format(int(ratio*100), min_time)
    with open(new_name, "w") as f:
        f.writelines(new_lines)
    cleaned = clean_zeros(new_name)
    return cleaned

def clean_zeros(new_file: str):
    df = pd.read_csv(new_file, index_col=0)
    to_remove = []
    for i in df:
        if df[i].sum() == 0:
            to_remove.append(i)
    for i in to_remove:
        df = df.drop(i, 1)
    cleaned = new_file.split('.')[0]+"_removed_0.csv"
    df.to_csv(cleaned)
    return cleaned


def comp_winners(new_file: str):
    df = pd.read_csv(new_file, index_col=0)
    final_dict = dict()
    for i in df:
        nb_comp = df[i].sum()
        final_dict[i] = nb_comp
    return final_dict

if __name__ == '__main__':
    main()