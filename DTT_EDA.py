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
from clagger import ClaggerCommon

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

claggerTables = ClaggerCommon.open()
per = lambda x: x*100
class ClaggerData():
    def __init__(self,base,typing):
        self.Name = "Clagger"
        self.Base = base
        self.Table = claggerTables[typing]
        self.Rank = 0.0
        self.hpmod = 100
    def Modify(self,difficulty,hpmod):
        if difficulty == 0:
            self.Rank = self.Table.lowr
        if difficulty == 1:
            self.Rank = self.Table.highr
        if difficulty == 2:
            self.Rank = self.Table.masterr
        self.hparray = hpmod
        return self
    def __str__(self):
        preamble = "Threshold per HP Roll: "+" - ".join(map(lambda x: "%6d"%(self.Base*x),self.hparray))+"\n"      
        head = self.strHeader()
        body =  " %7.2f%% | %+6.2f%% | %+7.2f%% | "%(per(1+self.Table.normal+self.Rank),per(self.Table.enrage),per(self.Table.fatigue))+"\n"
        claggerpreamble = "\nClagger Bracket Modifiers for Monster HP Left:\n"
        claggerhead = self.claggerHeader()
        claggerbody = '| '.join(["%+5.1f%%"%per(hp) for hp in self.Table.hpRangeMod])+"|\n"                
        return preamble+head+body+claggerpreamble+claggerhead+claggerbody
    @staticmethod
    def strHeader():
        return r"   Base   | Enraged | Fatigued |"+"\n"
    @staticmethod
    def claggerHeader():
        return r"00-90%| 90-80%| 80-70%| 70-60%| 60-50%| 50-40%| 40-30%| 30-20%| 20-10%| 10-00%|"+"\n"
    @staticmethod
    def Header():
        return ["Base","Enraged","Fatigued",*["%d-%d%%"%(i,i-10) for i in range(100,0,-10)]]

class Header (PyCStruct):
	fields = OrderedDict([
		("fileId", "uint64"),#
		("monId", "uint32"),#
		("magic", "byte[4]"),#
]);

StatusP = [        
		("%sBase", "uint32"),#
		("%sBuildup", "uint32"),#
		("%sMax", "uint32"),#
		("%sDrainTimer", "float"),# 
		("%sDrainVal", "uint32"),#
		("%sStartingDuration", "float"),#
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
        *expandStatusP("tranq"),
		("HRThreshold", "uint32"),#
		("MRThreshold", "int32"),#
        ]
Flash = expandStatusP("flash")
UnknS0 = [
        ("unknS0_0", "int32"),#
		("unknS0_1", "int32[8]"),#
        ("unknS0_2", "float[8]"),#
        ]
Mount = expandStatusP("mount")
MountKD = [
        *expandStatusP("mountkd"),
        ("mountkdUnknown", "int32"),#
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
UnknStruct = [        
		("struct%02dUnkn0", "int32"),#
        ("struct%02dUnkn1", "int32"),#
        ("struct%02dUnkn2", "int32"),#
        ]
def expandUnkn(string):
    return [(i[0]%string,i[1]) for i in UnknStruct]
SpecEnrage = [       
        *expandStatusP("specrage"),
		("flinchShot", "float"),#
        ("flinchShot_NoWall", "float"),#
        ("faceslap", "float"),#
        ("flinchShot_Wall", "float"),#
        ("flinchShot_Ledge", "float"),#
        ]
TailStruct = sum([expandUnkn(i)for i in range(6)],[]) + [
        ]
Clagger = [*expandStatusP("clagger"),
           ("claggertype", "int32"),#
           ]

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
            *MountKD,
            *Dung,
            *Shocktrap,
            *Pitfalltrap,
            *Vinetrap,
            *UnknS1,
            *Elderseal,
            *UnknS2,
            *UnknS3,
            *TailStruct,
            *SpecEnrage,
            *Clagger,
            
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
         StatusData(self.eda.status.mountBase,  self.eda.status.mountBuildup,   self.eda.status.mountMax,   "Mount"),#Mount
         ClaggerData(self.eda.status.claggerBase, self.eda.status.claggertype),]#Clagger
    
class EDA_Library():
    def __init__(self):
        self.hitzoneData = {}
        for hitzoneFile in list(Path(chunkPath+r"\em").rglob("*.dtt_eda")):
            eda = EDA_File(hitzoneFile)
            self.hitzoneData[eda.eda.header.monId]=eda
    def __getitem__(self, key):
        return self.hitzoneData[key]