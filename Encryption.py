# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 22:15:54 2020

@author: AsteriskAmpersand
"""
from FileLike import FileLike
from Crypto.Cipher import Blowfish
import struct

MIBKEY = b"TZNgJfzyD2WKiuV4SglmI6oN5jP2hhRJcBwzUooyfIUTM4ptDYGjuRTP"
EPGKEY = b"sJV4g7d55gKnQB5nS6XJ9pZ1qZmmQwNnSbidUW1OeAhHrpPd6MKbfsrt"
EDAKEY = b"Fqkpg1xx1cMlvg3AtKOCLxFgVFBwHkCbjizBRV49hWmEe5lOAaNOTm7m"
AEQKEY = b"b71AMFJuw63cUTlDt5ntSAtaAvwLKizNtapy4W0QAsC39QXPr6b78Asz"
LOTKEY = b"D7N88VEGEnRl0HEHTO0xMQkbeMb37arJF488lREp90WYojAONkLoxfMt"
SHPKEY = b"FZoS8QLyOyeFmkdrz73P9Fh2N4NcTwy3QQPjc1YRII5KWovK6yFuU8SL"
PLPKEY = b"j1P15gEkgVa7NdFxiqwCPitykHctY2nZPjSaElvqb0eSwcLO1cOlTqqv"

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
        
def endianness_reversal(data):
    return b''.join(map(lambda x: x[::-1],chunks(data, 4)))

def CapcomDecrypt(file, key = MIBKEY):
    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    return bytearray(endianness_reversal(cipher.decrypt(endianness_reversal(file))))

def CapcomEncrypt(file, key = MIBKEY):
    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    return endianness_reversal(cipher.encrypt(endianness_reversal(file)))

def DecryptFile(file, key = MIBKEY):
    result = file.read()
    return FileLike(CapcomDecrypt(result,key))

def EncryptFile(file,key = MIBKEY):
    data = file.read()
    return CapcomEncrypt(data,key)

def DecryptReplace(file,key=MIBKEY):
    with open(file,"rb") as inf:
        data = DecryptFile(inf,key).read()
    with open(file,"wb") as outf:
        outf.write(data)
        
def EncryptReplace(file,key=MIBKEY):
    with open(file,"rb") as inf:
        data = EncryptFile(inf,key)
    with open(file,"wb") as outf:
        outf.write(data)
        
def replaceData(inFile, outFile, value):
    w = inFile.open("rb").read()#CapcomDecrypt()
    #w[10:14] = struct.pack("I",value)
    with outFile.open("wb") as outf:
        outf.write(w)#CapcomEncrypt()
    return