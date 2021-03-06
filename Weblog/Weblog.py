#!/usr/bin/python
import _thread, time, sys
import datetime    
from time import sleep

try:
    import Weblog.Send as Websend
except Exception as ex:
	print("No WEB LOG Module loaded!", ex)


class Weblog():
    def __init__(self):
        self.first = "1"
        self.time = datetime.datetime.now()
        print("#Weblog initialized!")

    def log(self, temp, zieltemp, first = 0):
        try:
            if first == "1" or first == 1:
                self.first = 1
                
            if (datetime.datetime.now() - self.time).total_seconds() < 1:
                return
                
            temp = "%.2f" % temp
            time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            zieltemp = "%.2f" % zieltemp
            
            
            _thread.start_new_thread( Websend.SendToDB, (temp, zieltemp, time, str(self.first)) )
            # Websend.SendToDB(temp, zieltemp, time, self.first)
            
            self.time = datetime.datetime.now()
            self.first = "0"
        except Exception as ex:
            print("could not log to website!", ex)


