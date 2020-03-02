# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 13:45:27 2020

@author: AsteriskAmpersand
"""

import shutil
import os
from pathlib import Path
from MIBStructures import MIBFile

chunk = r"E:\MHW\chunkG0"
dest = r"E:\IBProjects\HealthFix\nativePC"
for src_fpath in Path(chunk).rglob("*.mib"):
    dest_fpath = Path(dest).joinpath(src_fpath.relative_to(chunk))    
    os.makedirs(os.path.dirname(dest_fpath), exist_ok=True)
    shutil.copy(src_fpath, dest_fpath)
    
for mib in Path(dest).rglob("*.mib"):
    mibdata = MIBFile(mib)
    for monster in mibdata.mib.rawMonsters:
        monster.monsterHealth -= monster.HealthAndDamageVariance
        monster.HealthAndDamageVariance = 0
    outmib = str(mib)
    mibdata.write(outmib)