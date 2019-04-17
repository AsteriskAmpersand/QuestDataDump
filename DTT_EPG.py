# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 02:46:52 2019

@author: AsteriskAmpersand
"""
from Cstruct import Mod3Container, PyCStruct
from collections import OrderedDict
from Chunk import chunkPath
from pathlib import Path
class PartHzv (PyCStruct):
    fields = OrderedDict([
		("unk0", "int32"),#    //00 00 00 00
		("Header", "int32"),#  //0A 00 00 00 
		("Sever", "int32"),#   //0A 00 00 00 
		("Blunt", "int32"),#   //4B 00 00 00 
		("Shot", "int32"),#    //46 00 00 00 
		("Fire", "int32"),#    //37 00 00 00 
		("Water", "int32"),#   //00 00 00 00 
		("Ice", "int32"),#     //0A 00 00 00 
		("Thunder", "int32"),# //0F 00 00 00 
		("Dragon", "int32"),#  //14 00 00 00 
		("Stun", "int32"),#    //0F 00 00 00 
		("unk10", "int32"),#
    ])
    def __str__(self):
        return '|'.join([" %3d "%self.__getattribute__(hzv) for hzv in list(self.fields.keys())])
    @staticmethod
    def header():
        return '|'.join(["Part#"," Unk "," Sig ","Sever", "Blunt","Shot ","Fire ", "Water"," Ice "," Thn ", " Dra ", "Stun ", " ES? "])

class Header (PyCStruct):
	fields = OrderedDict([
		("filetype", "int32"),#
		("ingameID", "int32"),#
		("section", "int32"),#
		("baseHP", "int32"),#    
        ])

class breakCounts (PyCStruct):
	fields = OrderedDict([
		("unkn5", "int32"),#//00 00 00 00 
		("unkn6", "int32"),#//FF FF FF FF 
		("unkn7", "int32"),#//FF FF FF FF 
		("unkn8", "int32"),#//FF FF FF FF 
		("unkn9", "int32"),#//FF FF FF FF 
    ])
    
class breakData (Mod3Container):
    Mod3Class = breakCounts
    
class partTrail(PyCStruct):
	fields = OrderedDict([
    	("unkn10", "int32"),#//03 00 00 00 
		("unkn11", "int32"),#//00 00 00 00 
		("unkn12", "int32"),#//00 00 00 00 
		("unkn13", "int32"),#//00 00 00 00     
        ])

class PartHP (PyCStruct):
    fields = OrderedDict([
		("flinchValue", "int32"),#//2C 01 00 00 
		("unk1", "int32"),#//FF FF FF FF 
		("unk2", "int32"),#//FF FF FF FF 
		("unk3", "int32"),#//00 00 00 00 ]
    ])
    def __init__(self):
        super().__init__()
        self.breaksData = breakData()
        self.trailing = partTrail()
    def marshall(self,data):
        super().marshall(data)
        self.breaksData.marshall(data)
        self.trailing.marshall(data)
    def serialize(self):
        return super().serialize()+self.breaksData.serialize+self.trailing.serialize

class Parts (Mod3Container):
	Mod3Class = PartHP

class Hitzones (Mod3Container):
    Mod3Class = PartHzv
    def __str__(self):
        if not self:
            return ""
        message = PartHzv.header() + "\n"
        message += "\n".join(["%5d"%ix+ "|" + str(part) for ix, part in enumerate(self)])
        return message
            
            

class CleaveData (PyCStruct):
	fields = OrderedDict([
		("damageType", "int32"),#
		("unkn1", "int32"),#
		("unkn2", "int32"),#
		("cleaveHP", "int32"),#
		("unkn4", "int32"),#
		("SeverMaybe", "bool"),#
		("BluntMaybe", "bool"),#
		("ShotMaybe", "bool"),#    
    ])

class CleaveZones (Mod3Container):
	Mod3Class = CleaveData

class UnkData(PyCStruct):
	fields = OrderedDict([
    ("int32", "unk0[4]"),#
	 ("unk1", "byte[2]"),#
	 ("unk2", "int32[2]"),#
    ])

class UnkZones (Mod3Container):
	Mod3Class = UnkData
    
class EPG():
    def __init__(self):
        self.Header = Header()
        self.Parts = Parts()
        self.Hitzones = Hitzones()
        self.CleaveZones = CleaveZones()
        self.parts = [self.Header, self.Parts, self.Hitzones, self.CleaveZones]
    def serialize(self):
        return b''.join([part.serialize() for part in self.parts])
    def marshall(self,data):
        for part in self.parts:part.marshall(data)
        
class EPG_File():
    def __init__(self,path):
        with open(path,"rb") as file:
            self.epg = EPG()
            self.epg.marshall(file)
            self.name = path.stem+"_"+str(path.parents[1].stem)
    def HP(self):
        return self.epg.Header.baseHP
    def Parts(self):
        return self.epg.Parts
    def Sever(self):
        return self.epg.CleaveZones
            
class EPG_Library():
    def __init__(self):
        self.hitzoneData = {}
        for hitzoneFile in list(Path(chunkPath+r"\em").rglob("*.dtt_epg")):
            epg = EPG_File(hitzoneFile)
            self.hitzoneData[epg.epg.Header.ingameID]=epg
    def __getitem__(self, key):
        return self.hitzoneData[key]