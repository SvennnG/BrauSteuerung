#!/usr/bin/python

import time
import threading
import logging
import re
import sys
#from Reader import tail

class TempGetter(threading.Thread):
    def __init__(self, file='/var/tmp/Px_temp.source'):
        threading.Thread.__init__(self)
            
        self.file=file
        self.running=True
        self.output=True	# output to logger
        self.logger = logging.getLogger('Maischen')
        self.temp = 0.0
        self.debug = False	# exception printing
        
        print("#TempGetter [" + file + "] initialized")
    def run(self):
        cnt = 0
        while self.running:
            self.temp = float(self.read_sensor())
            if self.temp == False:
                self.temp = 0.0
                self.logger.warning('IO Error: read file %s failed!' % self.file)
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
        
        if float(value) == 85.0:    # if connection error on sensor cable -> this is a error code, return last known temperature
            return self.temp
        return value

