#!/usr/bin/env python
import os
import sys
import re
import numpy as np
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from subprocess import call
from optparse import OptionParser,IndentedHelpFormatter

# Default values
HOME = os.environ.get('HOME')
if HOME is None:
    HOME = os.environ.get('USERPROFILE')
SCRDIR = os.path.join(HOME,'Automation')
DATDIR = os.path.join(HOME,'Work','Sentinel-1_Data')
END = datetime.now().strftime('%Y%m%d')
STR = END-timedelta(days=30)
SITES = ['Bojongsoang','Cihea']
SUBDIRS = ['Cihea:sigma0','Bojongsoang:sigma0_speckle']
P_VERSIONS = ['Cihea:v1.2','Bojongsoang:v1.0']
F_VERSIONS = ['Cihea:v1.4','Bojongsoang:v1.0']
DATE_FINAL = 5
MAX_RETRY = 10

# Read options
parser = OptionParser(formatter=IndentedHelpFormatter(max_help_position=200,width=200))
parser.add_option('--scrdir',default=SCRDIR,help='Script directory (%default)')
parser.add_option('--datdir',default=DATDIR,help='Data directory (%default)')
parser.add_option('-s','--str',default=STR,help='Start date in the format YYYYMMDD (%default)')
parser.add_option('-e','--end',default=END,help='End date in the format YYYYMMDD (%default)')
parser.add_option('-S','--sites',default=None,action='append',help='Target sites ({})'.format(SITES))
parser.add_option('--subdirs',default=None,action='append',help='Sub data directory, for example, Cihea:sigma0 ({})'.format(SUBDIRS))
parser.add_option('--p_versions',default=None,action='append',help='Version of preliminary transplanting estimation, for example, Cihea:v1.0 ({})'.format(P_VERSIONS))
parser.add_option('--f_versions',default=None,action='append',help='Version of final transplanting estimation, for example, Cihea:v1.0 ({})'.format(F_VERSIONS))
parser.add_option('--date_final',default=DATE_FINAL,type='int',help='Date to calculate final estimation (%default)')
parser.add_option('-M','--max_retry',default=MAX_RETRY,type='int',help='Maximum number of retries to download data (%default)')
parser.add_option('--skip_upload',default=False,action='store_true',help='Skip upload (%default)')
parser.add_option('--skip_copy',default=False,action='store_true',help='Skip copy (%default)')
parser.add_option('--overwrite',default=False,action='store_true',help='Overwrite mode (%default)')
parser.add_option('-d','--debug',default=False,action='store_true',help='Debug mode (%default)')
(opts,args) = parser.parse_args()
if opts.sites is None:
    opts.sites = SITES
if opts.subdirs is None:
    opts.subdirs = SUBDIRS
subdir = {}
for s in opts.subdirs:
    m = re.search('([^:]+):([^:]+)',s)
    if not m:
        raise ValueError('Error in subdir >>> '+s)
    subdir.update({m.group(1).lower():m.group(2)})
if opts.p_versions is None:
    opts.p_versions = P_VERSIONS
p_version = {}
for s in opts.p_versions:
    m = re.search('([^:]+):([^:]+)',s)
    if not m:
        raise ValueError('Error in version >>> '+s)
    p_version.update({m.group(1).lower():m.group(2)})
if opts.f_versions is None:
    opts.f_versions = F_VERSIONS
f_version = {}
for s in opts.f_versions:
    m = re.search('([^:]+):([^:]+)',s)
    if not m:
        raise ValueError('Error in version >>> '+s)
    f_version.update({m.group(1).lower():m.group(2)})

for site in opts.sites:
    site_low = site.lower()
    datdir = os.path.join(opts.datdir,site)
    dnam = os.path.join(datdir,'GRD')
    if not os.path.exists(dnam):
        os.makedirs(dnam)
    if not os.path.isdir(dnam):
        raise IOError('Error, no such folder >>> {}'.format(dnam))
    log = os.path.join(dnam,site_low+'.log')
    command = 'python'
    command += ' '+os.path.join(opts.scrdir,'sentinel1_update.py')
    command += ' --scrdir {}'.format(opts.scrdir)
    command += ' --datdir {}'.format(opts.datdir)
    if opts.str is not None:
        command += ' --str {}'.format(opts.str)
    if opts.end is not None:
        command += ' --end {}'.format(opts.end)
    if opts.skip_upload:
        command += ' --skip_upload'
    if opts.skip_copy:
        command += ' --skip_copy'
    command += ' --sites {}'.format(site)
    #sys.stderr.write(command+'\n')
    call(command,shell=True)
    fnams = []
    dstrs = []
    dtims = []
    if opts.str is not None and opts.end is not None:
        dmin = datetime.strptime(opts.str,'%Y%m%d')
        dmax = datetime.strptime(opts.end,'%Y%m%d')
        for year in range(dmin.year,dmax.year+1):
            dnam = os.path.join(datdir,'GRD','{:04d}'.format(year))
            if not os.path.isdir(dnam):
                continue
            for f in sorted(os.listdir(dnam)):
                m = re.search('^S1[AB]_IW_GRDH_1SDV_('+'\d'*8+')T\S+\.zip$',f)
                if not m:
                    continue
                dstr = m.group(1)
                d = datetime.strptime(dstr,'%Y%m%d')
                if d < dmin or d > dmax:
                    continue
                fnam = os.path.join(dnam,f)
                fnams.append(fnam)
                dstrs.append(dstr)
                dtims.append(d)
    elif os.path.exists(log):
        with open(log,'r') as fp:
            for line in fp:
                item = line.split()
                if len(item) < 1:
                    continue
                fnam = item[0]
                f = os.path.basename(fnam)
                #S1A_IW_GRDH_1SDV_20171227T223338_20171227T223405_019894_021DC8_434F.zip
                #S1B_IW_GRDH_1SDV_20200116T223300_20200116T223336_019848_025883_2DEF.zip
                m = re.search('^S1[AB]_IW_GRDH_1SDV_('+'\d'*8+')T\S+\.zip$',f)
                if not m:
                    continue
                dstr = m.group(1)
                d = datetime.strptime(dstr,'%Y%m%d')
                fnams.append(fnam)
                dstrs.append(dstr)
                dtims.append(d)
    else:
        raise ValueError('Error, failed in determining Start/End date.')
    if len(dstrs) < 1:
        continue
    indx = np.argsort(dtims)
    fnams = [fnams[i] for i in indx]
    dstrs = [dstrs[i] for i in indx]
    dtims = [dtims[i] for i in indx]
    dnam = os.path.join(datdir,'subset')
    if not os.path.exists(dnam):
        os.makedirs(dnam)
    if not os.path.isdir(dnam):
        raise IOError('Error, no such folder >>> {}'.format(dnam))
    for fnam in fnams:
        command = 'python'
        command += ' '+os.path.join(opts.scrdir,'sentinel1_preprocess.py')
        command += ' '+fnam
        command += ' --site {}'.format(site)
        command += ' --datdir {}'.format(dnam)
        if 'speckle' in subdir[site_low].lower():
            command += ' --speckle'
        command += ' --iangle_value'
        command += ' --std_grid'
        command += ' --tiff'
        call(command,shell=True)
        # Remove cache
        command = 'python'
        command += ' '+os.path.join(opts.scrdir,'remove_snap_cache.py')
        call(command,shell=True)
    dnam = os.path.join(datdir,'resample')
    if not os.path.exists(dnam):
        os.makedirs(dnam)
    if not os.path.isdir(dnam):
        raise IOError('Error, no such folder >>> {}'.format(dnam))
    for dstr,dtim in zip(dstrs,dtims):
        fnam = os.path.join(datdir,'subset','{}_subset.tif'.format(dstr))
        gnam = os.path.join(datdir,'resample','{}_resample.tif'.format(dstr))
        command = 'python'
        command += ' '+os.path.join(opts.scrdir,'sentinel_resample.py')
        command += ' --inp_fnam {}'.format(fnam)
        command += ' --out_fnam {}'.format(gnam)
        command += ' --site {}'.format(site)
        command += ' --read_comments'
        call(command,shell=True)
        d1 = (dtim+timedelta(days=-1)).strftime('%Y%m%d')
        d2 = (dtim+timedelta(days=+1)).strftime('%Y%m%d')
        wrkdir = os.path.join(opts.wrkdir,site,'preliminary',p_version[site_low],dstr)
        gnam = os.path.join(wrkdir,'trans_date_{}_{}_preliminary.shp'.format(site_low,dstr))
        if os.path.exists(gnam) and not opts.overwrite:
            pass
        else:
            command = 'python'
            command += ' '+os.path.join(opts.scrdir,'get_preliminary_estimation.py')
            command += ' --scrdir {}'.format(opts.scrdir)
            command += ' --datdir {}'.format(opts.datdir)
            command += ' --str {}'.format(d1)
            command += ' --end {}'.format(d2)
            command += ' --sites {}'.format(site)
            if opts.skip_upload:
                command += ' --skip_upload'
            if opts.skip_copy:
                command += ' --skip_copy'
            call(command,shell=True)
    if opts.str is not None and opts.end is not None:
        pass
    elif opts.str is not None:
        dmax = dtims[-1]
    elif opts.end is not None:
        dmin = dtims[0]
    else:
        dmin = dtims[0]
        dmax = dtims[-1]
    dtim = dmin
    while dtim <= dmax:
        if dtim.day == opts.date_final:
            dnex = dtim+relativedelta(months=1)
            if (dtim+timedelta(days=1)).month != dnex.month: # not the end of month
                dstr = (datetime(dtim.year,dtim.month,1)-timedelta(days=1)).strftime('%Y%m%d')
            else:
                dstr = dtim.strftime('%Y%m%d')
            d1 = dtim.strftime('%Y%m%d')
            d2 = d1
            wrkdir = os.path.join(opts.wrkdir,site,'final',f_version[site_low],dstr)
            gnam = os.path.join(wrkdir,'trans_date_{}_{}_final.shp'.format(site_low,dstr))
            if os.path.exists(gnam) and not opts.overwrite:
                pass
            else:
                command = 'python'
                command += ' '+os.path.join(opts.scrdir,'get_final_estimation.py')
                command += ' --scrdir {}'.format(opts.scrdir)
                command += ' --datdir {}'.format(opts.datdir)
                command += ' --str {}'.format(d1)
                command += ' --end {}'.format(d2)
                command += ' --sites {}'.format(site)
                if opts.skip_upload:
                    command += ' --skip_upload'
                if opts.skip_copy:
                    command += ' --skip_copy'
                call(command,shell=True)
        dtim += timedelta(days=1)
    if os.path.exists(log):
        os.remove(log)
