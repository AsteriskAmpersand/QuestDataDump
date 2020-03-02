# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 01:22:21 2019

@author: AsteriskAmpersand
"""

"""
- Part Durability -> Scales poison, paralysis, sleep, blast, and elder seal. Doesn't scale mount and stun
- Knockdown Resist -> Part HP
- Knockout Resist (Stun) -> Initial KO/stun threshold
- Immunity Reduction -> Initial mount threshold
- Stagger/Trip Resist -> Initial exhaust threshold"""

from pathlib import Path
from Chunk import chunkPath
import csv
import json
from DTT_EPG import EPG_Library
from DTT_EDA import EDA_Library, StatusData
from Size import masterSize
class Parts():
    def __init__(self, Monster, QuestBody, QuestModifiers, DifficultyModifiers):
        self.id = Monster.id
        self.name = Monster.name
        self.SpawnType, self.Tempering, self.HealthBaseVariance, self.BaseSize, self.SizeTable, self.Rank = QuestBody
        self.crowns = masterSize.getCrowns(self.id)
        self.SizeRange = masterSize[self.SizeTable].recenter(self.BaseSize)
        self.Crowns = ''.join(("g" if (self.SizeRange.extrema[0])<=self.crowns[0] else "-",
                       "G" if (self.SizeRange.extrema[1])>=self.crowns[1] else "-"))
        qmod = iter(QuestModifiers)
        qhp = next(qmod)
        self.HealthVariance = [int(DifficultyModifiers(qhp+index).monHPMultiplier*Monster.hzv.HP()) for index in self.HealthBaseVariance]
        self.Attack = DifficultyModifiers(next(qmod)).monDmgMultiplier*100
        self.PlayerDamageMultiplier = DifficultyModifiers(next(qmod)).playerDmgMultiplier*100

        self.PartMult =             DifficultyModifiers(next(qmod)).monPartHP
        self.StatusBaseMult =       DifficultyModifiers(next(qmod)).monStatusBase
        self.StatusBuildupMult =    DifficultyModifiers(next(qmod)).monStatusBuildup
        self.Stun =                 DifficultyModifiers(next(qmod)).monStun
        self.Exhaust =              DifficultyModifiers(next(qmod)).monExhaust
        self.Mount =                DifficultyModifiers(next(qmod)).monMount
        #status
        stati = Monster.status.getStatus()#Status Object
        self.Poison, self.Sleep, self.Paralysis, self.Blast = tuple(map(lambda x: x.Modify(self.StatusBaseMult, self.StatusBuildupMult), stati[:-4]))
        self.KO = stati[-4].Modify(self.Stun,self.Stun)
        self.Exhaust = stati[-3].Modify(self.Exhaust,self.Exhaust)
        self.Mount = stati[-2].Modify(self.Mount,self.Mount)
        self.Clagger = stati[-1].Modify(self.Rank,[DifficultyModifiers(qhp+index).monHPMultiplier for index in self.HealthBaseVariance])
        #parts
        #If we had part names they could be here
        self.Parts = [part.flinchValue*self.PartMult for part in Monster.hzv.Parts()]
        self.Sever = [part.cleaveHP*self.PartMult for part in Monster.hzv.Sever()]
        self.PartNames = Monster.partnames
    def __str__(self):
        return self.strMonsterBlock() + '-'*80 +'\n' + self.strStatus() + '-'*80 +'\n' + self.strParts() + ('-'*80 +'\n')*2
    def strMonsterBlock(self):
        message = self.Tempering+self.name+"\n"
        message += "HP Rolls: " + " - ".join(map(str,self.HealthVariance))+"\n"
        message += "Base Size: %3d | Size Table %d %s: %s"%(int(self.BaseSize),self.SizeTable,self.Crowns,self.SizeRange)+"\n"
        message += "Attack: %3d%% | Player Damage Bonus: %3d%% | Spawn Type: %2d"%(int(self.Attack),int(self.PlayerDamageMultiplier),int(self.SpawnType))+"\n"
        return message
    def strStatus(self):
        message = StatusData.strHeader()
        message += "".join([str(status) for status in [self.Poison, self.Sleep, self.Paralysis, self.Blast, self.KO, self.Exhaust, self.Mount]]) + "\n"
        message += str(self.Clagger)+"\n"
        return message
    def strParts(self):
        message= "Breakable Parts:\n"
        message += self.dualParse(self.Parts, self.PartNames['PartStringIds'],"LOC_PART_")+"\n"
        if self.Sever:
            if 'RemovablePartStringIds' not in self.PartNames or len(self.PartNames['RemovablePartStringIds'])!=len(self.Sever):
                self.PartNames['RemovablePartStringIds'] = ["Unk%d"%ix for ix in range(len(self.Sever))]
            message+= "Severable Parts:\n"
            message += self.dualParse(self.Sever, self.PartNames['RemovablePartStringIds'],"LOC_REMOVABLE_PART_")
        return message

    
    @staticmethod
    def dualParse(parts,partnames,typing):
        message = ""
        line1 = ""
        line2 = ""
        for partVal,partName in zip(parts,partnames):
            partName = partName.replace(typing,"").replace("_"," ").title()
            if len(line1)+len(partName)>80:
                message += line1+"|\n"
                message += line2+"|\n\n"
                line1 = ""
                line2 = ""
            line1 += '| '+partName.rjust(5)
            line2 += '| '+str(round(partVal)).rjust(max(5,len(partName)))
        message += line1+"|\n"
        message += line2+"|\n"
        return message
            

dummyHZVs = {'NameStringId': 'LOC_UNKNOWN_MONSTER', 'PartStringIds': ["Unkn%02d"%i for i in range(500)], 'BaseSize': 0.0, 'ScaleModifier': 1}

class Monster():
    epg = EPG_Library()
    eda = EDA_Library()
    with open("MonsterData.json","r")as ml:partnamelib = json.load(ml)['Monsters']
    with open("MonsterList.txt","r") as ml:names ={int(line[1], base=16):line[0] for line in csv.reader(ml)}
    
    def __init__(self, monsterID, QuestModifiers):
        self.id = monsterID
        self.name = self.names[monsterID] if monsterID in self.names else "Unkonwn Monster %d" % monsterID
        self.hzv = self.epg[monsterID]
        self.partnames = self.partnamelib[self.hzv.name] if self.hzv.name in self.partnamelib else dummyHZVs
        self.status = self.eda[monsterID]
        self.questModifiers = QuestModifiers

    def applyModifiers(self,DifficultyModifiers):
        QuestModifiers = self.questModifiers
        #Quest: Spawn, Tempered, HealthVariance, Size, RSiz Table
        #Quest and Diff: HP, Attack,PlayerDamage,Status,Stun,Exhaust,Mount,
        qMods, QuestModifiers = QuestModifiers[:6],QuestModifiers[6:]
        self.Parts = Parts(self,qMods, QuestModifiers, DifficultyModifiers)
        return self.Parts
        
    def __bool__(self):
        return self.name != "Empty"

        
"""
		("spawnID","uint32"),
		("unknown1","uint32"),
		("temperedFlag","ubyte"),
        
		("monsterHealth","uint32"),
		("monsterDamage","uint32"),
		("playerDamage","uint32"),
        
		("HealthVariance","uint32"), #Damage needs confirmation, but makes sense
        
		("size","uint32"),
		("sizeVariation","uint32"), #need confirmation

		("partHP","uint32"),
		("statusBase","uint32"),
		("statusBuildUp","uint32"),
		("stun","uint32"),
		("exhaust","uint32"),
		("mount","uint32"),
        
		("monHPMultiplier", "float"),#
		("monDmgMultiplier", "float"),#
		("playerDmgMultiplier", "float"),#
		("monPartHP", "float"),#
		("monStatusBase", "float"),#
		("monStatusBuildup", "float"),#
		("monStun", "float"),#
		("monExhaust", "float"),#
		("monMount", "float"),#
        """