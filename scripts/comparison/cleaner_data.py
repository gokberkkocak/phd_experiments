#!/usr/bin/python3
import os
import sys

location = sys.argv[1]
for root, dirs, files in os.walk(location):
    for name in files:
        if "_f_" in name and name.endswith("param"):
            r_f = os.path.join(root, name)
            print("Removing {}".format(r_f))
            os.remove(r_f)