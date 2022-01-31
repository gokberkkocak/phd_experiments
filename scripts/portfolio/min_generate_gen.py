import sys
import json
import subprocess
import os

files = [
    "raw/anneal.dat",
    "raw/audio.dat",
    "raw/aus.dat",
    "raw/german.dat",
    "raw/heart.dat",
    "raw/hepatit.dat",
    "raw/hypo.dat",
    "raw/krvskp.dat",
    "raw/lymph.dat",
    "raw/tumor.dat",
    "raw/vote.dat",
    "raw/zoo.dat"
]
nb = int(sys.argv[1])
f = files[nb]

modes = ["s", "m", "c", "g"]
mode = int(sys.argv[2])
mode = modes[mode]

freqs = [10, 20, 30, 40, 50]
freq = int(sys.argv[3])
freq = freqs[freq]

timeouts = [1, 3, 5, 10, 20, 30]
timeout = int(sys.argv[4])
timeout = timeouts[timeout]

result_file = "results/{}_{}_{}_t_{}.json".format(
    files[nb].split(".")[0].split("/")[-1], freq, mode, timeout)

if os.path.exists(result_file):
    sys.exit(0)


cmd = "timeout {} eclat -t{} {} -s{} - "
metadata_cmd = "timeout 1 lcm C {} 1"


def metadata(f):
    metadata_run = metadata_cmd.format(f)
    # print(metadata_run)
    process = subprocess.Popen(
        metadata_run.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline, b''):
        decoded = line.decode().strip()
        if "trsact" in decoded:
            i = decoded.split(" ")
            trans = int(i[3])
            items = int(i[5])
            size = int(i[7])
            return (trans, items, size)


def run(f, timeout, freq, mode):
    run = cmd.format(timeout, mode, f, freq)
    # print(run)
    process = subprocess.Popen(
        run.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    count = 0
    for line in iter(process.stdout.readline, b''):
        decoded = line.decode().strip()
        if len(decoded) > 0 and decoded[0].isdigit():
            count += 1
    return count



t, i, s = metadata(f)
count = run(files[nb], timeout, freq, mode)
map = dict()
map["count"] = count
map["trans"] = t
map["items"] = i
map["size"] = s
with open(result_file, "w") as f:
    json.dump(map, f)
