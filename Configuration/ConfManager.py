#!/usr/bin/python

import glob, re
import mysql.connector
from mysql.connector import (connection)
from mysql.connector import errorcode
import traceback
		
from pprint import pprint
class ConfManager():
	def __init__(self, table, db = "brauSteuerung"):
		self.table = table
		self.db = db
		try:
			config = {
				'user': 'brauer',
				'password': 'Seelze!Bier8',
				'host': '127.0.0.1',
				'database': db,
				'get_warnings':True,
				'raise_on_warnings': True,
				'collation':'utf8_bin',
				'autocommit' : True,
			}
			self.con = connection.MySQLConnection(**config)
			self.cursor = self.con.cursor(buffered=True)
			
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("Something is wrong with your user name or password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				print("Database does not exist")
			else:
				print(err)
		except:
			traceback.print_exc()
		
		print("###[MYSQL]:"+db+"."+table+" initialized")
		
		# default init 	
		self.profiles = {"default":{"Time1":"Temp1","Time2":"Temp2","Time3":"Temp3","Time4":"Temp4"}
						};	
		self.updateProfiles()
		
	def setValue(self, name, SettingId, value):
		item = "invalid Item!"
		if SettingId == 1:
			item = "Temp1"
		elif SettingId == 2:
			item = "Time1"
		elif SettingId == 3:
			item = "Temp2"
		elif SettingId == 4:
			item = "Time2"
		elif SettingId == 5:
			item = "Temp3"
		elif SettingId == 6:
			item = "Time3"
		elif SettingId == 7:
			item = "Temp4"
		elif SettingId == 8:
			item = "Time4"
		value = str(value)
		#print("[MYSQL]: Profile "+name+": "+item+" = "+value)
		try:
			self.profiles[name][item] = str(value)
			sql = "UPDATE "+self.table+" SET "+str(item)+" = "+str(value)+" WHERE Name = '"+name+"'"
			self.cursor.execute(sql)
			return 1
		except mysql.connector.Error as err:
			traceback.print_exc()
			print(err)
			print("[MYSQL]: Profiles error!")
			return 0
			
	def getValue(self, profileName, SettingId):
		item = "invalid Item!"
		if SettingId == 1:
			item = "Temp1"
		elif SettingId == 2:
			item = "Time1"
		elif SettingId == 3:
			item = "Temp2"
		elif SettingId == 4:
			item = "Time2"
		elif SettingId == 5:
			item = "Temp3"
		elif SettingId == 6:
			item = "Time3"
		elif SettingId == 7:
			item = "Temp4"
		elif SettingId == 8:
			item = "Time4"
		try:
			return self.profiles[profileName][item];
		except:
			traceback.print_exc()
			return False
			
	def getProfile(self, name):
		try:
			return self.profiles[name];
		except:
			traceback.print_exc()
			return False
		
	def updateProfiles(self):
		#print("[MYSQL]:"+"updating Global profiles Values:...")
		try:
			sql = "SELECT Name FROM "+self.table
			self.cursor.execute(sql)
			row = self.cursor.fetchone()
			while row is not None:
				#print("[MYSQL]: Profile found: "+str(row[0].decode(encoding="utf-8")))
				self.profiles[row[0].decode(encoding="utf-8")] = ""
				row = self.cursor.fetchone()
		except mysql.connector.Error as err:
			print(err)
			print("[MYSQL]: Profiles error!")
			return False;
		except:
			traceback.print_exc()
		
		for name in self.profiles:
			self.updateProfile(name)
		#print("[MYSQL]:"+"updating Global profiles Values finished!")
				
	def updateProfile(self, name):
		#print("[MYSQL]: Profile complete load: "+name)
		try:
			sql = "SELECT * FROM "+self.table+" WHERE Name = '"+name+"'"
			self.cursor.execute(sql)
			result = dict(zip(self.cursor.column_names, self.cursor.fetchone()))
			del result["Name"]
			self.profiles[name] = result
			print("[MYSQL]: Loaded "+name+" = "+str(self.profiles[name]))
		except:
			traceback.print_exc()
			print("[MYSQL]: Profiles error!")
			return False;