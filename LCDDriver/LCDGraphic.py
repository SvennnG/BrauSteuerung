#!/usr/bin/python   

import threading, time, sys
from enum import Enum
from LCDDriver.Adafruit.Adafruit_CharLCDPlate import Adafruit_CharLCDPlate

try:
    from LCDDriver.Virtual_CharLCDPlate import Virtual_CharLCDPlate
except:
    print("Virtual Display module could not be loaded!")
    
import logging

TIME_TO_REINTERPRET_KEY_PRESSED = 300 	# ms
TIME_BACKLIGHT_ACK = 300        		# ms
ACCEPT_TEMPERATUR_RANGE = 0.8   		# C to accept actual temperatur as goal
PROFILESCROLLTIMERINIT = 1250   		# ms
PROFILESCROLLTIMERINC = 450     		# ms


class LCDGraphic(threading.Thread):
		
	class States(Enum):
		Main = 0
		Sett1 = 1   # nicht aendern -> index der zu schreibenden/lesenden werte aus config
		Sett2 = 2   #
		Sett3 = 3   #
		Sett4 = 4   #
		Sett5 = 5   #
		Sett6 = 6   #
		ProfileSelect = 9 # for settings
		
		ProfileSelect2 = 10 # for start
		preHeat = 11            #
		preHeatComplete = 12    #
		Rast1 = 13              #
		HeatRast2 = 14          #
		Rast2 = 15              #
		HeatRast3 = 16          #
		Rast3 = 17              #
		Done = 18               #
		
		globalconf1 = 19        # global conf
		globalconf2 = 20
		
	class mainMenuItems(Enum):
		Start = 0
		Profiles = 1
		Settings = 2
		Shutdown = 3
		#Reset = 4
			
	def __init__(self, lcd="virtual"):
		threading.Thread.__init__(self)
		
		self.logger = logging.getLogger('Maischen')

		self.running=True
		self.tmp = 0.0  # aktuelle Temperatur (immer oben link)
		self.current_milli_time = lambda: int(round(time.time() * 1000))
		self.current_secs_time = lambda: int(round(time.time()))
		
		# um mehrfacherkennungen zu vermeiden / alle x ms
		self.prevButtonPressed = self.current_milli_time()
		
		# getter setter der einstellungen. muss in run.py gesetzt werden
		self.call_fkt_save = lambda name, sett, value: sys.stdout.write(" --- call function not yet set! (Profile: %s, %d @sett-id: %d) --- " % (name, value, sett))
		self.call_fkt_get = lambda name, sett: sys.stdout.write(" --- get function not yet set! (Profile: %s @sett-id: %d) --- " % (name, sett))
		
		# funktion um den heater abzufragen. muss in run.py gesetzt werden
		self.heaterStatus  = lambda: "?"
					
		# unterschiedliche einstellungen nutzen diesen wert der in der main in die konfigurationen uebertragen wird
		self.value = 0.0 
		
		#time and temp for maischen (after start use)
		self.valueTemp = 0.0    # ziel temperatur in celsius
		self.valueTime = 0.0    # dauer in sec
		self.countdown = 0.0    # countdown beim rasten. 00:00 min am ende!
		
		# profil der bier konfigurationen
		self.profile = "default"
		self.profileId = 0
		self.profiles = [] # is filled by run on start, contain names
		
		# global config
		self.globalconfig = [["Proportionalbereich.neg",0],["Proportionalbereich.pos",0]]
		self.globalconfigSavecall = lambda: print(" --- save function global conf not yet set! --- ")
		
		# set by self.shutown / called by mainmenu "Beenden"
		self.wantsToExit = False
		
		# timer fuer zu lange display namen der Profile
		self.profileScrollTimer = 0.0
		self.profileScrollCounter = 0
		
		# aktueller state +  mapping der entsprechenden Funktionen die diesen Status Rendern
		self.state = self.States.Main
		self.statemachine = {self.States.Main : self.view_main,
							 self.States.Sett1 : self.view_sett1, 
							 self.States.Sett2 : self.view_sett2, 
							 self.States.Sett3 : self.view_sett3,
							 self.States.Sett4 : self.view_sett4,
							 self.States.Sett5 : self.view_sett5,
							 self.States.Sett6 : self.view_sett6,
							 self.States.ProfileSelect : self.view_profilSelect,
							 
							 self.States.ProfileSelect2 : self.view_profilSelect2,
							 self.States.preHeat : self.view_preHeat,
							 self.States.preHeatComplete : self.view_preHeatComplete,
							 self.States.Rast1 : self.view_Rast1,
							 self.States.HeatRast2 : self.view_HeatRast2,
							 self.States.Rast2 : self.view_Rast2,
							 self.States.HeatRast3 : self.view_HeatRast3,
							 self.States.Rast3 : self.view_Rast3,
							 self.States.Done : self.view_Done,
							 
							 self.States.globalconf1 : self.view_globalconf1,
							 self.States.globalconf2 : self.view_globalconf2,
							 }
		
		# mainmenu state
		self.mainMenuSelect = self.mainMenuItems.Start
		
		# LCD or VirtualView, parameter for Init function!
		self.lcdChoise = lcd
		self.initLCD()
		
	def globalconfigSave(self):
		status = self.globalconfigSavecall()
		if status > 0:
			self.ack_ok()
		elif status < 0:
			self.ack_error()
			
	def shutdown(self):
		self.wantsToExit = True
			
	def initLCD(self):

		if self.lcdChoise == "virtual":
			print("- Using virtual LCD Display")
			self.lcd = Virtual_CharLCDPlate()
		elif self.lcdChoise == "real":
			print("- Using real LCD Display")
			
			self.lcd = Adafruit_CharLCDPlate()
			self.lcd.stop()
			self.lcd = Adafruit_CharLCDPlate()
		else:
			print("==> lcd need to specified virtual|real ! (Assuming virtual)")
			self.lcd = Virtual_CharLCDPlate()
			
		# LCD settings
		numcolumns = 16
		numrows = 2
#		self.lcd.stop()

		self.lcd.begin(numcolumns, numrows)
		self.lcd.clear()
		self.lcd.backlight(self.lcd.RED)
		
		# http://symlink.dk/electro/hd44780/lcd-font.png
		# Charsize: 5x8
		# LCDsize: 16x2
		# PixelSize: 80x16
		# eigene Zeichen: http://www.quinapalus.com/hd44780udg.html
		#
		# CharCodes 
		#       ab  Hex(7B) Dec(123)    (nur china zeichen danach) 
		#       bis Hex(20) Dec(32)     (ohne verwendung. 20/32 ist [SPACE]) http://ascii.cl/
		#
		# 00 : Grad-Symbol          \x00    \xdf   (mehr eckig)
		# 01 : heizen               \x01
		# 02 : kuehlen              \x02
		# 03 : Wahlmglk. oben/unten \x03
		# 04 : ok (pfeil rechts)    \x04    \x7e
		# 05 : wahl links/rechts    \x05
			# 05 : setting              \x05
			#self.lcd.createChar(5, [0,21,14,27,14,21,0,0])		
		# 06 : wenig heizen         \x06    \x5e
		# 07 : s-z Umlaut           \x07    
		#
		# umlaute:  \xf5    => ue
		#           \xe1    => ae
		#           \xef    => oe
		
		self.lcd.createChar(0, [0b01100,0b10010,0b10010,0b01100,0b00000,0b00000,0b00000,0b00000])
		self.lcd.createChar(1, [0,4,10,17,4,10,17,0])
		self.lcd.createChar(2, [0,17,10,4,17,10,4,0])
		self.lcd.createChar(3, [4,14,21,4,4,21,14,4])
		self.lcd.createChar(4, [0,0,4,2,29,2,4,0])
		self.lcd.createChar(5, [0,10,27,31,27,10,0])
		self.lcd.createChar(6, [0,4,10,17,0,0,0,0])
		self.lcd.createChar(7, [6,15,25,26,27,25,26,24])

		self.col = (self.lcd.RED , self.lcd.YELLOW, self.lcd.GREEN, self.lcd.TEAL,
			   self.lcd.BLUE, self.lcd.VIOLET, self.lcd.ON   , self.lcd.OFF)
		self.colnames = ("red", "yellow", "green", "teal", "blue", "violet", "normal", "off")
		
		# um x ms das Backlight des Displays einzustellen hier der timer
		self.resetLCDtoNormalTimer = 0
		self.lcd.backlight(self.lcd.ON)
		print("#Display initialized")
		
	def run(self):
		self.initLCD()
        
		while self.running:	
			try:
				# execute render function for current state
				self.statemachine[self.state]()

				if (self.lcd.getBackgroundColor() != self.lcd.ON and self.resetLCDtoNormalTimer > 0):
					if (self.resetLCDtoNormalTimer - self.current_milli_time() < 0):
						self.lcd.backlight(self.lcd.ON)
						self.resetLCDtoNormalTimer = 0
						
				offset = ACCEPT_TEMPERATUR_RANGE #0.3
				# STATE Switch bases on Temperature / Time
				# Switch between States, depending on Timer / Temperature
				if self.state == self.States.preHeat:        # preHeat
					if self.tmp >= self.valueTemp - offset and self.tmp <= self.valueTemp + offset :
						self.state = self.States.preHeatComplete
						print ("preHeating complete. Ready for Rast 1!")
						
				elif self.state == self.States.Rast1:      # rast1 
					if self.countdown - self.current_secs_time() <= 0:
						self.state = self.States.HeatRast2
						self.valueTemp = int(self.getSett(3)) #2. Rast / preheat    temp    vom aktellen Profil holen
						self.valueTime = int(self.getSett(4)) #2. Rast / preheat    dauer   vom aktellen Profil holen
						print ("Rast 1 complete. Continue to heat to Rast 2")
						
				elif self.state == self.States.HeatRast2:      # HeatRast2
					if self.tmp >= self.valueTemp - offset and self.tmp <= self.valueTemp + offset :
						self.state = self.States.Rast2
						self.countdown = self.current_secs_time() + self.valueTime * 60
						print ("Heating to Rast 2 complete. Timer for Rast 2 started")
						
				elif self.state == self.States.Rast2:      # Rast2
					if self.countdown - self.current_secs_time() <= 0:
						self.state = self.States.HeatRast3
						self.valueTemp = int(self.getSett(5)) #3. Rast / preheat    temp
						self.valueTime = int(self.getSett(6)) #3. Rast / preheat    dauer
						print ("Rast 2 complete. Continue to heat to Rast 3")
						
				elif self.state == self.States.HeatRast3:      # HeatRast3
					if self.tmp >= self.valueTemp - offset and self.tmp <= self.valueTemp + offset :
						self.state = self.States.Rast3
						self.countdown = self.current_secs_time() + self.valueTime * 60
						print ("Heating to Rast 3 complete. Timer for Rast 3 started")
						
				elif self.state == self.States.Rast3:      # Rast3
					if self.countdown - self.current_secs_time() <= 0:
						self.state = self.States.Done
						print ("Rast 3 complete. Done!")
						
				time.sleep(0.05)
			except Exception as ex:	
				self.logger.warning("LCD Display received exception!", ex)
			
			if self.lcd.hasError():
				time.sleep(1)	# 1 sec before retry of init
				print("LCD Error. trying to re-initialize...")
				try:
					self.initLCD()
				except:
					continue
				print("LCD Error!?. exception while updating display. Next function should report the re-init of lcd!")
				time.sleep(2)	# 1 sec before retry of init
				try:
					self.logger.warning("LCD Display trying to restart")
					self.initLCD()
				except:
					self.logger.warning("LCD Display restart failed")
					
			#time.sleep(0.02)
		self.lcd.backlight(self.lcd.OFF)
		self.lcd.clear()
		self.lcd.stop()

	def error(self):
		self.lcd.backlight(self.lcd.RED)
		
	def warning(self):
		self.lcd.backlight(self.lcd.TEAL)
		
	def normal(self):
		self.lcd.backlight(self.lcd.ON)
		
	def ack_error(self):
		self.lcd.backlight(self.lcd.RED)
		self.resetLCDtoNormalTimer = self.current_milli_time() + TIME_BACKLIGHT_ACK
		
	def ack_ok(self):
		self.lcd.backlight(self.lcd.GREEN)
		self.resetLCDtoNormalTimer = self.current_milli_time() + TIME_BACKLIGHT_ACK
		
	def update(self, temp):
		self.tmp = temp

	def isLeftButtonPressed(self):
		if self.lcd.buttonPressed(self.lcd.LEFT):
			if self.current_milli_time()-self.prevButtonPressed > TIME_TO_REINTERPRET_KEY_PRESSED:
				self.prevButtonPressed = self.current_milli_time()
				return True
		return False

	def isRightButtonPressed(self):
		if self.lcd.buttonPressed(self.lcd.RIGHT):
			if self.current_milli_time()-self.prevButtonPressed > TIME_TO_REINTERPRET_KEY_PRESSED:
				self.prevButtonPressed = self.current_milli_time()
				return True
		return False

	def isUpButtonPressed(self):
		if self.lcd.buttonPressed(self.lcd.UP):
			if self.current_milli_time()-self.prevButtonPressed > TIME_TO_REINTERPRET_KEY_PRESSED:
				self.prevButtonPressed = self.current_milli_time()
				return True
		return False

	def isDownButtonPressed(self):
		if self.lcd.buttonPressed(self.lcd.DOWN):
			if self.current_milli_time()-self.prevButtonPressed > TIME_TO_REINTERPRET_KEY_PRESSED:
				self.prevButtonPressed = self.current_milli_time()
				return True
		return False

	def isBackButtonPressed(self):
		if self.lcd.buttonPressed(self.lcd.SELECT):
			if self.current_milli_time()-self.prevButtonPressed > TIME_TO_REINTERPRET_KEY_PRESSED:
				self.prevButtonPressed = self.current_milli_time()
				return True
		return False
		
	def setHeaterStatusFkt(self,  call_fkt):
		self.heaterStatus = call_fkt

	def setSaveFkt(self, call_fkt):
		self.call_fkt_save = call_fkt

	def saveSett(self):
		if self.call_fkt_get(self.profile, self.state.value) != self.value:
			if (self.call_fkt_save(self.profile, self.state.value, self.value) == False):
				self.ack_error()
			else:
				self.ack_ok()

	def setGetFkt(self, call_fkt):
		self.call_fkt_get = call_fkt
			
	# Aus dem aktuellen Profil eine Einstellung abrufen (z.b. ID 0 für den Namen)
	# falls sinnlos wird das backlight in ack_error() rot aufleuchten
	def getSett(self, settID = -1):
		if settID == -1:
			val = self.call_fkt_get(self.profile, self.state.value)
		else:
			val = self.call_fkt_get(self.profile, settID)
			
		if val is None:
			print ("getSett returned a nonesens value")
			self.ack_error()
			return 0
		return val 

	#############################################################################################################
	# RENDER views
	#############################################################################################################

	def view_main(self):
		self.lcd.setCursor(0,0)
		self.lcd.message("%2.1f\x00C          " % float(self.tmp))
		
		self.lcd.setCursor(0,1)
		self.lcd.message("\x03 ") # updown pfeil
		items = ( "Beginnen\x04     ","ProfilesSett.\x04", "Einstellungen\x04", "Beenden\x04      ")#, "Reset\x04        ")
		self.lcd.message(items[self.mainMenuSelect.value])
		
		if self.isLeftButtonPressed():
			print ("left pressed - nothing to do in main view")
			
		elif self.isRightButtonPressed():
			print ("right pressed - select")
			if self.mainMenuSelect == self.mainMenuItems.Start:
				self.state = self.States.ProfileSelect2
				self.profileScrollCounter = 0
				self.profileScrollTimer = self.current_milli_time() + PROFILESCROLLTIMERINIT
				print ("start selected. to profile select 2")
			if self.mainMenuSelect == self.mainMenuItems.Shutdown:
				self.profileScrollCounter = 0
				self.profileScrollTimer = self.current_milli_time() + PROFILESCROLLTIMERINIT
				self.shutdown()
				print ("SHUTDOWN")
			elif self.mainMenuSelect == self.mainMenuItems.Profiles:
				self.state = self.States.ProfileSelect
				self.profileScrollCounter = 0
				self.profileScrollTimer = self.current_milli_time() + PROFILESCROLLTIMERINIT
				print ("Profile Settings opened - profilwahl")
			#~ elif self.mainMenuSelect == self.mainMenuItems.Reset:
				#~ self.mainMenuSelect = self.mainMenuItems.Start
				#~ self.state = self.States.Main
				#~ self.profileId = 0
				#~ self.profile = self.profiles[self.profileId]
				#~ self.lcd.clear()
				#~ self.ack_ok()
				#~ print ("Reset... \n Configuraton "+self.profile+" is selected\n State = Main Menu")
			elif self.mainMenuSelect == self.mainMenuItems.Settings:
				self.state = self.States.globalconf1
				self.profileScrollCounter = 0
				self.profileScrollTimer = self.current_milli_time() + PROFILESCROLLTIMERINIT
				print ("Global Settings opened - globalConfig")
				
		elif self.isUpButtonPressed():
			print ("up pressed")
			index = (self.mainMenuSelect.value + 1 ) % len(self.mainMenuItems)
			self.mainMenuSelect = self.mainMenuItems(index)
			
		elif self.isDownButtonPressed():
			print ("down pressed")
			index = (self.mainMenuSelect.value - 1 ) % len(self.mainMenuItems)
			self.mainMenuSelect = self.mainMenuItems(index)
			
		elif self.isBackButtonPressed():
			print ("back pressed - nothing to do in main view 2")
		
	def processtolcd(self,  str):   # thins function replaces all "Umlaute" to drawable signs. ss ist own symbol
		#print (str + ": %i, %i, %i, %i, %i, %i" %( ord(str[0]) , ord(str[1]) ,  ord(str[2]) ,  ord(str[3]) ,  ord(str[4]) ,  ord(str[5])))
		str = list(str)
		for i in range(0, len(str)):
			if (ord(str[i]) == 164 or ord(str[i]) == 132):
				str[i] = "\xe1"
			elif (ord(str[i]) == 182 or ord(str[i]) == 150):
				str[i] = "\xef"
			elif (ord(str[i]) == 188 or ord(str[i]) == 156):
				str[i] = "\xf5"
			elif (ord(str[i]) == 159):
				str[i] = "\x07"
			elif (ord(str[i]) == 195):  # ? jedes zeichen wechselt sich mit 195 ab...
				str[i] = ''
		str = "".join(str)
		self.lcd.message(str)
		
	def view_profilSelect(self):
		self.lcd.setCursor(0,0)
		self.lcd.message("%2.1f\x00C " % float(self.tmp))
		self.lcd.setCursor(7,0)
		self.lcd.message("   Profil")
		self.lcd.setCursor(0,1)
		self.lcd.message("\x03 ")
		self.lcd.setCursor(2,1)
		
		string = self.profiles[self.profileId]
		if len(string) > 13:
			if (self.profileScrollTimer - self.current_milli_time() < 0):
				self.profileScrollCounter = (self.profileScrollCounter + 1) % len(string)
				if self.profileScrollCounter == 0:
					self.profileScrollTimer = self.current_milli_time() + PROFILESCROLLTIMERINIT
				else:
					self.profileScrollTimer = self.current_milli_time() + PROFILESCROLLTIMERINC
			string = string[self.profileScrollCounter:self.profileScrollCounter+13]
		string = string.ljust(13,  ' ')
		self.processtolcd(string)
		
		self.lcd.setCursor(15,1)
		self.lcd.message("\x04")
		
		if self.isRightButtonPressed(): # select
			self.state = self.States.Sett1
			self.profile = self.profiles[self.profileId]
			self.value = int(self.getSett())
			print ("profile selected - " + self.profile)
			
		if self.isLeftButtonPressed() or self.isBackButtonPressed(): # back
			self.state = self.States.Main
			print ("profile selected aborted - back to main menu")
			
		if self.isUpButtonPressed():
			self.profileId = (self.profileId - 1) % len(self.profiles)
			self.profile = self.profiles[self.profileId]
			self.profileScrollCounter = 0
			self.profileScrollTimer = self.current_milli_time() + PROFILESCROLLTIMERINIT
			self.lcd.setCursor(2,1)
			self.lcd.message("             ")
			print ("profile selected - " + self.profile)
			
		if self.isDownButtonPressed():
			self.profileId = (self.profileId + 1) % len(self.profiles)
			self.profile = self.profiles[self.profileId]
			self.profileScrollCounter = 0
			self.profileScrollTimer = self.current_milli_time() + PROFILESCROLLTIMERINIT
			self.lcd.setCursor(2,1)
			self.lcd.message("             ")
			print ("profile selected - " + self.profile)
			
		
	def view_sett1(self):       # 1. Rast TEMP
		self.lcd.setCursor(0,0)
		self.lcd.message("\x05 1. Rast       ")
		self.lcd.setCursor(0,1)
		self.lcd.message("Ziel-Temp.:")
		self.lcd.setCursor(11,1)
		self.lcd.message("%3d" % abs(self.value))
		self.lcd.setCursor(14,1)
		self.lcd.message("\x00C")

		if self.isDownButtonPressed():
			print ("down pressed")
			if self.value > 0:
				self.value = abs(self.value - 1)
		elif self.isUpButtonPressed():
			print ("up pressed")
			if self.value < 999:
				self.value = abs(self.value + 1)
		elif self.isLeftButtonPressed():
			self.saveSett()
			self.state = self.States.Sett6
			self.value = int(self.getSett())
			print ("left pressed")
		elif self.isRightButtonPressed():
			self.saveSett()
			self.state = self.States.Sett2
			self.value = int(self.getSett())
			print ("right pressed")
		elif self.isBackButtonPressed():
			self.saveSett()
			self.state = self.States.Main
			print ("Back pressed -  to main menu")
		
	def view_sett2(self):       # 1. Rast Zeit
		self.lcd.setCursor(0,0)
		self.lcd.message("\x05 1. Rast       ")
		self.lcd.setCursor(0,1)
		self.lcd.message("Zeit.:")
		self.lcd.setCursor(6,1)
		self.lcd.message("%7d" % abs(self.value))
		self.lcd.setCursor(13,1)
		self.lcd.message("min")

		if self.isDownButtonPressed():
			print ("down pressed")
			if self.value > 0:
				self.value = abs(self.value - 1)
		elif self.isUpButtonPressed():
			print ("up pressed")
			if self.value < 999:
				self.value = abs(self.value + 1)
		elif self.isLeftButtonPressed():
			self.saveSett()
			self.state = self.States.Sett1
			self.value = int(self.getSett())
			print ("left pressed")
		elif self.isRightButtonPressed():
			self.saveSett()
			self.state = self.States.Sett3
			self.value = int(self.getSett())
			print ("right pressed")
		elif self.isBackButtonPressed():
			self.saveSett()
			self.state = self.States.Main
			print ("Back pressed -  to main menu")
		
	def view_sett3(self):       # 2. Rast TEMP
		self.lcd.setCursor(0,0)
		self.lcd.message("\x05 2. Rast       ")
		self.lcd.setCursor(0,1)
		self.lcd.message("Ziel-Temp.:")
		self.lcd.setCursor(11,1)
		self.lcd.message("%3d" % abs(self.value))
		self.lcd.setCursor(14,1)
		self.lcd.message("\x00C")

		if self.isDownButtonPressed():
			print ("down pressed")
			if self.value > 0:
				self.value = abs(self.value - 1)
		elif self.isUpButtonPressed():
			print ("up pressed")
			if self.value < 999:
				self.value = abs(self.value + 1)
		elif self.isLeftButtonPressed():
			self.saveSett()
			self.state = self.States.Sett2
			self.value = int(self.getSett())
			print ("left pressed")
		elif self.isRightButtonPressed():
			self.saveSett()
			self.state = self.States.Sett4
			self.value = int(self.getSett())
			print ("right pressed")
		elif self.isBackButtonPressed():
			self.saveSett()
			self.state = self.States.Main
			print ("Back pressed -  to main menu")
			
	def view_sett4(self):       # 2. Rast Zeit
		self.lcd.setCursor(0,0)
		self.lcd.message("\x05 2. Rast       ")
		self.lcd.setCursor(0,1)
		self.lcd.message("Zeit.:")
		self.lcd.setCursor(6,1)
		self.lcd.message("%7d" % abs(self.value))
		self.lcd.setCursor(13,1)
		self.lcd.message("min")

		if self.isDownButtonPressed():
			print ("down pressed")
			if self.value > 0:
				self.value = abs(self.value - 1)
		elif self.isUpButtonPressed():
			print ("up pressed")
			if self.value < 999:
				self.value = abs(self.value + 1)
		elif self.isLeftButtonPressed():
			self.saveSett()
			self.state = self.States.Sett3
			self.value = int(self.getSett())
			print ("left pressed")
		elif self.isRightButtonPressed():
			self.saveSett()
			self.state = self.States.Sett5
			self.value = int(self.getSett())
			print ("right pressed")
		elif self.isBackButtonPressed():
			self.saveSett()
			self.state = self.States.Main
			print ("Back pressed -  to main menu")
			
	def view_sett5(self):       # 3. Rast TEMP
		self.lcd.setCursor(0,0)
		self.lcd.message("\x05 3. Rast       ")
		self.lcd.setCursor(0,1)
		self.lcd.message("Ziel-Temp.:")
		self.lcd.setCursor(11,1)
		self.lcd.message("%3d" % abs(self.value))
		self.lcd.setCursor(14,1)
		self.lcd.message("\x00C")

		if self.isDownButtonPressed():
			print ("down pressed")
			if self.value > 0:
				self.value = abs(self.value - 1)
		elif self.isUpButtonPressed():
			print ("up pressed")
			if self.value < 999:
				self.value = abs(self.value + 1)
		elif self.isLeftButtonPressed():
			self.saveSett()
			self.state = self.States.Sett4
			self.value = int(self.getSett())
			print ("left pressed")
		elif self.isRightButtonPressed():
			self.saveSett()
			self.state = self.States.Sett6
			self.value = int(self.getSett())
			print ("right pressed")
		elif self.isBackButtonPressed():
			self.saveSett()
			self.state = self.States.Main
			print ("Back pressed -  to main menu")
			
	def view_sett6(self):       # 3. Rast Zeit
		self.lcd.setCursor(0,0)
		self.lcd.message("\x05 3. Rast       ")
		self.lcd.setCursor(0,1)
		self.lcd.message("Zeit.:")
		self.lcd.setCursor(6,1)
		self.lcd.message("%7d" % abs(self.value))
		self.lcd.setCursor(13,1)
		self.lcd.message("min")

		if self.isDownButtonPressed():
			print ("down pressed")
			if self.value > 0:
				self.value = abs(self.value - 1)
		elif self.isUpButtonPressed():
			print ("up pressed")
			if self.value < 999:
				self.value = abs(self.value + 1)
		elif self.isLeftButtonPressed():
			self.saveSett()
			self.state = self.States.Sett5
			self.value = int(self.getSett())
			print ("left pressed")
		elif self.isRightButtonPressed():
			self.saveSett()
			self.state = self.States.Sett1
			self.value = int(self.getSett())
			print ("right pressed")
		elif self.isBackButtonPressed():
			self.saveSett()
			self.state = self.States.Main
			print ("Back pressed -  to main menu")       
		
		
		
	def view_profilSelect2(self):
		self.lcd.setCursor(0,0)
		self.lcd.message("%2.1f\x00C " % float(self.tmp))
		self.lcd.setCursor(7,0)
		self.lcd.message("   Profil")
		self.lcd.setCursor(0,1)
		self.lcd.message("\x03 ")
		self.lcd.setCursor(2,1)
		
		string = self.profiles[self.profileId]
		if len(string) > 13:
			if (self.profileScrollTimer - self.current_milli_time() < 0):
				self.profileScrollCounter = (self.profileScrollCounter + 1) % len(string)
				if self.profileScrollCounter == 0:
					self.profileScrollTimer = self.current_milli_time() + PROFILESCROLLTIMERINIT
				else:
					self.profileScrollTimer = self.current_milli_time() + PROFILESCROLLTIMERINC
			string = string[self.profileScrollCounter:self.profileScrollCounter+13]
		string = string.ljust(13,  ' ')
		self.processtolcd(string)
		
		self.lcd.setCursor(15,1)
		self.lcd.message("\x04")
		
		if self.isRightButtonPressed(): # select
			self.profile = self.profiles[self.profileId]
			
			self.valueTemp = int(self.getSett(1)) #1. Rast / preheat    temp
			self.valueTime = int(self.getSett(2)) #1. Rast / preheat    dauer
			
			self.state = self.States.preHeat
			#self.profile = self.profiles[self.profileId]
			print ("profile select 2, profile: " + self.profile)
			
		if self.isLeftButtonPressed() or self.isBackButtonPressed(): # back
			self.state = self.States.Main
			print ("profile select 2 aborted - back to main menu")
			
		if self.isUpButtonPressed():
			self.profileId = (self.profileId - 1) % len(self.profiles)
			self.profile = self.profiles[self.profileId]
			self.profileScrollCounter = 0
			self.profileScrollTimer = self.current_milli_time() + PROFILESCROLLTIMERINIT
			self.lcd.setCursor(2,1)
			self.lcd.message("             ")
			print ("profile select 2 - " + self.profile)
			
		if self.isDownButtonPressed():
			self.profileId = (self.profileId + 1) % len(self.profiles)
			self.profile = self.profiles[self.profileId]
			self.profileScrollCounter = 0
			self.profileScrollTimer = self.current_milli_time() + PROFILESCROLLTIMERINIT
			self.lcd.setCursor(2,1)
			self.lcd.message("             ")
			print ("profile select 2 - " + self.profile)
			
	def view_preHeat(self):                                         # vorheizen auf rast1 temp
		self.lcd.setCursor(0,0)
		self.lcd.message("%2.1f\x00C         %s" % (float(self.tmp),  self.heaterStatus()))
		self.lcd.setCursor(0,1)
		self.lcd.message("Heizen auf  %i\x00C " % int(self.valueTemp))

		if self.isRightButtonPressed():
			print ("right pressed - skip to next step: rdy for malt")
			self.state = self.States.preHeatComplete
			print ("%i C" % self.valueTemp)
		elif self.isUpButtonPressed():
			print ("up pressed - nothing to do")
		elif self.isDownButtonPressed():
			print ("down pressed - nothing to do")
		if self.isLeftButtonPressed() or self.isBackButtonPressed(): # back
			self.state = self.States.ProfileSelect2
			print ("pre Heat aborted - back to select 2")
			
	def view_preHeatComplete(self):                                         # malz hinzugeben! temp halten...
		self.lcd.setCursor(0,0)
		self.lcd.message("%2.1f\x00C Soll:%2i\x00%s" % (float(self.tmp) ,int(self.valueTemp),  self.heaterStatus()))
		self.lcd.setCursor(0,1)
		self.lcd.message("Malz dazugeben!\x04  ") # pfeil rechts

		if self.isRightButtonPressed() or self.isUpButtonPressed():
			print ("right pressed - skip to next step: Rast 1 time loaded")
			self.state = self.States.Rast1
			self.countdown = self.current_secs_time() + self.valueTime * 60
			print ("%i minutes" % self.valueTime)
		if self.isLeftButtonPressed() or self.isDownButtonPressed() or self.isBackButtonPressed(): # back
			self.state = self.States.ProfileSelect2
			print ("pre Heat aborted - back to select 2")
		
	def view_Rast1(self):                                                   # temp halten zeit rast 2
		mins, secs = divmod(self.countdown - self.current_secs_time(), 60)
		timeformat = '{:02d}:{:02d}'.format(mins, secs)
		
		self.lcd.setCursor(0,0)
		self.lcd.message("%2.1f\x00C   %s %s" % (float(self.tmp),timeformat,  self.heaterStatus()))
		self.lcd.setCursor(0,1)
		self.lcd.message("1.Rast Soll:%i\x00C " % int(self.valueTemp))

		if self.isRightButtonPressed() or self.isUpButtonPressed():
			print ("right pressed - skip to next step: heatRast2: temp loaded")
			self.state = self.States.HeatRast2
			self.valueTemp = int(self.getSett(3)) #2. Rast / preheat    temp
			self.valueTime = int(self.getSett(4)) #2. Rast / preheat    dauer
			print ("%i C" % self.valueTemp)
		elif self.isLeftButtonPressed() or self.isDownButtonPressed():
			self.state = self.States.preHeat
			print (" left -> step back to preHeat")
		elif self.isBackButtonPressed():
			self.state = self.States.ProfileSelect2
			print (" break -> abort to profile select")
			
	def view_HeatRast2(self):                                               # vorheizen auf rast2 temp
		self.lcd.setCursor(0,0)
		self.lcd.message("%2.1f\x00C         %s" % (float(self.tmp),  self.heaterStatus()))
		self.lcd.setCursor(0,1)
		self.lcd.message("Heizen auf  %i\x00C " % int(self.valueTemp))

		if self.isRightButtonPressed() or self.isUpButtonPressed():
			print ("right pressed - skip to next step: Rast2 time loaded")
			self.state = self.States.Rast2
			self.countdown = self.current_secs_time() + self.valueTime * 60
			print ("%i minutes" % self.valueTime)
		elif self.isLeftButtonPressed() or self.isDownButtonPressed():
			self.state = self.States.Rast1
			self.valueTemp = int(self.getSett(1)) #1. Rast / preheat    temp
			self.valueTime = int(self.getSett(2)) #1. Rast / preheat    dauer
			self.countdown = self.current_secs_time() + self.valueTime * 60
			print (" left -> step back to Rast 1: Time/Temp loaded")
		elif self.isBackButtonPressed():
			self.state = self.States.ProfileSelect2
			print (" break -> abort to profile select")
			
	def view_Rast2(self):                                                   # temp halten zeit rast 2
		mins, secs = divmod(self.countdown - self.current_secs_time(), 60)
		timeformat = '{:02d}:{:02d}'.format(mins, secs)
		
		self.lcd.setCursor(0,0)
		self.lcd.message("%2.1f\x00C   %s %s" % (float(self.tmp),timeformat,self.heaterStatus()))
		self.lcd.setCursor(0,1)
		self.lcd.message("2.Rast Soll:%i\x00C " % int(self.valueTemp))

		if self.isRightButtonPressed() or self.isUpButtonPressed():
			print ("right pressed - skip to next step: Rast3 temp loaded")
			self.state = self.States.HeatRast3
			self.valueTemp = int(self.getSett(5)) #3. Rast / preheat    temp
			self.valueTime = int(self.getSett(6)) #3. Rast / preheat    dauer
			print ("%i C" % self.valueTemp)
		elif self.isLeftButtonPressed() or self.isDownButtonPressed():
			self.state = self.States.HeatRast2
			print (" left -> step back ")
		elif self.isBackButtonPressed():
			self.state = self.States.ProfileSelect2
			print (" break -> abort to profile select")
			
	def view_HeatRast3(self):                                               # vorheizen auf rast3 temp
		self.lcd.setCursor(0,0)
		self.lcd.message("%2.1f\x00C         %s" % (float(self.tmp),  self.heaterStatus()))
		self.lcd.setCursor(0,1)
		self.lcd.message("Heizen auf  %i\x00C " % int(self.valueTemp))

		if self.isRightButtonPressed() or self.isUpButtonPressed():
			print ("right pressed - skip to next step: Rast3 time loaded")
			self.state = self.States.Rast3
			self.countdown = self.current_secs_time() + self.valueTime * 60
			print ("%i minutes" % self.valueTime)
		elif self.isLeftButtonPressed() or self.isDownButtonPressed():
			self.state = self.States.Rast2
			self.valueTemp = int(self.getSett(3)) #2. Rast / preheat    temp
			self.valueTime = int(self.getSett(4)) #2. Rast / preheat    dauer
			self.countdown = self.current_secs_time() + self.valueTime * 60
			print (" left -> step back to Rast 2: temp/time loaded")
		elif self.isBackButtonPressed():
			self.state = self.States.ProfileSelect2
			print (" break -> abort to profile select")
			
	def view_Rast3(self):                                                   # temp halten zeit rast 3
		mins, secs = divmod(self.countdown - self.current_secs_time(), 60)
		timeformat = '{:02d}:{:02d}'.format(mins, secs)
		
		self.lcd.setCursor(0,0)
		self.lcd.message("%2.1f\x00C   %s %s" % (float(self.tmp),timeformat, self.heaterStatus()))
		self.lcd.setCursor(0,1)
		self.lcd.message("3.Rast Soll:%i\x00C " % int(self.valueTemp))

		if self.isRightButtonPressed() or self.isUpButtonPressed():
			print ("right pressed - skip to next step: Done")
			self.state = self.States.Done
		elif self.isLeftButtonPressed() or self.isDownButtonPressed():
			self.state = self.States.HeatRast3
			print (" left -> step back ")
		elif self.isBackButtonPressed():
			self.state = self.States.ProfileSelect2
			print (" break -> abort to profile select")
			
	def view_Done(self):                                                    # fertig! 
		self.lcd.setCursor(0,0)
		self.lcd.message("%2.1f\x00C         %s" % (float(self.tmp),self.heaterStatus()))
		self.lcd.setCursor(0,1)
		self.lcd.message("Rasten fertig!  ")

		if self.isRightButtonPressed() or self.isUpButtonPressed():
			print ("right pressed - skip to next step: Mainmenu")
			self.state = self.States.Main
		elif self.isLeftButtonPressed() or self.isDownButtonPressed():
			self.state = self.States.Rast3
			self.countdown = self.current_secs_time() + self.valueTime * 60
			print (" left -> step back ")
		elif self.isBackButtonPressed():
			self.state = self.States.ProfileSelect2
			print (" break -> abort to profile select")

	def view_globalconf1(self):                         # Proportional Regler negativ value! 
		self.lcd.setCursor(0,0)
		self.lcd.message("\x05 PropRegler.neg")
		self.lcd.setCursor(0,1)
		self.lcd.message("Temp: ")
		self.lcd.setCursor(6,1)
		self.lcd.message("%7d" % self.globalconfig[0][1])
		self.lcd.setCursor(13,1)
		self.lcd.message("\x00C")

		if self.isDownButtonPressed():
			print ("down pressed")
			self.globalconfig[0][1] = self.globalconfig[0][1] - 1
		elif self.isUpButtonPressed():
			print ("up pressed")
			self.globalconfig[0][1] = self.globalconfig[0][1] + 1
		elif self.isLeftButtonPressed():
			self.globalconfigSave()
			self.state = self.States.globalconf2
			print ("left pressed")
		elif self.isRightButtonPressed():
			self.globalconfigSave()
			self.state = self.States.globalconf2
			print ("right pressed")
		elif self.isBackButtonPressed():
			self.globalconfigSave()
			self.state = self.States.Main
			print ("Back pressed -  to main menu")      
			
	def view_globalconf2(self):                         # Proportional Regler positiv value! 
		self.lcd.setCursor(0,0)
		self.lcd.message("\x05 PropRegler.pos")
		self.lcd.setCursor(0,1)
		self.lcd.message("Temp: ")
		self.lcd.setCursor(6,1)
		self.lcd.message("%7d" % self.globalconfig[1][1])
		self.lcd.setCursor(13,1)
		self.lcd.message("\x00C")

		if self.isDownButtonPressed():
			print ("down pressed")
			self.globalconfig[1][1] = self.globalconfig[1][1] - 1
		elif self.isUpButtonPressed():
			print ("up pressed")
			self.globalconfig[1][1] = self.globalconfig[1][1] + 1
		elif self.isLeftButtonPressed():
			self.globalconfigSave()
			self.state = self.States.globalconf1
			print ("left pressed")
		elif self.isRightButtonPressed():
			self.globalconfigSave()
			self.state = self.States.globalconf1
			print ("right pressed")
		elif self.isBackButtonPressed():
			self.globalconfigSave()
			self.state = self.States.Main
			print ("Back pressed -  to main menu")      
        
