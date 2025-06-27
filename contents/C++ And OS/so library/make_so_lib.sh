#!/bin/bash

set -e

# check argc
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <.cpp filename> <.so name>"
  exit 1
fi

# get input from command line
CPP_FILE=$1
LIB_NAME=$2

OBJ_FILE="${CPP_FILE%.*}"

g++ -fPIC -c $CPP_FILE -o $OBJ_FILE.o
g++ -shared -o $LIB_NAME $OBJ_FILE.o

mv $LIB_NAME ./test

echo "make_so_lib.sh has finished"