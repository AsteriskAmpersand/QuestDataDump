# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 13:53:11 2019

@author: AsteriskAmpersand
"""
from Cstruct import PyCStruct
from collections import OrderedDict
from Itm import ItmFile
from Chunk import chunkPath
from pathlib import Path
import pylatex

class REM(PyCStruct):
    
    fields = OrderedDict([
    	("signature", "uint32"),#
		("signatureExtension", "short"),#
		("remID", "uint32"),#
		("dropMechanic", "uint32"),#
		("itemID", "uint32[16]"),#
		("itemQuantity", "ubyte[16]"),#
		("itemChance", "ubyte[16]"),#
    ])

class REMfile():
    itemFile = ItmFile()
    def __init__(self,path):
        with open(path,"rb") as file:
            self.rem = REM()
            self.rem.marshall(file)
    def __str__(self):
        first = True
        message = "%s %s -%s\n"%("Item".ljust(44),"Qt"," Drop%")
        message += "-"*len(message)+"\n"
        for itemid, quantity, chance in zip(self.rem.itemID, self.rem.itemQuantity, self.rem.itemChance):
            if itemid != 0 and quantity !=0:
                itemName = str(self.itemFile[itemid])
                itemName += '' if not (first and not self.rem.dropMechanic) else " (Guaranteed)"
                first = False
                message+="%s %2d - %3d%%\n"%((itemName+":").ljust(44), quantity, chance)
        return message
    
    def latex(self, doc):
        first = True
        tabula = pylatex.table.Tabular("l r r")
        tabula.add_row(["Item","Quantity","Drop %"])
        tabula.add_hline()
        for itemid, quantity, chance in zip(self.rem.itemID, self.rem.itemQuantity, self.rem.itemChance):
            if itemid != 0 and quantity !=0:
                itemName = str(self.itemFile[itemid])
                itemName += '' if not (first and not self.rem.dropMechanic) else " (Guaranteed)"
                first = False
                tabula.add_row([itemName,quantity, chance])
        doc.append(tabula)
                
         
class REMLib():
    def __init__(self):
        self.library = {}
        for rem in list(Path(chunkPath).rglob("*.REM")):
            index = rem.stem.replace("remData_","")
            self.library[int(index if index else 0)] = REMfile(rem)
    def __getitem__(self,key):
        return self.library[key]
    def __contains__(self, key):
        return key in self.library