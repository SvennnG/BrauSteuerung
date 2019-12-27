#!/bin/bash

if (( $EUID != 0 )); then
    echo "Please run as root"
    exit
fi

echo "Clearing old Log file"
now=$(date +"%m_%d_%Y-%H:%M")
echo "\nZipping log... $now\n" >> log/Maischen.log
gzip log/Maischen.log
mv log/Maischen.log.gz log/Maischen_previous.log.gz
touch log/Maischen.log

# wait until an i2c address is not -- (should be 20 for the display)
wc=`i2cdetect -y 1 | tr -cd '-' | wc -c`
while [[ $wc != 232 ]]; do
	sleep 1
        echo "WC is (!232) $wc"
	wc=`i2cdetect -y 1 | tr -cd '-' | wc -c`
done

source brau/bin/activate
sleep 2 && /home/gesper/BrauSteuerung/brau/bin/python3 /home/gesper/BrauSteuerung/run.py -s $1 $2

echo "ENDE: Start script der Brausteuerung"


exit 0
