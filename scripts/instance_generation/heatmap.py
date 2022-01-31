import json
import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

x = "cost"
y = "util"
z = "value"    

def main():
    if (len(sys.argv) < 1):
        sys.exit()    
    json_file = sys.argv[1]
    with open(json_file, "r") as f:
        exps = json.load(f)
    c=[]
    u=[]
    solve_time_per_sol = []
    script_time_per_sol = []
    sols = []
    solver_time = []
    script_time = []
    freq_sols = []
    compression_c_to_f = []
    exp_name = json_file.split(".")[0]
    for exp in exps:
        c.append(pd.to_numeric(exp[x]))
        u.append(pd.to_numeric(exp[y]))
        if "sols" in exp:
            if exp["sols"] > 0:
                solve_time_per_sol.append(pd.to_numeric(int(exp["solver_time"]/exp["sols"]*1000)))
                script_time_per_sol.append(pd.to_numeric(exp["script_time"]/exp["sols"]))
                # compression_c_to_f.append(pd.to_numeric(exp["sols"]/exp["freq sols"]))
            else:
                solve_time_per_sol.append(pd.to_numeric(""))
                script_time_per_sol.append(pd.to_numeric(""))
                compression_c_to_f.append(pd.to_numeric(""))
            solver_time.append(pd.to_numeric(exp["solver_time"]))
            script_time.append(pd.to_numeric(exp["script_time"]))
            sols.append(pd.to_numeric(exp["sols"]))
            # freq_sols.append(pd.to_numeric(exp["freq sols"]))
        else:
            sols.append(pd.to_numeric(""))
            freq_sols.append(pd.to_numeric(""))
            solver_time.append(pd.to_numeric(""))
            script_time.append(pd.to_numeric(""))
            solve_time_per_sol.append(pd.to_numeric(""))
            script_time_per_sol.append(pd.to_numeric(""))
            compression_c_to_f.append(pd.to_numeric(""))
    create_plot(exp_name, c, u, sols, "sols")
    # create_plot(exp_name, c, u, freq_sols, "freq_sols")
    create_plot(exp_name, c, u, solve_time_per_sol, "solve_time_per_sol")
    create_plot(exp_name, c, u, script_time_per_sol, "script_time_per_sol")
    create_plot(exp_name, c, u, solver_time, "solver_time")
    create_plot(exp_name, c, u, script_time, "script_time")
    # create_plot(exp_name, c, u, compression_c_to_f, "compression_c_to_f")

labels = {
    "sols": "Number of solutions",
    "freq_sols": "Frequency of solutions",
    "solve_time_per_sol": "Solver time per solution",
    "script_time_per_sol": "Script time per solution",
    "solver_time": "Solver time",
    "script_time": "Script time",
    "compression_c_to_f": "Compression ratio of closed to full"
}

def create_plot(exp_name, axis_1, axis_2, values, value_name):
    data = pd.DataFrame(data={x:axis_1, y:axis_2, z:values})
    data = data.pivot(index=x, columns=y, values=z)
    plt.figure(figsize=(9 , 5))
    ax = sns.heatmap(data, cbar_kws={'label': labels[value_name]})#, annot=True)
    ax.invert_yaxis()
    # plt.show() 
    plt.tight_layout()
    file_name = exp_name+"_"+value_name+".pdf"
    file_name = file_name.replace("_", "-")
    plt.savefig(file_name)

if __name__ == '__main__':
    main()