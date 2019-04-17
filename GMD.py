# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 14:37:33 2019

@author: AsteriskAmpersand
"""

from Cstruct import PyCStruct
from collections import OrderedDict

class GmdInfoEntry  (PyCStruct):
	fields = OrderedDict([
		("string_index", "uint32"),#
		("hash_key_2x", "int32"),# // signed_crc32(key_value + key_value)
		("hash_key_3x", "int32"),# // signed_crc32(key_value + key_value + key_value)
		("pad", "uint32"),# // always 0xCDCDCDCD
		("key_offset", "uint64"),#
		("bucket_index", "uint64"),#
])

class GmdString(PyCStruct):
    def __init__(self, count):
        self.fields = {"string":"char[%d]"%(count)}
        super().__init__()
    def __str__(self):
        return ''.join(self.string[:-1])

class GmdHeader  (PyCStruct):
    fields = OrderedDict([
		("magic", "uint32"),# // 0x00444d47, "GMD\00"
		("version", "uint32"),#
		("lang_id", "uint32"),#
		("unknown1", "uint32"),#
		("unknown2", "uint32"),#
		("key_count", "uint32"),#
		("string_count", "uint32"),#
		("key_block_size", "uint32"),#
		("string_block_size", "uint32"),#
		("name_size", "uint32"),#
		#("name", "char[name_size+1]"),# // null byte terminated string
])
    def marshall(self,data):
        super().marshall(data)
        self.name = GmdString(self.name_size+1)
        self.name.marshall(data)
    def serialize(self):
        return super().serialize()+self.name.serialize()

class GmdBucket(PyCStruct):
    fields = OrderedDict([
		("buckets", "uint64[256]"),])

class Gmd  ():
    def __init__(self):
        self.header = GmdHeader()
        self.info_entries = []
        self.buckets = GmdBucket()
        self.keyblock = None
        self.string_block = None
    def marshall(self,data):
        self.header.marshall(data)
        for entry in range(self.header.key_count):self.info_entries.append(GmdInfoEntry())
        for entry in self.info_entries:entry.marshall(data)
        self.buckets.marshall(data)
        self.keyblock = GmdString(self.header.key_block_size)
        self.keyblock.marshall(data)
        self.keyblock= self.keyblock.string.split('\x00')
        self.string_block = GmdString(self.header.string_block_size)
        self.string_block.marshall(data)
        self.string_block = self.string_block.string.split('\x00')
        
        
    def serialize(self):
        return self.header.serialize +\
                b''.join([e.serialize() for e in self.info_entries]) +\
                self.buckets.serialize() +\
                self.keyblock.serialize() +\
                self.string_block.serialize()
                
class GMDFile():
    def __init__(self, path):
        with open(path,"rb") as file:
            self.gmd = Gmd()
            self.gmd.marshall(file)
    def __getitem__(self, index):
        return self.gmd.string_block[index]
