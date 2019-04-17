# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 14:28:16 2019

@author: AsteriskAmpersand
"""

from Cstruct import PyCStruct
from collections import OrderedDict
from GMD import GMDFile
from Chunk import chunkPath

class ItmHeader  (PyCStruct):
	fields = OrderedDict([
		("identifier", "uint16"),# // 0x00AE
		("num_entries", "uint32"),#
])

class ItmEntry  (PyCStruct):
    itemName = GMDFile(r"%s\common\text\steam\item_eng.gmd"%chunkPath)
    fields = OrderedDict([
		("id", "uint32"),#
		("sub_type", "ubyte"),# // 0: item, 1: ammunition, 4: coating
		("type", "uint32"),# // 0: Item, 1: Monster Material, 2: Endemic Life, 3: Ammunition/Coating, 4: Jewel
		("rarity", "ubyte"),#
		("carry_limit", "ubyte"),#
		("unk_limit", "ubyte"),#
		("sort_order", "uint16"),#
		("flags", "uint32"),#
		("icon_id", "uint32"),#
		("icon_color", "uint16"),#
		("sell_price", "uint32"),#
		("buy_price", "uint32"),#
])
    def __str__(self):
        return self.itemName[self.id*2]

class Itm  ():
    def __init__(self):
        self.header = ItmHeader()
        self.entries = []
    def marshall(self,data):
        self.header.marshall(data)
        for entry in range(self.header.num_entries): self.entries.append(ItmEntry())
        for entry in self.entries: entry.marshall(data)
    def serialize(self):
        return self.header.serialize + b''.join([entry.serialize() for entry in self.entries])

class ItmFile():
    itemPath = r"%s\common\item\itemData.itm"%chunkPath
    def __init__(self):
        with open(self.itemPath,"rb") as file:
            self.itm = Itm()
            self.itm.marshall(file)
    def __getitem__(self, index):
        return self.itm.entries[index]