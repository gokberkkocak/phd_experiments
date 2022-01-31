#!/bin/bash
parallel -j3 --shuf --ungroup --eta --memfree 4G python train_with_test_v3_single.py ::: $(seq 0 25) ::: $(seq 0 5) ::: 1 ::: 100