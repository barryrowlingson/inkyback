#!/usr/bin/python

from datetime import datetime
from time import strftime
import os.path
import os
import sys
import glob
import shutil

import pruning

global options

def backupDir(archiveDir):
    """ return the path of a backup rooted at archiveDir for time=now """
    now = datetime.now()
    lastBit = "%02d_%02d" % (now.hour, now.minute)
    path = os.path.join(archiveDir, "%02d" % now.year, "%02d" % now.month, "%02d" % now.day, lastBit)
    return path

def getLockDir(archiveDir):
    """ try and get a lock on the archive """
    tmp=os.path.join(archiveDir,"lockdir")
    try:
        os.makedirs(tmp)
        return tmp
    except:
        raise ValueError("lockdir found in "+archiveDir+" - is another backup in progress?")

def unfPath(archiveDir, name="unfinished_backup"):
    """ returns the working path for a backup until it is complete """
    return os.path.join(archiveDir,name)

def checkUnfinished(archiveDir):
    """ test for an unfinished backup in this archive dir """
    unf = unfPath(archiveDir)
    if os.path.exists(unf):
        if options.verbose:
            print "removing previous incomplete backup"
        shutil.rmtree(unf)
    return unf

def makeBackupDir(archiveDir):
    """ create a backup directory in this archive """
    d=backupDir(archiveDir)
    try:
        os.makedirs(d)
        return (tmp,d)
    except:
        return None

def getAllBackups(archiveDir):
    """ find all the backups in this archive """
    return glob.glob(os.path.join(archiveDir,"????","??","??","??_??"))

def latestBackup(backups):
    """ get the most recent backup by getting all of them and sorting """
    if len(backups) == 0:
        return None
    backups.sort(cmp=lambda x,y: cmp(os.stat(y).st_ctime,os.stat(x).st_ctime))
    return backups[0]

from optparse import OptionParser

def opts():
    usage = "usage: %prog [options] <source dir> <archive dir>"
    parser = OptionParser(usage=usage)
    parser.add_option("-f","--filter",action="append",dest="filter",help="filter rules (repeatable)",type="string")
    parser.add_option("-p","--prune", action="store_true",default=False,dest="prune",help="prune y/m/w/d/h")
    parser.add_option("-v","--verbose", action="store_true",default=False,dest="verbose",help="show what we're doing")
    (options,args)=parser.parse_args()
    if len(args) != 2:
        parser.print_usage()
        sys.exit(2)
    options.source = args[0]
    options.dest = args[1]
    return options

def main():

    options = opts()
    
    src = options.source
    ad = options.dest
    
    d = getLockDir(ad)
    unf = checkUnfinished(ad)

    newDir = backupDir(ad)
    if os.path.exists(newDir):
        os.removedirs(d)
        raise ValueError("path "+newDir+" exists - wait 1 minute between backups")
    
    
    all = getAllBackups(ad)
    latest = latestBackup(all)

    if latest:
        if options.verbose:
            print "Making hard-link copy of previous backup.."
        os.system("cp -lR "+latest+" "+unf)

    if options.verbose:
        vstring="v"
    else:
        vstring=""

    fstring = ""
    if options.filter:
        for fil in options.filter:
            fstring = fstring + ' --filter="%s" ' % fil
        
    os.system('rsync -az'+vstring + fstring + ' --force --relative --hard-links --delete "'+src+'" "'+unf+'"')
    if options.verbose:
        print "now renaming ",unf," to ",newDir
    os.renames(unf, newDir)
    os.removedirs(d)

    if options.prune:
        pruning.prune(options,ad)
    
if __name__ == "__main__":
    main()

