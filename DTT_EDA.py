# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 19:02:42 2019

@author: AsteriskAmpersand
"""
from Cstruct import PyCStruct
from collections import OrderedDict
from Chunk import chunkPath
from pathlib import Path
import pylatex

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
		("fileId", "uint32"),#
		("monId", "uint32"),#
		("magic", "char[4]"),#
]);

class Status (PyCStruct):
	fields = OrderedDict([
		("poisonBase", "uint32"),#
		("poisonBuildup", "uint32"),#
		("poisonMax", "uint32"),#
		("poisonTimer1", "float"),#
		("poisonTimer2", "uint32"),#
		("poisonDuration", "float"),#
		("padding0", "uint64"),#
		("poisonDamageX2", "uint32"),#
		("poisonInterval", "float"),#
        
		("sleepBase", "uint32"),#
		("sleepBuildup", "uint32"),#
		("sleepMax", "uint32"),#
		("sleepTimer1", "float"),# 
		("sleepTimer2", "uint32"),#
		("sleepDuration", "float"),#
		("padding1", "uint64"),#
        
		("paraBase", "uint32"),#
		("paraBuildup", "uint32"),#
		("paraMax", "uint32"),#
		("paraTimer1", "float"),#
		("paraTimer2", "uint32"),#
		("paraDuration", "float"),#
		("padding2", "uint64"),#
        
		("koBase", "uint32"),#
		("koBuildup", "uint32"),#
		("koMax", "uint32"),#
		("koTimer1", "float"),#
		("koTimer2", "uint32"),#
		("koDuration", "float"),#
		("padding3", "uint64"),#
        
		("exhaustBase", "uint32"),# //225
		("exhaustBuildup", "uint32"),# //75
		("exhaustMax", "uint32"),# //900
		("exhaustTimer1", "float"),# //10
		("exhaustTimer2", "uint32"),# //5
		("unknown1 ", "uint32[4]"),#
		("unk2a", "float"),# //150
		("mountBase", "uint32"),# //40
		("mountBuildup", "uint32"),#  //70
		("mountMax", "uint32"),# //460
		("unknown2 ", "uint32[5]"),#
        
		("blastBase", "uint32"),#
		("blastBuildup", "uint32"),#
		("blastMax", "uint32"),#
		("unknown3 ", "uint32[5]"),#

		("unk3a", "uint32"),# //100
		("unk3b", "uint32"),# //150
		("unk3c", "uint32"),# //200
		("unk3d", "uint32"),# //300
		("unk3Timer1", "float"),# //5
		("unk3Timer2", "uint32"),# //5
		("unknown4 ", "uint32[3]"),#
		("unk33", "uint32"),# //30
		("unk34", "uint32"),# //1
		("unknown5 ", "uint32[4]"),#
		("unk4a", "float"),# //20
		("unk4b", "float"),# //4
		("unk4c", "float"),#  //5
		("unk4d", "uint32"),# //100
		("unk4e", "uint32"),# //100
		("unk4f", "uint32"),# //1000
		("unknown6 ", "uint32[5]"),#
		("unk5a", "uint32"),#   //100 
		("unk5b", "uint32"),# //1
		("unknown7 ", "uint32[4]"),#
		("unk6a", "float"),# //30
		("unk6b", "uint32"),#
		("unk6c", "uint32"),#
		("unk6d", "uint32"),# //50
		("unk6e", "float"),# //5
		("unk7a", "float"),#
		("unk7b", "uint32"),#
		("unk7c", "uint32"),#
		("unk7d", "uint32"),#
		("unk7e", "float"),#
		("unk8a", "float"),# //8
		("unk8b", "float"),# //2
		("unk8c", "float"),# //2
		("unk8d", "uint32"),#
		("unk8e", "uint32"),#
		("unk8Timer1", "float"),#
		("unk8Timer2", "uint32"),#
		("unk8f", "uint32"),#
		("unk8g", "float"),# //10
		("unk8h", "float"),# //2
		("unk8i", "float"),# //2
		("unknown8 ", "uint32[5]"),#
		("unk9a", "float"),#  //8
		("unk9b", "float"),#
		("unknown9 ", "uint32[4]"),#
		("unka", "float"),# //1
		("unknowna ", "uint32[9]"),#
		("unkbTimer1", "float"),#
		("unkbTimer2", "uint32"),#
		("unkba", "uint32"),#
		("unkbb", "uint32"),#
		("unkbc", "uint32"),#
		("unkbd", "uint32"),#  //20
		("unknownb ", "uint32[5]"),#
		("unkc", "float"),# //30
		("unknownc ", "uint32[2]"),#

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
            self.eda.marshall(file)
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