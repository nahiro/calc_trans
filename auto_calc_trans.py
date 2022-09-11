#!/usr/bin/env python
import os
import sys
import re
from datetime import datetime,timedelta
from subprocess import call
from optparse import OptionParser,IndentedHelpFormatter

# Default values
HOME = os.environ.get('HOME')
if HOME is None:
    HOME = os.environ.get('USERPROFILE')
SCRDIR = os.path.join(HOME,'Automation')
DATDIR = os.path.join(HOME,'Work','Sentinel-1_Data')
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
parser.add_option('-s','--str',default=None,help='Start date in the format YYYYMMDD (%default)')
parser.add_option('-e','--end',default=None,help='End date in the format YYYYMMDD (%default)')
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
                fnams.append(fnam)
                dstrs.append(m.group(1))
    if len(dstrs) < 1:
        continue
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
    for dstr in dstrs:
        fnam = os.path.join(datdir,'subset','{}_subset.tif'.format(dstr))
        gnam = os.path.join(datdir,'resample','{}_resample.tif'.format(dstr))
        command = 'python'
        command += ' '+os.path.join(opts.scrdir,'sentinel_resample.py')
        command += ' --inp_fnam {}'.format(fnam)
        command += ' --out_fnam {}'.format(gnam)
        command += ' --site {}'.format(site)
        command += ' --read_comments'
        call(command,shell=True)
        dtim = datetime.strptime(dstr,'%Y%m%d')
        d1 = (dtim+timedelta(days=-1)).strftime('%Y%m%d')
        d2 = (dtim+timedelta(days=+1)).strftime('%Y%m%d')
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
    if os.path.exists(log):
        os.remove(log)

dcur = datetime.now()
if dcur.day == opts.date_final:
    for site in opts.sites:
        command = 'python'
        command += ' '+os.path.join(opts.scrdir,'get_final_estimation.py')
        command += ' --scrdir {}'.format(opts.scrdir)
        command += ' --datdir {}'.format(opts.datdir)
        command += ' --sites {}'.format(site)
        if opts.skip_upload:
            command += ' --skip_upload'
        if opts.skip_copy:
            command += ' --skip_copy'
        call(command,shell=True)
