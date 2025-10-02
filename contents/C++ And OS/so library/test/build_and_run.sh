#!/bin/bash

set -e 

g++ main.cpp -L. -lMyLib.so -o main
export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH
./main

echo "build_and_run.sh finished"
