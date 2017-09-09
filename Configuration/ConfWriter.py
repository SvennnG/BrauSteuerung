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

def write(set, configfile=""):
    if configfile == "":
        print("ConfLoader Error! No File specified!")
        return
        
    try:
        #f = open(configfile, "w")
        f = codecs.open(configfile,'w',encoding='utf-8')
        skipfirst = True    # dateiname
        for item in set:
            #print "writing: " + str(item)
            if skipfirst:
                skipfirst = False
                continue
            string = str(item) + '\n'
            f.write(string)
        f.close()
    except IOError as e:
        print(time.strftime("%x %X"), ", Error writing '", configfile, "': ", e)
    

def writeGlobalConfig(set, configfile=""):
    if configfile == "":
        print("ConfLoader Error! No File specified!")
        return
        
    try:
        #f = open(configfile, "w")
        f = codecs.open(configfile,'w',encoding='utf-8')
        
        naming = ['', '', 'Proportionalbereich.neg: ', 'Proportionalbereich.pos: ']
        cnt = 0
        for item in set:
            if cnt < 2:
                cnt = cnt + 1
                continue
            string = naming[cnt] + str(item) + '\n'
            f.write(string)
            cnt = cnt + 1
        f.close()
        return 1
    except IOError as e:
        print(time.strftime("%x %X"), ", Error writing '", configfile, "': ", e)
        return -999
