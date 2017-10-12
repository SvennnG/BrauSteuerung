#!/usr/bin/python     

#from datetime import datetime
import sys, logging, time, os
import TempGetter.TempGetter as TempGetter
import LCDDriver.LCDGraphic as LCDGraphic
import Configuration.ConfManager as ConfManager
import Console.Console as Console
import Heater.Heater as Heater
import Weblog.Weblog as Weblog
try:
    import console.graph as Graph
except Exception as ex:
    print("Graph module could not be loaded!", ex)
    
from optparse import OptionParser
import locale

if locale.getpreferredencoding().upper() != 'UTF-8': 
    locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
# How to generate Locales:   
# echo LANG=de_DE.UTF-8 > /etc/locale.conf
# /etc/locale.gen muss das entsprechende locale einkommentiert haben, dann mittels locale-gen ausführen
# locale -a zeigt alle verfügbaren sprachen
    
    
# SVENTOP
profilepath = "/home/sven/Documents/Maischen/Configuration/Profile/"
globalprofilepath = "/home/sven/Documents/Maischen/Configuration/Global/"
#logfile = '/home/sven/scripts/Maischen/log/Maischen.log'
logfile = '/home/sven/Documents/Maischen/log/Maischen.log'
defaultconfig = '/home/sven/Documents/Maischen/Configuration/default.conf'


# Raspberry PI
foldername = "BrauSteuerung" # Maischen
profilepath = "/home/sven/" + foldername + "/Configuration/Profile/"
globalprofilepath = "/home/sven/" + foldername + "/Configuration/Global/"
#logfile = '/home/sven/scripts/Maischen/log/Maischen.log'
logfile = "/home/sven/" + foldername + "/log/Maischen.log"
defaultconfig = "/home/sven/" + foldername + "/Configuration/default.conf"




tempSensor1 = "/sys/bus/w1/devices/28-0000074013a8/w1_slave"
tempSensor2 = "/sys/bus/w1/devices/28-0000073ec998/w1_slave"


#####################
# Options settings
#####################
parser = OptionParser()
    
def optional_arg(arg_default):
    def func(option,opt_str,value,parser):
        if parser.rargs and not parser.rargs[0].startswith('-'):
            val=parser.rargs[0]
            parser.rargs.pop(0)
        else:
            val=arg_default
        setattr(parser.values,option.dest,val)
    return func

#parser.add_option("-v", "--virtual", action='callback',callback=optional_arg('255'), dest="red", help="to open the Diaply as a virtual 
#Emulated Display")
# option arg steht in options.red (dest)
parser.add_option("-v", "--virtual", dest="virtual", action="store_true", help="to open the Diaply as a virtual Emulated Display")
parser.add_option("-g", "--graph", dest="graph", action="store_true", help="to open a pygame window with the graph of temperature")
parser.add_option("-s", "--silent", dest="silent", action="store_true", help="show without 'console' window. like a typical cmdline program with this option")

(options, args) = parser.parse_args()


#####################
# Console settings
#####################
mystdout = Console.StdOutWrapper()      # STD out / print to the Wrapper
#sys.stdout = mystdout
#sys.stderr = mystdout 
if options.silent:
    console = Console.Console()
else:
    console = Console.Console(mystdout)     # without parameter = no extra console, mystdout = console window


#####################
# Logging Settings
#####################
logger = logging.getLogger('Maischen')
hdlr = logging.FileHandler(logfile) 
formatter = logging.Formatter('%(asctime)s %(levelname)s: [%(filename)14s:%(lineno)3s - %(funcName)9s()] %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

# WEBlog (temp, zieltemp, time, first)
weblog = Weblog.Weblog()

#####################
# TempGetter Init
#####################
tempGetter = 0
tempGetter2 = 0
try:
    tempGetter = TempGetter.TempGetter(tempSensor1)    # unten
    tempGetter2 = TempGetter.TempGetter(tempSensor1)
except Exception as ex:
    print("TempGetter init failed! cannot run! Exit", ex)
if tempGetter == 0 or tempGetter2 == 0:
    sys.exit(4)

#####################
# Heater Init
#####################
heater = 0
try:
    heater = Heater.Heater()
except Exception as ex:
    print("Heater init failed! cannot run! Exit", ex)
if heater == 0:
    sys.exit(3)

#####################
# Display Init
#####################
lcdGraphic = 0
try:
    if options.virtual:
        lcdGraphic = LCDGraphic.LCDGraphic("virtual")
    else:
        lcdGraphic = LCDGraphic.LCDGraphic("real")
except Exception as ex:
    print("Display init failed! cannot run! Exit", ex)
if lcdGraphic == 0:
    print("LCDGraphic is zero! EXIT!")
    exit(2)

if options.graph:
    try:
        graph = Graph.Graph()
    except Exception as ex:
        print("Temperatur Graph init failed!", ex)
        options.graph = False
            
class LCDExitException(Exception):
    pass
    
#####################
# Configuration Files Init
#####################
confman = 0
try:
    confman = ConfManager.ConfManager(profilepath)
    globalconfman = ConfManager.ConfManager(globalprofilepath, "globalConfig")
except:
    print("Configuration Manager init failed!")

def saveGlobal():
    success = 0
    if lcdGraphic.globalconfig[0][1] != globalconfman.profiles[0][2]:
        success += globalconfman.setGlobalValue("globalConfig", 1, lcdGraphic.globalconfig[0][1])
    if lcdGraphic.globalconfig[1][1] != globalconfman.profiles[0][3]:
        success += globalconfman.setGlobalValue("globalConfig", 2, lcdGraphic.globalconfig[1][1])
    try:
        heater.linearPos = globalconfman.profiles[0][3]
        heater.linearNeg = globalconfman.profiles[0][2]
        print("Linearregler Attribute Update: linearNeg = ", heater.linearNeg, "linearPos = ", heater.linearPos)
    except:
        print("Heater didn't get the new settings!")
    return success

try:
    logger.info('Maischen Programm Started.')

    try:
        console.start()
    except Exception as ex:
        print("Console start failed!", ex)
        
    try:
        tempGetter.start()
        tempGetter2.start()
    except Exception as ex:
        print("Temp Sensors start failed!", ex)
        
    try:
        heater.start()
    except Exception as ex:
        print("Heater start failed!", ex)
    
    try:
        #globalconfman.setValue("globalConfig", 0|1|..., value) 0 = pb.neg, 1 = pb.pos
        lcdGraphic.globalconfig[0][1] = globalconfman.profiles[0][2]
        lcdGraphic.globalconfig[1][1] = globalconfman.profiles[0][3]
        lcdGraphic.globalconfigSavecall = saveGlobal
        
        # Profilnamen an view geben (profile select, index erstellung zur addressierung)
        #profl = confman.getProfileNames()
        for tpl in confman.profl:
            lcdGraphic.profiles.append(str(tpl))
        
        # get set fkt an view damit Einstellungen gemacht werden koennen
        lcdGraphic.setGetFkt(confman.getValue)
        lcdGraphic.setSaveFkt(confman.setValue)
        lcdGraphic.setHeaterStatusFkt(heater.status)
        
        # save global settings to heater
        saveGlobal()
    except:
        print("Display functions to save/get config init failed!")
        
    try:
        lcdGraphic.start()
    except:
        print("Display start failed!")
    
    if options.graph:
        try:
            graph.start()
        except:
            print("Temperatur Graph start failed!")
            
    while 1:
        lastUpdate = int(round(time.time() * 1000))
        
        
        if tempGetter.temp == 0.0:
            tempGetter.temp = tempGetter2.temp
        if tempGetter2.temp == 0.0:
            tempGetter2.temp = tempGetter.temp
        tmp = tempGetter.temp #(tempGetter.temp + tempGetter2.temp) * 0.5

        lcdGraphic.update(tmp)
        
        if lcdGraphic.state.value >= 11 and lcdGraphic.state.value <= 17: #LCDGraphic.LCDGraphic.States is running
            # 11 = preHeating
            # 17 = Rast3
            # 18 = Done
            if heater.isHeating == False:
                heater.activate()
            heater.updateTargetTemperature(lcdGraphic.valueTemp)
            heater.update(tmp) 
            weblog.log(tmp, lcdGraphic.valueTemp)
        elif heater.isHeating:
            heater.deactivate()
            weblog.log(tmp, 0)
        else:
            weblog.log(tmp, 0)
        
        console.temp = tmp
        
        if lcdGraphic.wantsToExit:
            raise LCDExitException
        
        # je 100ms update
        while int(round(time.time() * 1000)) < lastUpdate + 100:
            time.sleep(0.05)
        

    if options.graph:
        graph.running = False
    logger.info('Maischen Stoped naturally!')
    tempGetter.running = False
    tempGetter2.running = False
    lcdGraphic.running = False
    heater.running = False
    tempGetter.join()
    tempGetter2.join()
    lcdGraphic.join()
    heater.join()
    console.running = False
    console.join()

except (KeyboardInterrupt, SystemExit):
    if options.graph:
        graph.running = False
    tempGetter.running = False
    tempGetter2.running = False
    lcdGraphic.running = False
    heater.adjust(0.0)
    heater.deactivate()
    heater.running = False
    console.running = False
    console.join()
    lcdGraphic.join()
    print("\nProgramm end.")
    logger.info('Maischen Stoped. All Shut down...')
    sys.exit(6)
    
except LCDExitException:
    if options.graph:
        graph.running = False
    tempGetter.running = False
    tempGetter2.running = False
    lcdGraphic.running = False
    heater.adjust(0.0)
    heater.deactivate()
    heater.running = False
    console.running = False
    console.join()
    lcdGraphic.join()
    print("\nProgramm end. USER Input")
    logger.info('Maischen Stoped by USER Input. SHUTDOWN now')
    
    os.system("sleep 2 && sudo shutdown -h now")
    sys.exit(6)
    
    
except Exception as err:
    if options.graph:
        graph.running = False
    tempGetter.running = False
    tempGetter2.running = False
    lcdGraphic.running = False
    heater.adjust(0.0)
    heater.deactivate()
    heater.running = False
    console.running = False
    console.join()
    print("\nProgramm end. why...? %s" % err)
    logger.info('Maischen interesting...')
    logger.info(err)
    sys.exit(7)
    


sys.exit(0)
