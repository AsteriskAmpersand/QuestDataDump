# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 15:59:11 2019

@author: AsteriskAmpersand
"""

from Cstruct import PyCStruct
from collections import OrderedDict
from Chunk import chunkPath

class Header (PyCStruct):
	fields = OrderedDict([
		("FileID", "uint32"),#
 ]);

class monCount (PyCStruct):
	fields = OrderedDict([
		("stringCount", "uint32"),#
    ])

class values(PyCStruct):
    fields = OrderedDict([
		("valueCount", "uint32"),#
		("monHPMultiplier", "float"),#
		("monDmgMultiplier", "float"),#
		("playerDmgMultiplier", "float"),#
		("monPartHP", "float"),#
		("monStatusBase", "float"),#
		("monStatusBuildup", "float"),#
		("monStun", "float"),#
		("monExhaust", "float"),#
		("monMount", "float"),#
    ])
    def toModifiers(self):
        return [self.__getattribute__(key) for key in list(self.fields.keys())[1:]]
    def __mul__(self, value):
        result = values()
        result.__setattr__("valueCount",self.valueCount)
        for field in list(self.fields.keys()):
            result.__setattr__(field,self.__getattribute__(field)*value.__getattribute__(field))
        return result

class Difficulty():
    def __init__(self):
        self.DifficultyHeader=Header()
        self.SoloCount=monCount()
        self.soloMultipliers= [values() for _ in range(100)]
        self.MultiCount=monCount()
        self.mpMultipliers=[values() for _ in range(100)]
    def marshall(self,data):
        self.DifficultyHeader.marshall(data)
        self.SoloCount.marshall(data)
        [solo.marshall(data) for solo in self.soloMultipliers]
        self.MultiCount.marshall(data)
        [mult.marshall(data) for mult in self.mpMultipliers]
    def serialize(self,data):
        self.DifficultyHeader.serialize()
        self.SoloCount.serialize()
        [solo.serialize() for solo in self.soloMultipliers]
        self.MultiCount.serialize()
        [mult.serialize() for mult in self.mpMultipliers]

class DifficultyFile():
    difficultyPath = r"%s\common\em\em_difficulty.dtt_dif"%chunkPath
    def __init__(self):
        with open(self.difficultyPath, "rb") as diff:
            self.Difficulty = Difficulty()
            self.Difficulty.marshall(diff)
    def spMod(self):
        return lambda key: self.Difficulty.soloMultipliers[key]
    def mpMod(self, hr):
        return lambda key: self.Difficulty.mpMultipliers[hr]*self.Difficulty.soloMultipliers[key]
        