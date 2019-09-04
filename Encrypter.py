# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 05:36:33 2019

@author: AsteriskAmpersand
"""
from Crypto.Cipher import Blowfish
from pathlib import Path

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
        
def endianness_reversal(data):
    return b''.join(map(lambda x: x[::-1],chunks(data, 4)))

def reverseCapcomBlowfish(file):
    cipher = Blowfish.new("TZNgJfzyD2WKiuV4SglmI6oN5jP2hhRJcBwzUooyfIUTM4ptDYGjuRTP".encode("utf-8"), Blowfish.MODE_ECB)
    return endianness_reversal(cipher.encrypt(endianness_reversal(file)))

for file in Path(r"E:\Projects\0-ArenaAkantorex\Marathonex\Decrypted").glob("*.bim"):
    with file.with_suffix(".mib").open("wb") as fib:
        fib.write(reverseCapcomBlowfish(file.open("rb").read()))