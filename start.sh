#!/bin/bash

if (( $EUID != 0 )); then
    echo "Please run as root"
    exit
fi

python3 /home/sven/BrauSteuerung/run.py -s $1 $2

echo "ENDE: Start script der Brausteuerung"


exit 0
