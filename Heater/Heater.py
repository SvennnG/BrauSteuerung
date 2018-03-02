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
		
		self.activatePin = 22 # BCM 22, wiring ? pin 15
		
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
			
			GPIO.setup(self.activatePin, GPIO.OUT)

			GPIO.output(self.firstBit, GPIO.LOW)
			GPIO.output(self.secondBit, GPIO.LOW)
			GPIO.output(self.thirdBit, GPIO.LOW)
			GPIO.output(self.fourthBit, GPIO.LOW)
			
			GPIO.output(self.activatePin, GPIO.LOW)
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
			integral_error = 0
			while self.running:
				if self.isHeating == True:
					try:
						GPIO.output(self.activatePin, GPIO.HIGH)
					except Exception as ex:
						print("HEATER active not possible. GPIO could not be set. HEATER doesnt run! - Heater is shutting down!", ex)
						self.running = False
				
					# Linear Regler: 
					#       [-region , targetTmp, +region] 
					#       [0          ...          100%]
                    # verschiebung des linare bereichs entsprechend der zieltemperatur: (-5, +2)
                    #17% bei 57 um temp zu halten
                    #21% bei 64 um temp zu halten
                    #26% bei 73 um temp zu halten
                    #28% bei 76 um temp zu halten
                    #33% bei 85 um temp zu halten
					kfaktor = 2.5 											# Intensität der verschiebung
					ttmp = self.tmp + (kfaktor - self.targetTmp/76*kfaktor) # bei Temperatur 76 keine Verschiebung
                    
					min_temp = self.targetTmp + self.linearNeg
					max_temp = self.targetTmp + self.linearPos
					diff = max_temp - ttmp
					linear_percent = 100 * diff / (abs(self.linearNeg) + abs(self.linearPos))
					if linear_percent < 0:
						linear_percent = 0
					if linear_percent > 100:
						linear_percent = 100

					# INTEGRAL Regler:
					#    additiv zu linear hinzu
					#    klingt langsam ab (0.99 ~ hälfte je minute, 0.98~ hälfte alle 30s)
					error = self.targetTmp - self.tmp

					integral_error = integral_error + error
					if error > 0.01:
						if integral_error < 0:
							integral_error = integral_error * 0.94
					elif error < 0.01:
						if integral_error > 0:
							integral_error = integral_error * 0.94
                            
					if integral_error < -66:
						integral_error = -66
					if integral_error > 66:
						integral_error = 66
                        
					integral_error = 0.99 * integral_error	
					
					#power = linear_percent
					power = linear_percent * 1 + integral_error * 1	# gewichtete Summe
					
					if power > 100:
						power = 100
					if power < 0:
						power = 0
					
					print("\n Integral: %f\n power: %f\n" % (integral_error, power))
					
					#if self.current_milli_time() - self.time > 1500:
				#		self.time = self.current_milli_time()
			#			print("mint", mint, "maxt", maxt, "diff", diff, "perc", perc)
		#				print("-:", self.linearNeg, ", +:", self.linearPos)
					
					power = int(power)
					if int(self.power) != power:
						self.adjust(power)
						
				elif self.power != 0.0: # no more heating => power to 0
					self.adjust(0.0)
					try:
						GPIO.output(self.activatePin, GPIO.LOW)
					except Exception as ex:
						print("HEATER active not possible. GPIO could not be set. HEATER doesnt run! - Heater is shutting down!", ex)
						self.running = False
				
				#print("Heater; alive: %r, power: %2.2f %%" % (self.isHeating, self.power))
				while self.current_milli_time() - self.time < 1000:
					time.sleep(0.1)
				self.time = self.current_milli_time()
					
			self.adjust(0.0)
			self.deactivate()
		except Exception as ex:
			print("Error in HEATER! call Support", ex)
