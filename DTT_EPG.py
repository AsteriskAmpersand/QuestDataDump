# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 02:46:52 2019

@author: AsteriskAmpersand
"""
from Cstruct import Mod3Container, PyCStruct
from Encryption import DecryptFile,EncryptFile, EPGKEY
from collections import OrderedDict
from Chunk import chunkPath
from pathlib import Path
class Header (PyCStruct):
	fields = OrderedDict([
        ("ibBytes","int32"),
		("filetype", "int32"),#
		("ingameID", "int32"),#
		("section", "int32"),#
		("baseHP", "int32"),#    
        ])

class subParts (PyCStruct):
    fields = OrderedDict([
		("base", "int32"),#//00 00 00 00 
		("broken", "int32"),#//FF FF FF FF 
		("spec0", "int32"),#//FF FF FF FF 
		("spec1", "int32"),#//FF FF FF FF 
		("spec2", "int32"),#//FF FF FF FF 
    ])
    def empty(self):
        return all((getattr(self,f) == -1 for f in self.fields))
    
class breakCounts():
    def __init__(self):
        self.subParts = [subParts(),subParts()]
    def marshall(self,data):
        for part in self.subParts:   part.marshall(data)
    def serialize(self):
        return b''.join(map(lambda x: x.serialize(), self.subParts))
        
class breakData (Mod3Container):
    Mod3Class = breakCounts
    
class partTrail(PyCStruct):
	fields = OrderedDict([
    	("unkn10", "int32"),#//03 00 00 00 
		("unkn11", "int32"),#//00 00 00 00 
		("unkn12", "int32"),#//00 00 00 00 
		("unkn13", "int16"),#//00 00 00 00     
        ])

class PartHP (PyCStruct):
    fields = OrderedDict([
		("flinchValue", "int32"),#//2C 01 00 00 
		("CleaveLink1", "int32"),#//FF FF FF FF 
		("CleaveLink2", "int32"),#//FF FF FF FF 
		("CleaveLink3", "int32"),#//00 00 00 00 ]
        ("KinsectExtract", "int32"),#//00 00 00 00 ]
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
        return super().serialize()+self.breaksData.serialize()+self.trailing.serialize()

class Parts (Mod3Container):
	Mod3Class = PartHP

class PartHzv (PyCStruct):
    fields = OrderedDict([
		("Timer", "float"),#    //00 00 00 00
		("Sever", "int32"),#   //0A 00 00 00 
		("Blunt", "int32"),#   //4B 00 00 00 
		("Shot", "int32"),#    //46 00 00 00 
		("Fire", "int32"),#    //37 00 00 00 
		("Water", "int32"),#   //00 00 00 00 
		("Ice", "int32"),#     //0A 00 00 00 
		("Thunder", "int32"),# //0F 00 00 00 
		("Dragon", "int32"),#  //14 00 00 00 
		("Stun", "int32"),#    //0F 00 00 00 
		("Mount", "int32"),#
    ])
    def __str__(self):
        return '|'.join([" %3d "%self.__getattribute__(hzv) for hzv in list(self.fields.keys())])
    @staticmethod
    def header():
        return '|'.join(["Part#","Timer","Sever", "Blunt","Shot ","Fire ", "Water"," Ice "," Thn ", " Dra ", "Stun ", "Mount"])

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
		("Specialunkn", "bool"),#
		("Specialunkn2", "bool"),#
		("Specialunkn3", "bool"),#    
    ])

class CleaveZones (Mod3Container):
	Mod3Class = CleaveData

class UnkData(PyCStruct):
	fields = OrderedDict([
    ("unkn0","int32"),
    ("unkn1","int32"),
    ("unkn2","int32"),
    ("unkn9","byte"),
    ("unkn3","int32"),
    ("unkn4","byte"),
    ("unkn5","byte"),
    ("unkn6","int32"),
    ("unkn7","byte"),
    ("unkn8","byte"),
    ("unkn10","byte")
    ])

class UnkZones (Mod3Container):
	Mod3Class = UnkData
    
class Padding(PyCStruct):
	fields = OrderedDict([
		("padding", "int32[2]")])

def pad(data):
    #print(len(data))
    return data + b'\x00'*((-len(data))%16)
    
class EPG():
    def __init__(self):
        self.Header = Header()
        self.Parts = Parts()
        self.Hitzones = Hitzones()
        self.CleaveZones = CleaveZones()
        self.UnkZones = UnkZones()
        self.Padding = Padding()
        self.parts = [self.Header, self.Parts, self.Hitzones, self.CleaveZones, self.UnkZones,self.Padding]
    def serialize(self):
        return pad(b''.join([part.serialize() for part in self.parts]))
    def marshall(self,data):
        for part in self.parts:part.marshall(data)
        
class EPG_File():
    def __init__(self,path):
        with open(path,"rb") as file:
            file = DecryptFile(file,EPGKEY)
            self.epg = EPG()
            self.epg.marshall(file)
            self.name = path.stem+"_"+str(path.parents[1].stem)
    def serialize(self):
        #print(len(self.epg.serialize()))
        return EncryptFile(self.epg.serialize(),EPGKEY)
        
    def HP(self):
        return self.epg.Header.baseHP
    def Parts(self):
        return self.epg.Parts
    def Sever(self):
        return self.epg.CleaveZones
    def __str__(self):
        string = ""
        string += ("Base HP: %d\n"%self.HP())
        string += ("Hitzones:\n")
        string += PartHzv.header()+"\n"
        string += '\n'.join([str(part) for part in self.epg.Hitzones])
        string += ("\nParts HP:\n")
        string += '\n'.join([str(part) for part in self.Parts()])
        string += ("\nCleave HP:\n")
        string += '\n'.join([str(part) for part in self.Sever()])        
        return string
            
class EPG_Library():
    def __init__(self):
        self.hitzoneData = {}
        for hitzoneFile in list(Path(chunkPath+r"\em").rglob("*.dtt_epg")):
            epg = EPG_File(hitzoneFile)
            self.hitzoneData[epg.epg.Header.ingameID]=epg
            #epg.serialize()
    def __getitem__(self, key):
        return self.hitzoneData[key]
    def __iter__(self):
        return iter(self.hitzoneData)