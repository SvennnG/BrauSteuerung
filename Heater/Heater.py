#!/usr/bin/python
try:
	import RPi.GPIO as GPIO
except Exception as ex:
	print("No GPIO module! HEATER wont run!", ex)
      
import threading, time, sys

class Heater(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

		self.running = True 
		self.isHeating = False
		self.power = 0.0    # aktuelle leistung
		self.tmp = 0.0      # aktuelle temp
		self.targetTmp = 0.0# aktuelle ZielTemperatur

		self.firstBit = 1 #BCM 1, wiring 31
		self.secondBit = 12 # BCM 12, wiring 26
		self.thirdBit = 0 # BCM 0, wiring 30
		self.fourthBit = 5 # BCM 5, wiring 21
		
		self.current_milli_time = lambda: int(round(time.time() * 1000))
        
		self.linearNeg = -22
		self.linearPos = 22

		try:
			GPIO.setmode(GPIO.BCM)  # vs. GPIO.BOARD
			GPIO.setwarnings(False) #  This channel is already in use, continuing anyway.

			GPIO.setup(self.firstBit, GPIO.OUT)
			GPIO.setup(self.secondBit, GPIO.OUT)
			GPIO.setup(self.thirdBit, GPIO.OUT)
			GPIO.setup(self.fourthBit, GPIO.OUT)

			GPIO.output(self.firstBit, GPIO.LOW)
			GPIO.output(self.secondBit, GPIO.LOW)
			GPIO.output(self.thirdBit, GPIO.LOW)
			GPIO.output(self.fourthBit, GPIO.LOW)
		except Exception as ex:
			print("HEATER init Error: GPIO could not be initialized. HEATER wont run!", ex)

		print("#Heater initialized")
        
	def adjust(self, percentPower):
		if percentPower < 0.0:
			print("Heater cannot cool! Power need to be positive!")
			self.adjust(0.0)
		else:
			if percentPower > 100.0:
				print("Heater cannot do more than 100%! Power need to be limited!")
				self.adjust(100.0)
				return
			
			self.power = float(percentPower)
			
			n = int(round(self.power / 100 * 15))
			
			try:
				if (float(n) / 2) % 1 != 0:
					GPIO.output(self.firstBit, GPIO.HIGH)
				else:
					GPIO.output(self.firstBit, GPIO.LOW)
				if (float(int(float(n) / 2)) / 2 ) % 1 != 0:
					GPIO.output(self.secondBit, GPIO.HIGH)
				else:
					GPIO.output(self.secondBit, GPIO.LOW)
				if (float(int(float(int(float(n) / 2)) / 2 )) / 2 ) % 1 != 0:
					GPIO.output(self.thirdBit, GPIO.HIGH)
				else:
					GPIO.output(self.thirdBit, GPIO.LOW)
				if (float(int(float(int(float(int(float(n) / 2)) / 2 )) / 2 )) / 2 ) % 1 != 0:
					GPIO.output(self.fourthBit, GPIO.HIGH)
				else:
					GPIO.output(self.fourthBit, GPIO.LOW)
				print("Heater adjust Power: %2.2f %%" % self.power )
			except Exception as ex:
				print("GPIO could not be set. HEATER doesnt run! - Heater is shutting down!", ex)
				self.running = False
				
	def deactivate(self):
		self.isHeating = False
		print("Heater stopped  (Power still: %2.2f %%)" % self.power )
		
	def activate(self):
		self.isHeating = True
		print("Heating started. Power: %2.2f %%" % self.power )
		
	def resetHeating(self):
		self.isHeating = False
		self.power = 0.0
		print("Heating reset. Stopped!")
		
	def update(self, temp):
		self.tmp = temp
		
	def updateTargetTemperature(self,  temp):
		self.targetTmp = temp
		
	def status(self): # display symbols
		if self.power > 70.0:
			return "\x01"
		elif self.power > 10.0:
			return "\x06"
		else:
			return "\x02"
		
	def run(self):
		try:
			#cnt = 0
			self.time = self.current_milli_time()
			while self.running:
				if self.isHeating == True:
				
					# linear Regler mit Stufe:
					#diff = self.targetTmp - self.tmp
					# if diff >= 10:      # full power (>10 degree to heat)
						# power = 100.0
					# elif diff <= -3.0:   # cooling, too hot (>3 degree)
						# power = 0
					# elif diff <= 0.0:   # small power, little too hot (0-3 degree)
						# power = 10
					# else:               # controlled power (0-10 degree to heat), linear 20%-100% => 0-10 degree
						# power = 20+8*diff
					
					# Linear Regler: 
					#       [-region , targetTmp, +region] 
					#       [0          ...          100%]
					mint = self.targetTmp + self.linearNeg
					maxt = self.targetTmp + self.linearPos
					diff = maxt - self.tmp
					perc = 100 * diff / (abs(self.linearNeg) + abs(self.linearPos))
					if perc < 0:
						perc = 0
					if perc > 100:
						perc = 100
					power = perc
					
					
					#~ if self.current_milli_time() - self.time > 1500:
						#~ self.time = self.current_milli_time()
						#~ print("mint", mint, "maxt", maxt, "diff", diff, "perc", perc)
						#~ print("-:", self.linearNeg, ", +:", self.linearPos)
					
					
					power = int(power)
					if int(self.power) != power:
						self.adjust(power)
						
				elif self.power != 0.0: # no more heating => power to 0
					self.adjust(0.0)
				
				# update symbol in lcd...
				# adjust heating...
				#print("Heater; alive: %r, power: %2.2f %%" % (self.isHeating, self.power))
				
				time.sleep(1)
			self.adjust(0.0)
			self.deactivate()
		except Exception as ex:
			print("Error in HEATER! call Support", ex)
