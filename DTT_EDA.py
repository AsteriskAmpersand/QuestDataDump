# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 19:02:42 2019

@author: AsteriskAmpersand
"""
from Cstruct import PyCStruct
from Encryption import DecryptFile,EncryptFile, EDAKEY
from collections import OrderedDict
from Chunk import chunkPath
from pathlib import Path

class StatusData():
    def __init__(self,base,buildup,maxv, name):
        self.Name = name
        self.Base = base
        self.Buildup = buildup
        self.Max = maxv
        
    def Modify(self, BaseMult, BuildupMult):
        return StatusData(self.Base * BaseMult, 
                          self.Buildup * BuildupMult, 
                          self.Max * BuildupMult,
                          self.Name)

    def latex(self, table):
        table.add_row([self.Name.ljust(10), int(self.Base), int(self.Buildup), int(self.Max)])

    def __str__(self):
        return "%s| %5d | %7d | %5d |\n"%(self.Name.ljust(10), int(self.Base), int(self.Buildup), int(self.Max))
    
    @staticmethod
    def strHeader():
        return "  Status  |  Base | BuildUp |  Cap  |\n"
    @staticmethod
    def Header():
        return ["Status","Base","Build Up","Cap"]
    

class Header (PyCStruct):
	fields = OrderedDict([
		("fileId", "uint64"),#
		("monId", "uint32"),#
		("magic", "char[4]"),#
]);

StatusP = [        
		("%sBase", "uint32"),#
		("%sBuildup", "uint32"),#
		("%sMax", "uint32"),#
		("%sDrainTimer", "float"),# 
		("%sDrainVal", "uint32"),#
		("%sStatingDuration", "float"),#
		("%sDurationDecrease", "float"),#
        ("%sMinimumDuration", "float"),#
        ]
def expandStatusP(string):
    return [(i[0]%string,i[1]) for i in StatusP]

Poison = [
        *expandStatusP("poison"),
		("poisonDamage", "uint32"),#
		("poisonInterval", "float"),#
        ]
Sleep = expandStatusP("sleep")
Paralysis = expandStatusP("para")
KO = expandStatusP("ko")
Exhaust = [
        *expandStatusP("exhaust"),
		("exhaustUnkn", "uint32"),#
		("staminaDamage", "float"),#
        ]
Blast = [
        *expandStatusP("blast"),
		("blastDamage", "uint32"),#
        ]
Tranq = [
        *expandStatusP("exhaust"),
		("exhaustUnkn", "uint32"),#
		("capThreshold", "int32[2]"),#
        ]
Flash = expandStatusP("flash")
UnknS0 = [
        ("unknS0_0", "int32"),#
		("unknS0_1", "int32[8]"),#
        ("unknS0_2", "float[8]"),#
        ]
Mount = [
        *expandStatusP("mount"),
        ("mountUnknown", "int32"),#
        ]
Dung = [
        *expandStatusP("dung"),
        ("dungUnknown", "int32"),#
        ("dungUnknownFloat", "float"),#
        ]
Shocktrap = expandStatusP("shocktrap")
Pitfalltrap = expandStatusP("pitfalltrap")
Vinetrap = expandStatusP("vinetrap")
UnknS1 = [
        *expandStatusP("unkns1"),
        ("unkns1Unknown", "int32"),#
        ("unkns1UnknownFloat", "float"),#
        ]
Elderseal = [
        *expandStatusP("elderseal"),
        ("aura","int32")
        ]
UnknS2 = expandStatusP("unkns2")
UnknS3 = expandStatusP("unkns3")
   
class Status (PyCStruct):
	fields = OrderedDict([
            *Poison,
            *Sleep,
            *Paralysis,
            *KO,
            *Exhaust,
            *Mount,
            *Blast,
            *Tranq,
            *Flash,
            *UnknS0,
            *Mount,
            *Dung,
            *Shocktrap,
            *Pitfalltrap,
            *Vinetrap,
            *UnknS1,
            *Elderseal,
            *UnknS2,
            *UnknS3
]);

class EDA():
    def __init__(self):
        self.header = Header()
        self.status = Status()
    def marshall(self,data):
        self.header.marshall(data)
        self.status.marshall(data)
    def serialize(self):
        return self.header.serialize()+self.status.serialize()
    
class EDA_File():
    def __init__(self,path):
        with open(path,"rb") as file:
            self.eda = EDA()
            self.eda.marshall(DecryptFile(file,EDAKEY))
    def getStatus(self):
        return [
         StatusData(self.eda.status.poisonBase, self.eda.status.poisonBuildup,  self.eda.status.poisonMax,  "Poison"),#Poison
         StatusData(self.eda.status.sleepBase,  self.eda.status.sleepBuildup,   self.eda.status.sleepMax,   "Sleep"),#SLeep
         StatusData(self.eda.status.paraBase,   self.eda.status.paraBuildup,    self.eda.status.paraMax,    "Paralysis"),#Paralysis
         StatusData(self.eda.status.blastBase,  self.eda.status.blastBuildup,   self.eda.status.blastMax,   "Blast"),#Blast
         StatusData(self.eda.status.koBase,     self.eda.status.koBuildup,      self.eda.status.koMax,      "KO"),#KO
         StatusData(self.eda.status.exhaustBase,self.eda.status.exhaustBuildup, self.eda.status.exhaustMax, "Exhaust"),#Exhaust
         StatusData(self.eda.status.mountBase,  self.eda.status.mountBuildup,   self.eda.status.mountMax,   "Mount")]#Mount
    
class EDA_Library():
    def __init__(self):
        self.hitzoneData = {}
        for hitzoneFile in list(Path(chunkPath+r"\em").rglob("*.dtt_eda")):
            eda = EDA_File(hitzoneFile)
            self.hitzoneData[eda.eda.header.monId]=eda
    def __getitem__(self, key):
        return self.hitzoneData[key]