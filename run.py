#!/usr/bin/python	 

#from datetime import datetime
import sys, logging, time, os, traceback
import TempGetter.TempGetter as TempGetter
from LCDDriver.LCDGraphic import LCDGraphic
from LCDDriver.LCDGraphic import States as LCDGraphicStates
import Configuration.ConfManager as ConfManager
import Configuration.ConfManager2 as ConfManager2
import Console.Console as Console
import Heater.Heater as Heater
import Weblog.Weblog as Weblog
from pprint import pprint
import copy

try:
	import Console.graph as Graph
except Exception as ex:
	print("Graph module could not be loaded!", ex)
	
from optparse import OptionParser
import locale

print("\n ### Load Complete! ###\n")

if locale.getpreferredencoding().upper() != 'UTF-8': 
	locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
# How to generate Locales:   
# echo LANG=de_DE.UTF-8 > /etc/locale.conf
# /etc/locale.gen muss das entsprechende locale einkommentiert haben, dann mittels locale-gen ausführen
# locale -a zeigt alle verfügbaren sprachen
	
if os.uname()[4].startswith("arm"):
	# Raspberry PI -s (no pygame)
	foldername = "/home/sven/BrauSteuerung"
	tempSensor1 = "/sys/bus/w1/devices/28-0000074013a8/w1_slave"
	tempSensor2 = "/sys/bus/w1/devices/28-0000073ec998/w1_slave"
else:
	# SVENTOP alway with -e (emulate fot tempsensor)
	foldername = "/home/sven/Documents/BrauSteuerung" 


#profilepath = foldername + "/Configuration/Profile/"
#globalprofilepath = foldername + "/Configuration/Global/"
#logfile = '/home/sven/scripts/Maischen/log/Maischen.log'
logfile = foldername + "/log/Maischen.log"
#defaultconfig =foldername + "/Configuration/default.conf"

updatetimer10s = int(round(time.time() * 1000))

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
parser.add_option("-e", "--emulate", dest="emulate", action="store_true", help="emulate Temperature Sensor by using input File: /var/tmp/Px_temp.source")

(options, args) = parser.parse_args()


#####################
# Console settings
#####################
mystdout = Console.StdOutWrapper()	  # STD out / print to the Wrapper
#sys.stdout = mystdout
#sys.stderr = mystdout 
if options.silent:
	console = Console.Console()
else:
	console = Console.Console(mystdout)	 # without parameter = no extra console, mystdout = console window


#####################
# Logging Settings
#####################
logger = logging.getLogger('Maischen')
hdlr = logging.FileHandler(logfile) 
formatter = logging.Formatter('%(asctime)s %(levelname)s: [%(filename)14s:%(lineno)3s - %(funcName)9s()] %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

#####################
# TempGetter Init
#####################
tempGetter = 0
tempGetter2 = 0

if options.emulate:
	tempSensor1 = '/var/tmp/Px_temp.source'
	tempSensor2 = '/var/tmp/Px_temp.source'

try:
	tempGetter = TempGetter.TempGetter(tempSensor1)	# unten
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
		lcdGraphic = LCDGraphic("virtual")
	else:
		lcdGraphic = LCDGraphic("real")
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
	#confman = ConfManager.ConfManager(profilepath)
	confman = ConfManager.ConfManager("profil")
	globalconfman = ConfManager2.ConfManager2("config")
except:
	print("Configuration Manager init failed!")

def saveGlobal():
	success = 0
	if lcdGraphic.globalconfig["Proportionalbereich.neg"] != globalconfman.getValue("Proportionalbereich.neg"):
		success += globalconfman.setValue("Proportionalbereich.neg", lcdGraphic.globalconfig["Proportionalbereich.neg"])
	if lcdGraphic.globalconfig["Proportionalbereich.pos"] != globalconfman.getValue("Proportionalbereich.pos"):
		success += globalconfman.setValue("Proportionalbereich.pos", lcdGraphic.globalconfig["Proportionalbereich.pos"])
	try:
		heater.linearPos = globalconfman.getValue("Proportionalbereich.pos");
		heater.linearNeg = globalconfman.getValue("Proportionalbereich.neg");
		print("Linearregler Attribute Update: linearNeg = ", heater.linearNeg, "linearPos = ", heater.linearPos)
	except:
		print("Heater didn't get the new settings!")
	return success

try:
	logger.info('Maischen Programm Started.')
	
	try:
		tempGetter.start()
		tempGetter2.start()
	except Exception as ex:
		print("Temp Sensors start failed!", ex)
		
	try:
		weblog = Weblog.Weblog()
	except Exception as ex:
		print("Web Logger start failed!", ex)

	try:
		lcdGraphic.start()
	except:
		print("Display start failed!")
		
	if options.graph:
		try:
			graph.start()
		except:
			print("Temperatur Graph start failed!")
			
	try:
		heater.start()
	except Exception as ex:
		print("Heater start failed!", ex)
	
	try: 
		lcdGraphic.globalconfig["Proportionalbereich.neg"] = globalconfman.getValue("Proportionalbereich.neg");
		lcdGraphic.globalconfig["Proportionalbereich.pos"] = globalconfman.getValue("Proportionalbereich.pos");
		lcdGraphic.globalconfigSavecall = saveGlobal
		
		heater.linearPos = globalconfman.getValue("Proportionalbereich.pos");
		heater.linearNeg = globalconfman.getValue("Proportionalbereich.neg");
		
		# Profilnamen an view geben (profile select, index erstellung zur addressierung)
		pprint(confman.profiles)
		for name in confman.profiles:
			lcdGraphic.profiles.append(name)
			print(name+" added to heater profiles")
		
		# get set fkt an view damit Einstellungen gemacht werden koennen
		lcdGraphic.setGetFkt(confman.getValue)
		lcdGraphic.setSaveFkt(confman.setValue)
		lcdGraphic.setHeaterStatusFkt(heater.status)
	except:
		traceback.print_exc()
		print("Display functions to save/get config init failed!")
					
	try:
		console.start()
	except Exception as ex:
		print("Console start failed!", ex)
		
	lastState = 0
	print("\n ### Start of All Components completed ! ###\n")
	while 1:
		lastUpdate = int(round(time.time() * 1000))
		
		if tempGetter.temp == 0.0:
			tempGetter.temp = tempGetter2.temp
		if tempGetter2.temp == 0.0:
			tempGetter2.temp = tempGetter.temp
		tmp = tempGetter.temp #(tempGetter.temp + tempGetter2.temp) * 0.5

		lcdGraphic.update(tmp)
		
		if lcdGraphic.state.value == 11 and lastState != 11:
			weblog.log(tmp, lcdGraphic.valueTemp, 1)
			print(" Weblog new Dataset!")
		elif lcdGraphic.state.value >= 11 and lcdGraphic.state.value <= 17: #LCDGraphic.LCDGraphic.States is running
			# 11 = preHeating
			# 17 = Rast3
			# 18 = Done
			if heater.isHeating == False:
				heater.activate()
			heater.updateTargetTemperature(lcdGraphic.valueTemp)
			heater.update(tmp) 
			weblog.log(tmp, lcdGraphic.valueTemp)
		elif lcdGraphic.state.value == 18:
			if heater.isHeating == False:
				heater.activate()
			heater.updateTargetTemperature(20.0)
			heater.update(tmp) 
			weblog.log(tmp, 20)
		elif heater.isHeating:
			heater.deactivate()
			weblog.log(tmp, 0)
		else:
			weblog.log(tmp, 0)
		
		lastState = lcdGraphic.state.value
		console.temp = tmp
		
		if lcdGraphic.wantsToExit:
			raise LCDExitException
		
		# UPDATE alle 10s um profile und setting neu zu laden und upzudaten
		if int(round(time.time() * 1000)) > updatetimer10s:
			updatetimer10s = int(round(time.time() * 1000)) + 10000
			if lcdGraphic.state != LCDGraphicStates.globalconf1 and lcdGraphic.state != LCDGraphicStates.globalconf2:
				globalconfman.updateValues();
				lcdGraphic.globalconfig["Proportionalbereich.neg"] = globalconfman.getValue("Proportionalbereich.neg");
				lcdGraphic.globalconfig["Proportionalbereich.pos"] = globalconfman.getValue("Proportionalbereich.pos");
				heater.linearPos = globalconfman.getValue("Proportionalbereich.pos");
				heater.linearNeg = globalconfman.getValue("Proportionalbereich.neg");
			if lcdGraphic.state.value > 6 or lcdGraphic.state.value == 0:
				previous = copy.deepcopy(confman.profiles)
				confman.updateProfiles();
				for name in confman.profiles:	# Fuege neue Profile hinzu
					if name not in previous:
						lcdGraphic.profiles.append(name)
						print("New Profile!: "+name+" added to Profiles")
				for name in confman.profiles:	# aktualisiere werte in alten profilen 
					for item, value in confman.profiles[name].items():
						if (previous[name][item] != value):
							print("################# Wert des Profils "+ name +" hat sich geändert!:"+item +" = "+ str(value))
							print(lcdGraphic.state)
							print((LCDGraphicStates.preHeat, LCDGraphicStates.preHeatComplete, LCDGraphicStates.Rast1 ))
							if lcdGraphic.state in (LCDGraphicStates.preHeat, LCDGraphicStates.preHeatComplete, LCDGraphicStates.Rast1 ):
								lcdGraphic.valueTemp = int(lcdGraphic.getSett(1)) #1. Rast / preheat    temp
								lcdGraphic.valueTime = int(lcdGraphic.getSett(2)) #1. Rast / preheat    dauer
							elif lcdGraphic.state in (LCDGraphicStates.Rast2, LCDGraphicStates.HeatRast2):
								lcdGraphic.valueTemp = int(lcdGraphic.getSett(3)) #2. Rast / preheat    temp
								lcdGraphic.valueTime = int(lcdGraphic.getSett(4)) #2. Rast / preheat    dauer
							elif lcdGraphic.state in (LCDGraphicStates.Rast3, LCDGraphicStates.HeatRast3):
								lcdGraphic.valueTemp = int(lcdGraphic.getSett(5)) #3. Rast / preheat    temp
								lcdGraphic.valueTime = int(lcdGraphic.getSett(6)) #3. Rast / preheat    dauer
			
		# je 100ms update
		while int(round(time.time() * 1000)) < lastUpdate + 100:
			time.sleep(0.05)

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
	traceback.print_exc()
	sys.exit(7)
	
sys.exit(0)
