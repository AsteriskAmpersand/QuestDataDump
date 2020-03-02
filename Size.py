# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 13:04:14 2020

@author: AsteriskAmpersand
"""
from construct import Int32sl as int32
from construct import Int32ul as uint32
from construct import Int64ul as uint64
from construct import Float32l as float32
from construct import CString as string
from construct import Struct,this,Probe
from Chunk import chunkPath
from pathlib import Path
from collections import OrderedDict
from MonsterEnumeration import monEnum
from SizeTranslation import translationTable
sizeFilePath = Path(chunkPath).joinpath(r"common\em\em_rsiz.dtt_rsz")

monsterEntry = Struct(
    "index" / uint32,
    "smallGold" / uint32,
    "silver" / uint32,
    "bigGold" / uint32,
    "size" / float32,
)

sizeData = Struct(
    "sizeIndex" / uint32,
    "chance" / uint32,
)

sizeTable = Struct(
    "name" / string("utf-8"),
    "size" / sizeData[0x26],
)

size = Struct(
    "signature" / uint64,
    "monsterDataCount" / int32,
    "entries" / monsterEntry[this.monsterDataCount],
    "sizeTableCount" / int32,
    "sizeTables" / sizeTable[this.sizeTableCount],
)


class sizeTable():
    def __init__(self,sizeTableStruct):
        self.entries = OrderedDict([(entry.sizeIndex, entry.chance) for entry in sizeTableStruct.size if entry.chance])
        nonnull=list(self.entries.keys())
        self.extrema = (nonnull[0],nonnull[-1])
        
    def __repr__(self):
        return "[%d%%,%d%%]"%self.extrema
    
    def recenter(self,base):
        dif = base-100
        self.dif = dif
        self.extrema = (self.extrema[0]+dif,self.extrema[1]+dif)
        self.entries = OrderedDict([(key+dif,self.entries[key]) for key in self.entries])
        return self

class sizeFile():
    struct = size
    def __init__(self, path = None):
        if path is not None:
            with open(path,"rb") as inf:
                self.marshall(inf.read())
    def marshall(self, data):
        col = self.struct.parse(data)
        for field in self.struct.subcons:
            setattr(self,field.name,getattr(col,field.name))
        self.crownTable = {entry.index:(entry.smallGold,entry.bigGold) for entry in self.entries}
    def append(self, entry):
        self.entries.append(entry)
    def __getitem__(self,ix):
        return sizeTable(self.sizeTables[ix])
    def __setitem__(self,ix,data):
        self.entries[ix]=data
    def __iter__(self):
        return iter(self.entries)
    def __len__(self):
        return len(self.entries)
    def serialize(self):
        return self.struct.build({field.name:getattr(self,field.name) for field in self.struct.subcons})
    def getCrowns(self,mid):
        if mid in self.crownTable:
            return self.crownTable[mid]
        else:
            return (90,123)

masterSize = sizeFile(sizeFilePath)

if "__main__" in __name__:
    import matplotlib.pyplot as plt
    import csv
    b=sizeFilePath
    b =r"E:\IBProjects\Guaranteed Crowns\Big\nativePC\common\em\em_rsiz.dtt_rsz"
    b =r"E:\IBProjects\Guaranteed Crowns\Small\nativePC\common\em\em_rsiz.dtt_rsz"
    s = sizeFile(b)
    for t in s.sizeTables:
        print("%s:%s"%(translationTable[t.name],sizeTable(t)))
        #plt.bar(list(map(lambda x: x.sizeIndex, t.size)),list(map(lambda x: x.chance, t.size)))
        #plt.title(translationTable[t.name])
        #plt.savefig(r"G:\QuestDataDump\SizeTables\%s.png"%translationTable[t.name].replace(":",""))
        #plt.close()
    #with open("MonsterList.txt","r") as ml:names ={int(line[1], base=16):line[0] for line in csv.reader(ml)}
    #for monster in s.entries:
    #    print("%03d - %s: [%d-%d] %.2f"%(monster.index, names[monster.index] if monster.index in names else "Unknown",monster.smallGold,monster.bigGold,monster.size))