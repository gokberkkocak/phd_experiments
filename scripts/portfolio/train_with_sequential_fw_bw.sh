#!/bin/bash
parallel -j10 --shuf --ungroup --eta --memfree 4G python train_with_sequential_fw_bw.py ::: $(seq 0 25) ::: $(seq 0 5) ::: 0 ::: 100 ::: $(seq 0 3)