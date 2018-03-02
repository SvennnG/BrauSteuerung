#!/usr/bin/python

import glob, re
import mysql.connector
from mysql.connector import (connection)
from mysql.connector import errorcode
import traceback
		
class ConfManager2():
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
			self.cursor = self.con.cursor()
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("Something is wrong with your user name or password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				print("Database does not exist")
			else:
				print(err)
			
		print("###[MYSQL]:"+db+"."+table+" initialized")
		
		# default init 	
		self.config = {"Proportionalbereich.neg":"-11",
						 "Proportionalbereich.pos":"5"
						};	
		self.updateValues()
		
	def setValue(self, name, value):
		value = str(value)
		#print("[MYSQL]: "+name+" new value: "+value)
		try:
			self.config[name] = str(value)
			sql = "UPDATE "+self.table+" SET Value = "+str(value)+" WHERE Setting = '"+name+"'"
			self.cursor.execute(sql)
			return 1
		except mysql.connector.Error as err:
			traceback.print_exc()
			print(err)
			print("[MYSQL]:"+"error : ")
			return 0
			
	def getValue(self, name):
		try:
			return self.config[name];
		except:
			return False
		
	def updateValues(self):
		#print("[MYSQL]:"+"updating Global Config Values:...")
		for name, value in self.config.items():
			self.updateValue(name)
		#print("[MYSQL]:"+"updating Global Config Values finished!")
				
	def updateValue(self, name):
		try:
			sql = "SELECT Value FROM "+self.table+" WHERE Setting = '"+name+"'"
			self.cursor.execute(sql)
			result = self.cursor.fetchone()
			self.config[name] = result[0]
			print("[MYSQL]: Loaded "+name+" = "+str(self.config[name]))
		except:
			traceback.print_exc()
			print("[MYSQL]:"+"error : ")
			return False;