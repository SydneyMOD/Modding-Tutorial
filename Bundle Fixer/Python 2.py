"""
This code is from 'https://bitbucket.org/Frankelstner/pd2-hashlist/src/2b2d2f8a100ba52670b2a9aa3875debc8e11ef8a/bundle%20fixer.py?at=master&fileviewer=file-view-default'.
"""

"""
This changes the bundle metadata back to the way it used to be, so the Bundle Modder will access the files just fine.
Run this script before the Bundle Modder to fix the bundles. Whenever the game gets an update, this script must run again,
or the Bundle Modder will not work correctly.

Effects of the script:

1. The script moves the all_h.bundle file to the location of the script, possibly overwriting it if it already exists there.
   It basically stays there as a backup just in case.
   Moving is actually not necessary if you only want to extract but there is no real harm either.
   I still think that the old format is better in every respect anyway.
2. The script reads in the all_h.bundle and uses the info to create individual all_xy_h.bundle.
   As you can see below, I just feed in lots and lots of constants that I am not sure about.
   The Bundle Modder and the game run fine though.

Requires Python, preferably 2.7: https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi

Adjust the path p if necessary.
If the path is invalid, the script will try to find the assets folder on its own and use the first one that it finds.
Double click the file to run; or right click -> Edit with IDLE -> F5.
The script location must not be the assets folder if you want to use the Bundle Modder to apply mods outside the override folder.
"""


p = r"C:\Program Files (x86)\Steam\steamapps\common\PAYDAY 2\assets"

##################################
##################################
##################################
from binascii import hexlify, unhexlify
from collections import OrderedDict
import os, sys
from struct import pack, unpack

def AllMeta(source):
    """Read all_h.bundle."""
    f = open(source,"rb")
    eof, bundleCount, _,_,_ = unpack("5I",f.read(20))
    offsets, entryCounts = [], []
    for i in xrange(bundleCount):
        index, entryCount, entryCount2, offset, one = unpack("QIIQI",f.read(28))
        assert entryCount == entryCount2
        assert index == i
        assert one == 1
        entryCounts.append(entryCount)
        offsets.append(offset+4)

    rv = []
    for i in xrange(bundleCount):
        dat = OrderedDict()
        f.seek(offsets[i])
        for entry in xrange(entryCounts[i]):
            index, offset, size = unpack("III",f.read(12))
            dat[index] = (offset, size)
        rv.append(dat)
    f.close()
    return rv
# If user did not bother to give the right path, try to figure it out.
if not os.path.exists(p):
    try:
        from _winreg import *
    except ImportError:
        from winreg import *
    paths = [QueryValueEx(OpenKey(HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam"), "SteamPath")[0]]
    if paths[0] and os.path.exists(paths[0]+"/steamapps/libraryfolders.vdf"):
        for line in open(paths[0]+"/steamapps/libraryfolders.vdf"):
            pieces = line.split('"')
            if len(pieces)==5 and pieces[3][1:4]==":\\\\":
                paths.append(pieces[3].replace("\\\\","/"))
    for p2 in [p2+"/steamapps/common/PAYDAY 2/assets" for p2 in paths]:
        if os.path.exists(p2):
            p=p2
            break

# Move the all_h.bundle from the assets folder to the script folder.
if os.path.exists(p+"/all_h.bundle"):
    target = os.path.dirname(__file__)+"/all_h.bundle"
    if os.path.exists(target):
        os.remove(target)
    os.rename(p+"/all_h.bundle", target)

# Write the new _h bundles.
for i, dat in enumerate(AllMeta("all_h.bundle")):
    f = open(p+"/all_"+str(i)+"_h.bundle","wb")
    fileSize = 7*4 + len(dat)*12+4
    f.write(pack("I",fileSize))
    f.write(unhexlify("F297A000"))
    f.write(pack("II",len(dat),len(dat)))
    f.write(unhexlify("18000000ACEC180001ED1800"))
    for index, (offset, size) in dat.iteritems():
        f.write(pack("III", index, offset, size))
    f.write(unhexlify("191FC59400000000"))
    f.close()