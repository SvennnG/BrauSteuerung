import os, sys
import time
import random
import threading
import time
from datetime import datetime

class TempEmu(threading.Thread):
    def __init__(self, file='/var/tmp/Px_temp.source'):
        threading.Thread.__init__(self)
        self.file = file
        self.running=True
        self.output=True
        self.temp = 23
        print("\nTempEmu run start!\n  File: %s\n" % self.file)
        
    def run(self):
        cnt = 0
        while self.running:
        
            if self.temp < float(random.randint(55,65)):
                self.temp = self.temp + float(random.randint(10,50)) * 0.01
            else:
                self.temp = self.temp - float(random.randint(10,50)) * 0.005
                
#5f 01 4b 46 7f ff 01 10 9b : crc=9b YES
#5f 01 4b 46 7f ff 01 10 9b t=21937

            #t = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            
            file=open(self.file, 'w')
            file.write("5f 01 4b 46 7f ff 01 10 9b : crc=9b YES\n")
            file.write("5f 01 4b 46 7f ff 01 10 9b t={0:05.0f}\n".format(self.temp*1000))
            file.close()
            
            if cnt % 1 == 0 and self.output == True:
                t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                print ("\r\x1b[K", end='', flush=True)
                print ("%s - " % t, end='', flush=True)
                print("Temp: %.2f" % self.temp, end='', flush=True)
                cnt = 0;
            cnt = cnt + 1
            time.sleep(1)
        print("\nTempEmu run stopped!")

if __name__ == "__main__":
    Temu = TempEmu();
    Temu.start();

    try:
        while 1: 
            time.sleep(0.05)
            
    except (KeyboardInterrupt, SystemExit):
        Temu.running = False