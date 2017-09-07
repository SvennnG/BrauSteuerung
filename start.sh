#!/bin/bash

if (( $EUID != 0 )); then
    echo "Please run as root"
    exit
fi

if (( $1 == "-s" )); then
    python3 ./run.py $1 $2 $3 $4 $5 > ./log/Maischen.output
elif (( $2 == "-s" )); then
    python3 ./run.py $1 $2 $3 $4 $5 > ./log/Maischen.output
elif (( $3 == "-s" )); then
    python3 ./run.py $1 $2 $3 $4 $5 > ./log/Maischen.output
elif (( $4 == "-s" )); then
    python3 ./run.py $1 $2 $3 $4 $5 > ./log/Maischen.output
elif (( $5 == "-s" )); then
    python3 ./run.py $1 $2 $3 $4 $5 > ./log/Maischen.output
else
    python3 ./run.py $1 $2 $3 $4 $5
fi


