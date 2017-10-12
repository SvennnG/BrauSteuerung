#!/usr/bin/python
import thread, time, sys
import datetime    
from time import sleep

try:
    import Weblog.send as Websend
except Exception as ex:
	print("No WEB LOG Module loaded!", ex)


class Weblog():
    def __init__(self):
        self.first = 1

    def log(self, temp, zieltemp):
        try:
            if (self.time - datetime.datetime.now()).total_seconds() < 1:
                return
                
            temp = "%.2f" % temp
            time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            zieltemp = "%.2f" % zieltemp
            
            thread.start_new_thread( Websend.SendToDB, (temp, zieltemp, time, self.first) )
            # Websend.SendToDB(temp, zieltemp, time, self.first)
            
            self.time = datetime.datetime.now()
            self.first = 0
        except Exception as ex:
            print("could not log to website!", ex)


