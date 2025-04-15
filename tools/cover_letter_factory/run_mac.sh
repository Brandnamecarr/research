#!/bin/bash

# check an argument was passed in
if [ -z "$1" ]; then
    echo "Please provide an argument"
    exit 1
fi

# Run the python script with the argument
python main.py "$1"

echo "Done"
