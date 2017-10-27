#!/usr/bin/python

import time
import threading
import logging
import re
import sys
import os
#from Reader import tail

tempgetterID = 0

class TempGetter(threading.Thread):
    def __init__(self, file='/var/tmp/Px_temp.source'):
        global tempgetterID
        threading.Thread.__init__(self)
        self.id = tempgetterID
        tempgetterID = tempgetterID + 1
        self.file=file
        self.running=True
        self.output=True	# output to logger
        self.logger = logging.getLogger('Maischen')
        self.temp = -1.0
        self.debug = False	# exception printing
        
        print("#TempGetter [" + file + "] initialized")
    def run(self):
        cnt = 0
        while self.running:
            newtmp = float(self.read_sensor())
            if self.temp == False:
                self.temp = self.temp
                self.logger.warning('IO Error: read file %s failed!' % self.file)
            else:
                self.temp = newtmp
            if cnt % 2 == 0:
                #self.logger.info('Temp @%s is %.2f' % (self.file, self.temp))
                if self.output == True:
                    self.logger.info('Temp @%s is %.2f' % (self.file, self.temp))
                    #print ("Temp @%s got: %.2f" % (self.file, self.temp))
            cnt = cnt + 1
            time.sleep(0.5)
        print ("TempGetter run stopped! [" + self.file + "]")
        
    def read_sensor(self):
        value = 0.0
        try:
            f = infile = open(self.file, "r")
            line = f.readline()
            if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
                line = f.readline()
                m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
                if m:
                    value = str(float(m.group(2)) / 1000.0)
            f.close()
        except IOError as e:
            if self.debug:
                print (time.strftime("%x %X"), "Error reading", self.file, ": ", e)
            return False
        
        if float(value) == 85.0 or float(value) == 0.0:    # if connection error on sensor cable -> this is a error code, return last known temperature
            return self.temp
        return value


if __name__ == "__main__":
    try:
        logger = logging.getLogger('TempSensor')
        hdlr = logging.FileHandler('/var/log/TempSensor.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s: [%(filename)14s:%(lineno)3s - %(funcName)9s()] %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr) 
        logger.setLevel(logging.INFO)

        tempGetter = []
        tempGetter.append(TempGetter())
        for x,  dirs,  y in os.walk('/sys/bus/w1/devices/'):
            for x in dirs:
                if x.startswith('28-'):
                    tempGetter.append(TempGetter("/sys/bus/w1/devices/"+str(x)+"/w1_slave"))
        
        for item in tempGetter:
            item.start()
        
        while 1:
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            print ("\r\x1b[K", end='')
            print ("%s -" % t, end='')
            for item in tempGetter:
                print ("- %s: %.2f C " % (item.id,  item.temp), end='')
            sys.stdout.flush()
            time.sleep(0.5)
        
        for item in tempGetter:
            item.running = False
        for item in tempGetter:
            item.join()

    except (KeyboardInterrupt, SystemExit):
        for item in tempGetter:
            item.running = False