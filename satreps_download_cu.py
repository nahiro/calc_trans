import os
import sys
import re
import psutil
from datetime import datetime,timedelta
from subprocess import call
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
HOME = os.environ.get('HOME')
if HOME is None:
    HOME = os.environ.get('USERPROFILE')
TOPDIR = os.path.join(HOME,'Work')
TIME_NOW = datetime.now()

# Default values
SITES = ['Bojongsoang','Cihea']
BINDIR = os.path.join(HOME,'miniconda3','bin')
if os.path.isdir(BINDIR):
    PYTHON_PATH = os.path.join(BINDIR,'python')
else:
    PYTHON_PATH = os.path.join(HOME,'miniconda3','python')
CMDDIR = os.path.join(HOME,'Automation')
S1_DATA = os.path.join(TOPDIR,'Sentinel-1_Data')
S2_DATA = os.path.join(TOPDIR,'Sentinel-2_Data')
PMAX = 1

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-S','--sites',default=None,action='append',help='Target sites ({})'.format(SITES))
parser.add_argument('--python_path',default=PYTHON_PATH,help='Path to the Python (%(default)s)')
parser.add_argument('--cmddir',default=CMDDIR,help='Command folder (%(default)s)')
parser.add_argument('--topdir',default=TOPDIR,help='Top folder (%(default)s)')
parser.add_argument('--s1_data',default=None,help='Sentinel-1 data folder ({})'.format(S1_DATA))
parser.add_argument('--s2_data',default=None,help='Sentinel-2 data folder ({})'.format(S2_DATA))
parser.add_argument('--pmax',default=PMAX,type=int,help='Max number of processes allowed simultaneously (%(default)s)')
parser.add_argument('-U','--skip_s1_update',default=False,action='store_true',help='Skip sentinel1_update (%(default)s)')
parser.add_argument('-u','--skip_s2_update',default=False,action='store_true',help='Skip sentinel2_update (%(default)s)')
parser.add_argument('-p','--skip_s2_preprocess',default=False,action='store_true',help='Skip sentinel2_preprocess (%(default)s)')
args = parser.parse_args()
if args.sites is None:
    args.sites = SITES
if args.s1_data is None:
    args.s1_data = os.path.join(args.topdir,'Sentinel-1_Data')
if args.s2_data is None:
    args.s2_data = os.path.join(args.topdir,'Sentinel-2_Data')
gis_bojongsoang = os.path.join(args.topdir,'Shapefile','Bojongsoang','Bojongsoang.shp')
gis_cihea = os.path.join(args.topdir,'Shapefile','All_area_polygon_20210914','All_area_polygon_20210914.shp')
gis_testsite = os.path.join(args.topdir,'Shapefile','Testsite_polygon_20210914','Testsite_polygon_20210914.shp')
wv_bojongsoang = os.path.join(args.topdir,'WorldView','wv2_190816_mul.tif')
wv_cihea = os.path.join(args.topdir,'WorldView','wv2_180629_mul.tif')

script_name = os.path.basename(sys.argv[0]).lower()
pids = []
cmds = []
for p in psutil.process_iter(attrs=['pid','name','cmdline']):
    if p.info['cmdline'] is None:
        continue
    command = ' '.join(p.info['cmdline']).lower()
    if re.search('python',command) and re.search(script_name,command) and not re.search('powershell',command):
        pids.append(p.info['pid'])
        cmds.append(command)
if len(pids) > args.pmax:
    sys.stderr.write('\nProcess exists >>> {}\n'.format(len(pids)))
    for i in range(len(pids)):
        sys.stderr.write('{:3d} {:8d} {}\n'.format(i+1,pids[i],cmds[i]))
    sys.stderr.flush()
    sys.exit()

dend = TIME_NOW
dstr = dend-timedelta(days=280)

for site in args.sites:
    # Download/Upload GRD
    if site in ['Bojongsoang','Cihea']:
        command = args.python_path
        command += ' "{}"'.format(os.path.join(args.cmddir,'sentinel1_update.py'))
        command += ' --scrdir "{}"'.format(args.cmddir)
        command += ' --datdir "{}"'.format(args.s1_data)
        command += ' --sites {}'.format(site)
        command += ' --str {:%Y%m%d}'.format(dstr)
        command += ' --end {:%Y%m%d}'.format(dend)
        command += ' --skip_upload'
        try:
            if args.skip_s1_update:
                pass
            else:
                call(command,shell=True)
        except Exception as e:
            sys.stderr.write('{}\n'.format(e))
            sys.stderr.flush()

    # Download/Upload L2A
    if site in ['Bojongsoang']:
        command = args.python_path
        command += ' "{}"'.format(os.path.join(args.cmddir,'sentinel2_update.py'))
        command += ' --scrdir "{}"'.format(args.cmddir)
        command += ' --datdir "{}"'.format(args.s2_data)
        command += ' --sites {}'.format(site)
        command += ' --str {:%Y%m%d}'.format(dstr)
        command += ' --end {:%Y%m%d}'.format(dend)
        command += ' --skip_upload'
        try:
            if args.skip_s2_update:
                pass
            else:
                call(command,shell=True)
        except Exception as e:
            sys.stderr.write('{}\n'.format(e))
            sys.stderr.flush()
