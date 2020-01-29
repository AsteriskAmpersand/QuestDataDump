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

class values(PyCStruct):
    fields = OrderedDict([
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
        for field in list(self.fields.keys()):
            result.__setattr__(field,self.__getattribute__(field)*value.__getattribute__(field))
        return result

class unknTrail(PyCStruct):
    fields = OrderedDict([
		("unknownData", "int32[7]"),#
    ])
class Difficulty():
    def __init__(self):
        self.DifficultyHeader=Header()
        self.soloMultipliers= [values() for _ in range(1000)]
        self.mpMultipliers=[values() for _ in range(1000)]
        self.unknTrail = unknTrail()
    def marshall(self,data):
        self.DifficultyHeader.marshall(data)
        [solo.marshall(data) for solo in self.soloMultipliers]
        [mult.marshall(data) for mult in self.mpMultipliers]
        self.unknTrail.marshall(data)
    def serialize(self):
        result = self.DifficultyHeader.serialize()
        result+=b''.join([solo.serialize() for solo in self.soloMultipliers])
        result+=b''.join([mult.serialize() for mult in self.mpMultipliers])
        result+= self.unknTrail.serialize()
        return result
        

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
        