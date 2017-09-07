#!/usr/bin/python

import glob, re
import Configuration.ConfLoader as ConfLoader
import Configuration.ConfWriter as ConfWriter
        
class ConfManager():
    def __init__(self, path, load = "profiles"):
        
        self.path=path   #os.getcwd()
        list = sorted(glob.glob(self.path+"*.conf"))
        self.list = []
        for item in list:
            m = re.match(r"^(.+\/)*(.+)\.(.+)$", item)
            if m:
                it = str(str(m.group(2)) + "." + str(m.group(3)))
                self.list.append(it)
                
        self.list = sorted(self.list, key=lambda s: s.lower())  # alphabetisch sortierte liste an profilen. case-insensitive
        
        print ("- found Profiles: " + ', '.join(self.list))
        
        try:
            if load == "profiles":
                self.loadProfiles()
            elif load == "globalConfig":
                self.loadGlobalConfig()
        except Exception as ex:
            print("Load of ",load ," failed!", ex)
        
        self.profl = self.getProfileNames()
        
        print("#"+load+" initialized")
    def loadProfiles(self):
        self.profiles = []
        
        #(bier_name, r1_temp, r1_time, r2_temp, r2_time, r3_temp, r3_time) from confloader
        #an bestehende liste mit allen profilen haengen
        for file in self.list:
            (bier_name, r1_temp, r1_time, r2_temp, r2_time, r3_temp, r3_time) = ConfLoader.read(self.path+file)
            self.profiles = self.profiles + [(file, bier_name, r1_temp, r1_time, r2_temp, r2_time, r3_temp, r3_time)] 
         
        #return self.profiles
    
    def loadGlobalConfig(self):
        self.profiles = []
        
        #(bier_name, r1_temp, r1_time, r2_temp, r2_time, r3_temp, r3_time) from confloader
        #an bestehende liste mit allen profilen haengen
        if len(self.list) != 1:
            raise Exception("load of global Config failed because of to many config files!")
        for file in self.list:
            (pbneg, pbpos) = ConfLoader.readGlobal(self.path+file)
            self.profiles = self.profiles + [(file, "globalConfig", pbneg, pbpos)]
    
    def getProfileNames(self):
        profilenames = []
        #print("get profile names called...")
        for tpl in self.profiles:
            #print(" - Loading profile: " +tpl[1])
            profilenames = profilenames + [tpl[1]]
        return profilenames
    
    def getValue(self, profileName, settingID):
        for tpl in self.profiles:
            if tpl[1] == profileName:
                return tpl[settingID + 1]
        return None
    
    def setValue(self, profileName, settingID, value):
        count = 0
        for tpl in self.profiles:
            if tpl[1] == profileName:
                new = list(tpl)
                new[settingID + 1] = value
                self.profiles[count] = tuple(new)
                ConfWriter.write(self.profiles[count],self.path + tpl[0])
                return True
            count = count + 1
        return False
        
    def setGlobalValue(self, profileName, settingID, value):
        count = 0
        for tpl in self.profiles:
            if tpl[1] == profileName:
                new = list(tpl)
                new[settingID + 1] = value
                self.profiles[count] = tuple(new)
                ConfWriter.writeGlobalConfig(self.profiles[count],self.path + tpl[0])
                return True
            count = count + 1
        return False
        
