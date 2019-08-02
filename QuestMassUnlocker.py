# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 20:20:09 2019

@author: AsteriskAmpersand
"""
from pathlib import Path
from Crypto.Cipher import Blowfish
import sys
import struct
from shutil import copyfile

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
        
def endianness_reversal(data):
    return b''.join(map(lambda x: x[::-1],chunks(data, 4)))

def CapcomDecrypt(file):
    cipher = Blowfish.new(b"TZNgJfzyD2WKiuV4SglmI6oN5jP2hhRJcBwzUooyfIUTM4ptDYGjuRTP", Blowfish.MODE_ECB)
    return bytearray(endianness_reversal(cipher.decrypt(endianness_reversal(file))))

def CapcomEncrypt(file):
    cipher = Blowfish.new(b"TZNgJfzyD2WKiuV4SglmI6oN5jP2hhRJcBwzUooyfIUTM4ptDYGjuRTP", Blowfish.MODE_ECB)
    return endianness_reversal(cipher.encrypt(endianness_reversal(file)))

def replaceData(inFile, outFile, value):
    w = CapcomDecrypt(inFile.open("rb").read())
    w[6:10] = struct.pack("I",value)
    with outFile.open("wb") as outf:
        outf.write(CapcomEncrypt(w))
    return

inpf = Path(r"E:\MHW\Merged")
outpf = Path(r"E:\Program Files (x86)\Steam\steamapps\common\Monster Hunter World\nativePC(Quests)")

base = 90001
qd = "*questData_%s.mib"
st = "*%s*.gmd"
candidates = ['00331','00332','00333','00431','00432','00433','00434','00531',
              '00532','00533','00534','00631','00632','00633','00634','00635',
              '00636','00637','00731','00732','00733','00734','00735','00736',
              '00737','00738']#'62609','00804','00991'

for ix,candidate in enumerate(candidates):
    index = str(base+ix)
    inQuest = next(inpf.rglob(qd%candidate))
    outFolder = outpf.joinpath(inQuest.parent.relative_to(inpf))
    outQuest = outFolder.joinpath("questData_%s.mib"%index)
    replaceData(inQuest,outQuest,base+ix)
    for stringFile in [a for a in inpf.rglob(st%candidate) if "common" in str(a)]:
        outFolder = outpf.joinpath(stringFile.parent.relative_to(inpf))
        outQuest = outFolder.joinpath(stringFile.stem.replace(candidate,index)+".gmd")
        copyfile(stringFile, outQuest)
