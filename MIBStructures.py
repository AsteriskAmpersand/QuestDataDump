# -*- coding: utf-8 -*-
"""
Spyder Editor
"""
from Cstruct import PyCStruct
from collections import OrderedDict
from MonsterData import Monster
from Crypto.Cipher import Blowfish
from FileLike import FileLike
from GMD import GMDFile
from REM import REMLib
from Diff import DifficultyFile
from Chunk import chunkPath, tssTextPath
from pathlib import Path
import math
       
timeOfDay = ["Current","Late Night", "Dawn", "Early Day", "Mid Day", "Late Day",
             "Dusk", "Early Night", "Midnight", "Freeze Time"]
weather = ["Random","No Weather","Base Weather", "Alternate Weather", "Alternate Weather 2", "Alternate Weather 3"]
        
class Area():
    Areas = {0x65:"Ancient Forest",
         0x66:"Wildspire Waste",
         0xC9:"Special Arena",
         0x6A:"Great Ravine",
         0x67:"Coral Highlands",
         0x68:"Rotten Vale",
         0x69:"Elders' Recess",
         0x6a:"Hoarfrost Reach",
         0x6b:"Hoarfrost Reach",
         0x6c:"Hoarfrost Reach",
         0x19b:"Seliana Supply Cache",
         0x19c:"Origin Isle (Ruiner Arena)",
         0x19d:"Origin Isle",
         0x0193:"Everstream",
         0x0195:"Confluence of Fates",
         0x2E01:"Astera",
         0x2F01:"Research Lab",
         0x0199:"Caverns of El Dorado",
         0x0196:"Ancient Forest (Closed)",         
         0x0191:"Opening Cutscene",
         0xCA:"Arena"}
    
    def __getitem__(self, key):
        if key in self.Areas:
            return self.Areas[key]
        return "Unknown Area - 0x%s"%hex(key)[2:].rjust(8,'0')
        

class ObjectiveData(PyCStruct):
	fields = OrderedDict([
		("objectiveID","ubyte"),
		("event","ubyte"),
		("unkn11","ushort"),
		("objectiveID","ushort"),
		("objectiveAmount","ushort"),
		])

class MIBHeader(PyCStruct):
    fields = OrderedDict([
		("mibSignature","uint64"),
		("padding","ushort"),
		("mibID","int32"),
		("starRating","ubyte"),
		("unkn1","uint32"),
		("unkn2","uint32"),
		("questRank","uint32"),#LR or HR
		("mapID","uint32"),
		("playerSpawn","uint32"),#Camp1, ChoseWWingDrake
		("fixedSpawn","uint32"),#Scripted Spawn location? 1 Means Yes
		("binaryMapToggle","uint32"),#God knows
		("dayNightControl","uint32"),
		("weatherControl","uint32"),
		("unkn5","uint32"),
		("zennyReward","uint32"),
		("faintPenalty","uint32"),
		("subObjReward","uint32"),
		("questTimer","uint32"),
		("unkn9","ubyte"),
		("monsterIconId","ushort[5]"),
		("hrRestriction","ubyte"),
		("unkn10","uint32"),   
		])
    def stage(self):
        return Area()[self.mapID]
    def timeDay(self):
        return timeOfDay[self.dayNightControl]
    def weather(self):
        return weather[self.weatherControl]
    def time(self):
        return self.questTimer
    def zenny(self):
        return self.zennyReward
    def faints(self):
        return math.ceil(self.zennyReward/self.faintPenalty if self.faintPenalty else 0)
    
class MIBObjective(PyCStruct):
    fields = OrderedDict([
        ("objectiveID","ubyte"),
        ("multiMonsterFlag","ubyte"),#00/04 Off/On
        ("unkn11","ushort"),
        ("objectiveID1","ushort"),
        ("objectiveAmount","ushort")])
    
class MIBObjectiveHeader(PyCStruct):
    fields = OrderedDict([
		("subobjectivesRequired","ubyte"),])
    def __init__(self):
        self.Objectives = [MIBObjective() for _ in range(2)]
        super().__init__()
        self.subObjectives = [MIBObjective() for _ in range(2)]
    def marshall(self,data):
        for obj in self.Objectives:
            obj.marshall(data)
        super().marshall(data)
        for subobj in self.subObjectives:
            subobj.marshall(data)
    def serialize(self,data):
        return b''.join([obj.serialize() for obj in self.Objectives]) +\
                super().serialize() +\
                b''.join([obj.serialize() for obj in self.subObjectives])
    
class MIBObjectiveSection(PyCStruct):
    fields = OrderedDict([
		("unkn11","uint32"),
		("music","uint32"),
		("endMusic","uint32"),
		("questType","ubyte"),
		("questTypeIcon","ubyte"),
		("ATFlag","ubyte"), #02 enables AT global modifier
		("unkn14","ubyte"),
		("REMID","uint32[3]"),
		("SUPPID1","uint32[3]"),
		("unkn17","uint32"),
		("EXP","uint32"),#HR Points
		("unkn18","uint32"),
		("unkn19","uint32"),
		])
    def __init__(self):
        self.Header = MIBObjectiveHeader()
        super().__init__()
    def marshall(self,data):
        self.Header.marshall(data)
        super().marshall(data)
    def serialize(self):
        return self.Header.serialize()+super.serialize()
    def HRExp(self):
        return self.EXP 

class MIBMonster(PyCStruct):
    fields = OrderedDict([
		("monsterID","int32"),
		("spawnID","uint32"),
		("unknown1","int32"),
		("temperedFlag","byte"),
		("monsterHealth","int32"),
		("monsterDamage","int32"),
		("playerDamage","int32"),
		("HealthAndDamageVariance","int32"), #Damage needs confirmation, but makes sense
		("size","int32"),
		("sizeVariation","int32"), #need confirmation
		("unknown2","int32"),
		("partHP","int32"),
		("statusBase","int32"),
		("statusBuildUp","int32"),
		("stun","int32"),
		("exhaust","int32"),
		("mount","int32"),
		])
    @staticmethod
    def tempering(AT, Temper):
        if not Temper:
            return ""
        if AT:
            return "Arch-Tempered "
        return "Tempered "
    
    def toMonster(self, AT):
        questModifiers = [self.spawnID, self.tempering(AT,self.temperedFlag) ,
                          [i for i in range(-self.HealthAndDamageVariance,self.HealthAndDamageVariance+1)], 
                          self.size, self.sizeVariation]
        questModifiers += [
                self.monsterHealth,
                self.monsterDamage,
                self.playerDamage,
                self.partHP,  
                self.statusBase,
                self.statusBuildUp,
                self.stun,
                self.exhaust,  
                self.mount
                ]
        return Monster(self.monsterID,questModifiers)
    def __bool__(self):
        return self.monsterID != -1 and self.monsterID != 0xFFFF

class MIBSmallMonster(PyCStruct):
    fields = OrderedDict([
		("spawnID","int32"),
		("hp","uint32"),
		("attack","int32"),
        ("status","int32"),
        ])

class MIBMapIcon(PyCStruct):
    fields = OrderedDict([
		#("icons","MIBMapIcon[17]"),#        
		("mapIconValue1","int32"),
        ("mapIconValue2","int32"),
        ("mapIconColor","int32"),
        ])

class MIBMapIcons(PyCStruct):
    fields = OrderedDict([
		#("icons","MIBMapIcon[17]"),#        
		("emsIconFlag","int32[5]"),
        ("emsIconID","int32[5]"),
        ])
    def __init__(self):
        self.icons = [MIBMapIcon() for i in range(17)]
        super().__init__()
    def marshall(self,data):
        [i.marshall(data) for i in self.icons]
        super().marshall(data)
    def serialize(self):
        return b''.join([i.serialize() for i in self.icons])+super().serialize()

class MIBSpawns(PyCStruct):
	fields = OrderedDict([
		("unknFlag","byte"),
		("multiDiff","uint32"),
        ("spawnIconCount","uint32"),
        ("seqSpawnRule","uint32[5]"),
        ("spawnPercEM6","uint32"),
        ("spawnGlobalDelay","uint32"),
        ("spawnPercEM7","uint32"),
        ("spawnChance3","uint32"),
        ("spawnChance4","uint32"),
        ("spawnChance5","uint32"),
        ("spawnChance6","uint32"),
        ("spawnChance7","uint32"),
        ])

class MIBArena(PyCStruct):
	fields = OrderedDict([
		("arenaSetId","uint32"),
		("playerCountRestriction","uint32"),
		("arenaRankA","uint32"),
        ("arenaRankB","uint32"),
        ("arenaRankC","uint32"),
        ("unkn0","uint32"),
        ("unkn1","uint32"),
        ("unkn2","uint32"),
		("fenceControl","ubyte"),#00 Disabled 80 Available
		("unkn3","ubyte"),
        ("unkn4","ushort"),
        ("unkn5","uint32"),
        ("fenceCooldown","uint32"),
        ("fenceUptime","uint32"),
        ("unkn6","uint32"),
        ("unkn7","uint32"),
        ("unkn8","uint32"),
		])
            
class MIBIBData(PyCStruct):
	fields = OrderedDict([
		("unk","uint32[10]"),
        ("unkByte","byte"),
        ("unk100","uint32[7]"),
        ("unk10","uint32[5]"),
        ("unkBytes","byte[3]"),
        ])

class MIB():
    REM = REMLib()
    Diff = DifficultyFile()
    def __init__(self):
        self.Header = MIBHeader()
        self.Objective = MIBObjectiveSection()
        self.Monsters = [MIBMonster() for _ in range(7)]
        self.SmallMonsters = MIBSmallMonster()
        self.Spawns = MIBSpawns()
        self.MapIcons = MIBMapIcons()
        self.Arena = MIBArena()
        self.IB = MIBIBData()
    
    def marshall(self, data):
        self.Header.marshall(data)
        self.Objective.marshall(data)
        [m.marshall(data) for m in self.Monsters]#TODO - missing converting each MIB monster to a pureMonster
        self.binaryMonsters = [m for m in self.Monsters if m]
        self.Monsters = [m.toMonster(self.Objective.ATFlag) for m in self.binaryMonsters]
        self.SmallMonsters.marshall(data)
        self.Spawns.marshall(data)
        self.MapIcons.marshall(data)
        self.Arena.marshall(data)
        self.IB.marshall(data)
        
    def __str__(self):
        return self.strHeader() +\
                    ('-'*75+'\n') + "Single Player Stats:\n" +\
                    ('-'*75+'\n').join([str(Monster.applyModifiers(self.Diff.spMod())) for Monster in self.Monsters if Monster]) + "\n" +\
                    ('-'*75+'\n') + "Mutliplayer Stats:\n" +\
                    ('-'*75+'\n').join([str(Monster.applyModifiers(self.Diff.mpMod(self.Spawns.multiDiff))) for Monster in self.Monsters if Monster]) + "\n" +\
                    ('-'*75+'\n') + self.strREM()
    def strREM(self):
        return '\n'.join([str(self.REM[rem]) if rem in self.REM else "Missing REM"  for rem in self.Objective.REMID if rem != 0])
    def strHeader(self):
        message = ""
        m = "Stage: %s"%self.Header.stage()
        m = m.ljust(35) + "Time of day: %s"%self.Header.timeDay()
        message+=m+"\n"
        m = "Rank: %s"%self.rank()
        m = m.ljust(35) + "Weather: %s"%self.Header.weather()
        message+=m+"\n"
        m = "Time: %d"%self.Header.time()
        m = m.ljust(35) + "Rank Exp: %d"%self.Objective.HRExp()
        message+=m+"\n"
        m = "Zenny: %d"%self.Header.zenny()
        m = m.ljust(35) + "Faint Count: %d"%self.Header.faints()
        message+=m+"\n"
        return message
    
    def rank(self):
        if self.Header.questRank == 0:
            string = "LR"
        if self.Header.questRank == 1:
            string = "HR"
        if self.Header.questRank == 2:
            string = "MR"
        if self.Objective.ATFlag == 2:
                string += " AT"
        return string
      
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
        
def endianness_reversal(data):
    return b''.join(map(lambda x: x[::-1],chunks(data, 4)))

def CapcomBlowfish(file):
    cipher = Blowfish.new("TZNgJfzyD2WKiuV4SglmI6oN5jP2hhRJcBwzUooyfIUTM4ptDYGjuRTP".encode("utf-8"), Blowfish.MODE_ECB)
    return endianness_reversal(cipher.decrypt(endianness_reversal(file)))

class MIBFile():
    mibText = lambda x : r"%s\common\text\quest\%s_eng.gmd"%(chunkPath, Path(x).stem.replace("questData_","q"))
    mibTssText = lambda x : r"%s\%s_eng.gmd"%(tssTextPath, Path(x).stem.replace("questData_","q"))
    def __init__(self, path):
        data = FileLike(CapcomBlowfish(open(path,'rb').read()))
        self.mib = MIB()
        self.mib.marshall(data)
        try:
            file = MIBFile.mibText(path)
            self.name = GMDFile(file)[0]
        except:
            try:
                file = MIBFile.mibTssText(path)
                self.name = GMDFile(file)[0]     
            except:
                self.name = "Name Not Found"
        self.path = path
    def __str__(self):
        starRating = str(self.mib.Header.starRating) if self.mib.Header.starRating <10 else "MR %d"%(self.mib.Header.starRating-10)
        message = ("="*80+"\n")*2 +\
                    str(self.path.stem)+"\n" +\
                    (self.name + " (%s *) "%starRating).ljust(70)  + ("*"*self.mib.Header.starRating).rjust(10) + "\n" +\
                    ("="*80+"\n")*2
        message += str(self.mib)
        message += '\n\n'
        return message
            
    def hexPrint(self):
        message = ("="*80+"\n")*2 +\
            str(self.path.stem)+"\n" +\
            (self.name + " (%d *) "%self.mib.Header.starRating).ljust(70)  + ("*"*self.mib.Header.starRating).rjust(10) + "\n" +\
            ("="*80+"\n")*2
        for monster, binmonster in zip(self.mib.Monsters,self.mib.binaryMonsters):
            message += monster.name + " : " + ' '.join(map(lambda x: hex(x)[2:].zfill(2), binmonster.serialize())) + "\n"
        message += '\n\n'
        return message