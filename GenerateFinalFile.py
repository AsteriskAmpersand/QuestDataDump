# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 19:15:02 2019

@author: AsteriskAmpersand
"""
from pathlib import Path
from MIBStructures import MIBFile
from pylatex import Document
from pylatex.utils import NoEscape

def errCal(mib):
    mibber = MIBFile(mib)
    string = str(mibber)
    return string

def Header():
    return """The following is a list of every single quest in the game with their respective relevant values, it's the consagration of close to 3/4 of a year of research into the game's quest system and related files including monster data. The credits for most of the body of MIB editing are numerous as is the number of volunteers who have contributed parts or the whole of sections. Thanks to Hexhexhex for the templates for difficulty (verified empirically by NekotagaYuhatora, Cloud Flare, Fahmeux, Kef and myself (*&/AsteriskAmpersand)), part of the monster hitzone values (the other half completed by me), the bigger share of the eda (completed thanks to the help of Cloud Flare and NekotagaYuhatora) and ordering swathes of the MIB research. I merely filled in the voids, and solved the remaining connections between files. As for the MIB structure itself, thanks to Zindea, Vuze, Nexusphobiker, TITAN, Wishmaker/JunkBunny, Fandirus, Approved, Mace ya face, Bedtime, Vuze, kkkkyue, elliotbw, again Hexhexhex and finally again myself, from the initial research that started the life of the MHW Modding Discord to which I also thank for being the amazing community they are. Additionaly thanks to r00tElement for the names of parts of monsters. https://discord.gg/gJwMdhK"""

dataDump = Path(r"G:\Wisdom\MHW-LibraryOfBabel.txt")
with open(dataDump,"w",encoding = "utf-8") as output:
    output.write(Header()+"\n")
    output.write("\n".join([errCal(quest) for quest in Path(r"E:\MHW").rglob("*.mib")]))
    

#dataDump = Path(r"G:\Wisdom\MHW-LibraryOfBabel")
#chapterString = NoEscape(r"""\titleformat{\chapter}[display]{\normalfont\bfseries}{}{0pt}{\Huge}"""+"\n")
#doc = Document(documentclass='report')
#doc.preamble.append(NoEscape(r"\usepackage{titlesec}"+"\n"))
#doc.preamble.append(chapterString)
#doc.preamble.append(NoEscape(r"\usepackage[document]{ragged2e}"))
#doc.append(Header())
#[MIBFile(quest).latex(doc) for quest in Path(r"E:\MHW").rglob("*.mib")]
#doc.generate_pdf(dataDump.as_posix())