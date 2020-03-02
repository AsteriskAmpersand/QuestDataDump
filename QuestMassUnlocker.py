# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 20:20:09 2019

@author: AsteriskAmpersand
"""
from pathlib import Path
from shutil import copyfile
from Encryption import replaceData
from MIBStructures import MIBFile
inpf = Path(r"E:\MHW\ChunkG0")
outpf = Path(r"E:\Program Files (x86)\Steam\steamapps\common\Monster Hunter World\nativePC(Quests)")

base = 90201
qd = "*questData_%s.mib"
st = "*%s*.gmd"
candidates = ["01131","01132","01133","01134","01231","01232","01233","01234","01235","01236","01237",
            "01238","01331","01332","01333","01334","01335","01336","01337","01338","01339","01340",
            "01431","01432","01433","01434","01435","01632","01633","01634","01635","01636"]

for ix,candidate in enumerate(candidates):
    print(candidate)
    index = str(base+ix)
    inQuest = next(inpf.rglob(qd%candidate))
    outFolder = outpf.joinpath(inQuest.parent.relative_to(inpf))
    outQuest = outFolder.joinpath("questData_%s.mib"%index)
    replaceData(inQuest,outQuest,base+ix)

    mibdata = MIBFile(outQuest)
    for monster in mibdata.mib.rawMonsters:
        monster.monsterHealth -= monster.HealthAndDamageVariance
        monster.HealthAndDamageVariance = 0
    mibdata.write(outQuest)

    for stringFile in [a for a in inpf.rglob(st%candidate) if "common" in str(a)]:
        outFolder = outpf.joinpath(stringFile.parent.relative_to(inpf))
        outQuest = outFolder.joinpath(stringFile.stem.replace(candidate,index)+".gmd")
        copyfile(stringFile, outQuest)