#!/bin/bash
parallel -j3 --shuf --ungroup --eta --memfree 4G python train_with_test_v3.py ::: $(seq 0 25) ::: $(seq 0 5) ::: $(seq 0 1) ::: 150