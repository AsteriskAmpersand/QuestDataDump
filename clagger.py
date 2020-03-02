# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 19:09:06 2020

@author: AsteriskAmpersand
"""
from Cstruct import PyCStruct
from collections import OrderedDict
from Chunk import chunkPath
from pathlib import Path
from FileLike import FileLike

class Header(PyCStruct):
    fields = OrderedDict([
         ("IB" , "byte[4]"),
         ("unkn0" , "int32"),
         ("cnt" , "int32"),])

class Clagger(PyCStruct):
    fields = OrderedDict([
         ("unkn0" , "int32"),
         ("normal" , "float"),
         ("enrage" , "float"),
         ("fatigue" , "float"),
         ("hpRangeMod" ,"float[10]"),
         ("lowr" , "float"),
         ("highr" , "float"),
         ("masterr" , "float"),])
    def __repr__(self):
        return ','.join([str(getattr(self,f)) for f in self.fields if "unkn" not in f])
    def header(self):
        return ','.join([f for f in self.fields.keys() if "unkn" not in f])
class Trail(PyCStruct):
    fields = OrderedDict([
         ("unkn" , "int32[3]")])

class ClaggerCommon():
    defaultPath = Path(chunkPath).joinpath(r"common\em\em_clawgrab_common.dtt_clawc")
    def __init__(self):
        self.Header = Header()
        self.ClaggerTables = []
    def marshall(self,data):
        self.Header.marshall(data)
        self.ClaggerTables = [Clagger().marshall(data) for i in range(self.Header.cnt)]
        self.Trail =  Trail().marshall(data)
    @staticmethod
    def open(filepath = None):
        if filepath is None:
            filepath=ClaggerCommon.defaultPath
        clag = ClaggerCommon()
        with open(filepath,"rb") as inf:
            clag.marshall(FileLike(inf.read()))
        return clag
    def __getitem__(self,ix):
        return self.ClaggerTables[ix]