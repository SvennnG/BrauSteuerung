#!/usr/bin/python 
import time, codecs


# Config-Files: line by Line
#
# Name der Configuration          String  identisch mit Name der Datei! (zum schreiben)
# 1. Rast / Vorheiztemperatur     in C   ohne nachkommastellen (int)
# 1. Rast Dauer                   in min
# 2. Rast                         in C   ohne nachkommastellen (int)
# 2. Rast Dauer                   in min
# 3. Rast                         in C   ohne nachkommastellen (int)
# 3. Rast Dauer                   in min
# 

def read(configfile = ""):
    if configfile == "":
        print("ConfLoader Error! No File specified!")
        return
        
    try:
        #f = open(configfile, "r", encoding='utf-8', errors='ignore')
        f = codecs.open(configfile,'r',encoding='utf-8')
        
        num_lines = sum(1 for line in codecs.open(configfile,'r',encoding='utf-8')) # count an dateien
        
        bier_name = f.readline()
        r1_temp = int(float(f.readline()))
        r1_time = int(float(f.readline()))
        r2_temp = int(float(f.readline()))
        r2_time = int(float(f.readline()))
        
        if (num_lines <= 5) :
            r3_temp = r2_temp
            r3_time = 0
        else :
            r3_temp = int(float(f.readline()))
            r3_time = int(float(f.readline()))
        
        f.close()
        
        return (bier_name[:-1], r1_temp, r1_time, r2_temp, r2_time, r3_temp, r3_time)
    except IOError as e:
        print(time.strftime("%x %X"), ", Error reading '", configfile, "': ", e)
    
# Config-File: line by Line, Only 1 FILE!
#
# Proportionalbereich.neg: <int>
# Proportionalbereich.pos: <int>
# 
def readGlobal(configfile = ""):
    if configfile == "":
        print("ConfLoader Error! No File specified!")
        return
        
    try:
        f = codecs.open(configfile,'r',encoding='utf-8')
        #num_lines = sum(1 for line in codecs.open(configfile,'r',encoding='utf-8')) # count an dateien
        
        pbneg = f.readline()
        identifier = 'Proportionalbereich.neg: '
        if not pbneg.startswith(identifier):
            f.close()
            raise Exception("Proportionalbereich.neg ist nicht erste Zeile!")
        pbneg = float(pbneg[len(identifier):])
        
        pbpos = f.readline()
        identifier = 'Proportionalbereich.pos: '
        if not pbpos.startswith(identifier):
            f.close()
            raise Exception("Proportionalbereich.pos ist nicht zweite Zeile!")
        pbpos = float(pbpos[len(identifier):])
        
        f.close()
        return (pbneg, pbpos)
    except IOError as e:
        print(time.strftime("%x %X"), ", Error reading Global Config! '", configfile, "': ", e)
    
