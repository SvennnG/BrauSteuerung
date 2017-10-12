import os
import time
import random
import threading
import time
from datetime import datetime

class TempEmu(threading.Thread):
    def __init__(self, file='/var/tmp/Px_temp.source'):
        threading.Thread.__init__(self)
        self.file=open(file, 'w', 0)
        self.running=True
        self.output=True
        self.temp = 23
        
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
            self.file.write("5f 01 4b 46 7f ff 01 10 9b : crc=9b YES\n")
            self.file.write("5f 01 4b 46 7f ff 01 10 9b t={0:05.0f}\n".format(self.temp*1000))
            
            if cnt % 10 and self.output == True:
                print("Temp set (10. step) : %.2f" % self.temp)
            cnt = cnt + 1
            time.sleep(0.1)
        print "TempEmu run stopped!"

if __name__ == "__main__":
	Temu = TempEmu();
	Temu.start();

    try:
        while 1: 
            time.sleep(0.05)
            
    except (KeyboardInterrupt, SystemExit):
        Temu.running = False