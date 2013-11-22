
import sys
from datetime import datetime
import glob
import os.path
import os
import shutil

start=datetime(1900,1,1)

Unknown, Keep, Delete = ['Unknown','Keep','Delete']

class Backup:
    """ Class for representing a backup in an archive """
    def __init__(self,archiveDir,backupDir):
        """ Constructor for Backup objects """
        self.archiveDir = archiveDir
        self.backupDir = backupDir
        # now parse the path into time parts 
        (rest,time) = os.path.split(backupDir)
        (self.hour,self.minute) = time.split("_")
        self.hour = int(self.hour)
        self.minute = int(self.minute)
        (rest,self.day) = os.path.split(rest)
        self.day = int(self.day)
        (rest,self.month) = os.path.split(rest)
        self.month = int(self.month)
        (rest,self.year) = os.path.split(rest)
        self.year = int(self.year)
        self.dtime = datetime(self.year,self.month,self.day,self.hour,self.minute,00)

        self.dday = (self.dtime-start).days 
        self.dhour = self.dday*24 + self.hour
        self.dweek = self.dday/7
        self.dmonth = self.year*12 + self.month
        self.status = Unknown
        self.reason = ""
        return
    def __repr__(self):
        return "<Backup: %s %s (%s)>" % (self.dtime, self.status, self.reason)
        return "<Backup: %s h%d d%d w%d m%d y%d >" % (self.dtime,self.dhour,self.dday,self.dweek,self.dmonth,self.year)
        return "<Backup: %s/%02d/%02d %02d:%02d (%d,%d)>" % (self.year,self.month,self.day,self.hour,self.minute,self.dday,self.dweek)
    def setStatus(self, status, reason):
        self.status=status
        self.reason=reason

def mycmp(self,other):
    return -cmp(self.dtime,other.dtime)
        
def setStatus(backups, groupBy):
    groups={}
    for b in backups:
        val=getattr(b,groupBy)
        if not groups.has_key(val):
            groups[val]=[]
        groups[val].append(b)
    for g in groups.keys():
        groups[g].sort(cmp=mycmp)
        [x.setStatus(Delete,groupBy) for x in groups[g]]
        groups[g][0].status=Keep
    return groups

def getBackups(archiveRoot):
    """ get a list of all backups in an archive """
    allDirs = glob.glob(os.path.join(archiveRoot,"*","*","*","*_*"))
    all = [Backup(archiveRoot,x) for x in allDirs]
    return all

def splitHour(backupSet,now):
    thisHour = [x for x in backupSet if x.year==now.year and x.month==now.month and x.day==now.day and x.hour==now.hour]
    notThisHour = set(backupSet)-set(thisHour)
    return( (thisHour,notThisHour) )

def splitDay(backupSet,now):
    thisDay = [x for x in backupSet if x.year==now.year and x.month==now.month and x.day==now.day]
    notThisDay = set(backupSet)-set(thisDay)
    return( (thisDay, notThisDay) )

def splitWeek(backupSet,now):
    thisWeek = [x for x in backupSet if (now-x.dtime).days < 7]
    notThisWeek = set(backupSet)-set(thisWeek)
    return( (thisWeek, notThisWeek) )

def splitMonth(backupSet,now):
    """ month here is last 28 days """
    #    thisMonth = [x for x in backupSet if x.year==now.year and x.month==now.month ]
    thisMonth = [x for x in backupSet if (now-x.dtime).days < 28 ]
    notThisMonth = set(backupSet)-set(thisMonth)
    return( (thisMonth, notThisMonth) )

def splitYear(backupSet,now):
    thisYear = [x for x in backupSet if x.year==now.year]
    notThisYear = set(backupSet)-set(thisYear)
    return( (thisYear, notThisYear) )

def listing(backupSet):
    return "\n".join([str(x) for x in backupSet])
    

def checkArchive(archiveDir, now=datetime.now()):
    all=getBackups(archiveDir)

    (hours,others) = splitHour(all,now)
    (todays, others) =  splitDay(others,now)
    (weeks,others) = splitWeek(others,now)
    (months, others) = splitMonth(others,now)
    (years,others) = splitYear(others,now)
    hours.sort(mycmp)
    todays.sort(mycmp)
    weeks.sort(mycmp)
    months.sort(mycmp)
    years.sort(mycmp)
    setStatus(hours,'dhour')
    setStatus(todays,'dhour')
    setStatus(weeks,'dday')
    setStatus(months,'dweek')
    setStatus(years,'dmonth')
    setStatus(others,'year')
    all.sort(mycmp)
    return(all)

from optparse import OptionParser

def opts():
    usage = "usage: %prog [options] archive"
    parser = OptionParser(usage)
    parser.add_option("-p","--prune", action="store_true",default=False,dest="prune",help="prune y/m/w/d/h backups")
    parser.add_option("-v","--verbose", action="store_true",default=False,dest="verbose",help="show what we're doing")
    (options,args)=parser.parse_args()
    if len(args) != 1:
        parser.error("archive not given")
        sys.exit(2)
    return (options,args[0])


def zap(a):
    # this deletes the last part of the backup path, the time:
    shutil.rmtree(a.backupDir)
    # so now remove the day/m/year if empty 
    cp=os.path.normpath(a.backupDir)
    (ymd,t)=os.path.split(cp)
    try:
        os.rmdir(ymd)
    except:
        pass
    (ym,d)=os.path.split(ymd)
    try:
        os.rmdir(ym)
    except:
        pass
    (y,m)=os.path.split(ym)
    try:
        os.rmdir(y)
    except:
        pass

def main():
    (options,archiveDir) = opts()
    prune(options,archiveDir)
        
def prune(options,archiveDir):
    all = checkArchive(archiveDir)
    if not options.prune and options.verbose:
        print "Dry run..."
    for a in all:
        if a.status==Delete:
            if options.verbose:
                print "deleting: ",a.backupDir
            if options.prune:
                zap(a)
        if a.status==Keep:
            if options.verbose:
                print "keeping: ",a.backupDir
        if a.status==Unknown:
            print "Unknown backup ",a

if __name__=="__main__":
    main()
