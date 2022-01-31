#!/usr/bin/python3
import os
import time
import subprocess
import sys

#
# Check if any file is going above 200gigs. (go crazy on enp-ferry) If so, delete it which will kill the experiment.
# Also delete any not deleted files.
#

tmp_location = sys.argv[1]
minsol_location = sys.argv[2]
rm_command = "rm -rf {}"
cgroups_check_command = "lscgroup"
cgroups_delete_command = "cgdelete -g {}"
ps_process_command = "ps -ef"
kill_command = "kill -9 {}"
while (True):
    for filename in os.listdir(tmp_location):
        f = os.path.join(tmp_location, filename)
        if  os.access(f, os.R_OK):
            if (os.path.getsize(f) > 75*1024*1024*1024 or  time.time() - os.path.getmtime(f) > 6*60*60):
                print(f, os.path.getmtime(f), os.path.getsize(f))
                print(rm_command.format(f))
                rm_process = subprocess.Popen(rm_command.format(f).split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in iter(rm_process.stdout.readline, b''):
                    print(line.decode()[:-1])
    for filename in os.listdir(minsol_location):
        f = os.path.join(minsol_location, filename)
        if  os.access(f, os.R_OK) and ".MINIONSOL" in filename:
            if (os.path.getsize(f) > 50*1024*1024*1024 or time.time() - os.path.getmtime(f) > 6*60*60):
                print(f, os.path.getmtime(f), os.path.getsize(f))
                print(rm_command.format(f))
                rm_process = subprocess.Popen(rm_command.format(f).split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in iter(rm_process.stdout.readline, b''):
                    print(line.decode()[:-1])
    cg_process = subprocess.Popen(cgroups_check_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(cg_process.stdout.readline, b''):
        if "cpu" in line.decode() and "savilerow" in line.decode():
            creation_date = int(line.decode().split("_")[1])
            if time.time() - creation_date > 10*60*60:
                print(cgroups_delete_command.format(line.decode()))
                cgd_process = subprocess.Popen(cgroups_delete_command.format(line.decode()).split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in iter(cgd_process.stdout.readline, b''):
                    print(line.decode()[:-1])
    # kill orphans
    ps_process = subprocess.Popen(ps_process_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(ps_process.stdout.readline, b''):
        if "gk34" in line.decode() and "minion" in line.decode():
            pid = int(line.decode().split()[1])
            ppid = int(line.decode().split()[2])
            if ppid == 1:
                kill_process = subprocess.Popen(kill_command.format(pid).split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                print(kill_command.format(pid))
    time.sleep(5)