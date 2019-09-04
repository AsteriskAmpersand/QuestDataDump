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
from pylatex import Document, Section, Subsection, Subsubsection, table
from pylatex import LineBreak as lbr

class Parts():
    def __init__(self, Monster, QuestBody, QuestModifiers, DifficultyModifiers):
        self.name = Monster.name
        self.SpawnType, self.Tempering, self.HealthVariance, self.BaseSize, self.SizeTable = QuestBody
        qmod = iter(QuestModifiers)
        qhp = next(qmod)
        self.HealthVariance = [int(DifficultyModifiers(qhp+index).monHPMultiplier*Monster.hzv.HP()) for index in self.HealthVariance]
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
        self.Poison, self.Sleep, self.Paralysis, self.Blast = tuple(map(lambda x: x.Modify(self.StatusBaseMult, self.StatusBuildupMult), stati[:-3]))
        self.KO = stati[-3].Modify(self.Stun,self.Stun)
        self.Exhaust = stati[-2].Modify(self.Exhaust,self.Exhaust)
        self.Mount = stati[-1].Modify(self.Mount,self.Mount)
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
        message += "Base Size: %3d | Size Table: %3d"%(int(self.BaseSize),self.SizeTable)+"\n"
        message += "Attack: %3d%% | Player Damage Bonus: %3d%% | Spawn Type: %2d"%(int(self.Attack),int(self.PlayerDamageMultiplier),int(self.SpawnType))+"\n"
        return message
    def strStatus(self):
        message = StatusData.strHeader()
        message += "".join([str(status) for status in [self.Poison, self.Sleep, self.Paralysis, self.Blast, self.KO, self.Exhaust, self.Mount]]) + "\n"
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
    def latexStatus(self, doc):
        tabula = table.Tabular("l r r r")
        tabula.add_row(StatusData.Header())
        tabula.add_hline
        for status in [self.Poison, self.Sleep, self.Paralysis, self.Blast, self.KO, self.Exhaust, self.Mount]:
            status.latex(tabula)
        doc.append(tabula)
    @staticmethod
    def latexPart(part,partname):
        tabula = table.Tabular("l")
        tabula.add_row([partname])
        tabula.add_row([round(part)])
        return tabula
    
    def latexMonsterBlock(self,doc):
        doc.append("HP Rolls: " + " - ".join(map(str,self.HealthVariance)))
        doc.append(lbr())
        doc.append("Base Size: %3d \t Size Table: %3d"%(int(self.BaseSize),self.SizeTable))
        doc.append(lbr())
        doc.append("Attack: %3d%% \t Player Damage Bonus: %3d%% \t Spawn Type: %2d"%(int(self.Attack),int(self.PlayerDamageMultiplier),int(self.SpawnType)))
        doc.append(lbr())
    def latex(self,doc):
        with doc.create(Subsection(self.Tempering+self.name)):
            self.latexMonsterBlock(doc)
            self.latexStatus(doc)
            with doc.create(Subsubsection("Breakable Parts")):
                for part,name in zip(self.Parts, self.PartNames['PartStringIds']):
                    doc.append(self.latexPart(part,name.replace("LOC_PART_","").replace("_"," ").title()))
            if self.Sever:
                if 'RemovablePartStringIds' not in self.PartNames or len(self.PartNames['RemovablePartStringIds'])!=len(self.Sever):
                    self.PartNames['RemovablePartStringIds'] = ["Unk%d"%ix for ix in range(len(self.Sever))]
                with doc.create(Subsubsection("Severable Parts")):
                    for part,name in zip(self.Sever, self.PartNames['RemovablePartStringIds']):
                        doc.append(self.latexPart(part,name.replace("LOC_REMOVABLE_PART_","").replace("_"," ").title()))
                
    
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
            
        
class Monster():
    epg = EPG_Library()
    eda = EDA_Library()
    with open("MonsterData.json","r")as ml:partnamelib = json.load(ml)['Monsters']
    with open("MonsterList.txt","r") as ml:names ={int(line[1], base=16):line[0] for line in csv.reader(ml)}
    
    def __init__(self, monsterID, QuestModifiers):
        self.name = self.names[monsterID]
        self.hzv = self.epg[monsterID]
        self.partnames = self.partnamelib[self.hzv.name]
        self.status = self.eda[monsterID]
        self.questModifiers = QuestModifiers

    def applyModifiers(self,DifficultyModifiers):
        QuestModifiers = self.questModifiers
        #Quest: Spawn, Tempered, HealthVariance, Size, RSiz Table
        #Quest and Diff: HP, Attack,PlayerDamage,Status,Stun,Exhaust,Mount,
        qMods, QuestModifiers = QuestModifiers[:5],QuestModifiers[5:]
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