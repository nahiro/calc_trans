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

# Default values
BINDIR = os.path.join(HOME,'miniconda3','bin')
if os.path.isdir(BINDIR):
    PYTHON_PATH = os.path.join(BINDIR,'python')
else:
    PYTHON_PATH = os.path.join(HOME,'miniconda3','python')
CMDDIR = os.path.join(HOME,'Automation')
SCRDIR = os.path.join(HOME,'SatelliteTool')
S1_DATA = os.path.join(TOPDIR,'Sentinel-1_Data')
S2_DATA = os.path.join(TOPDIR,'Sentinel-2_Data')
S2_PATH = '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2'
UNZIP = '7za x -o@'

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('--python_path',default=PYTHON_PATH,help='Path to the Python (%(default)s)')
parser.add_argument('--cmddir',default=CMDDIR,help='Command folder (%(default)s)')
parser.add_argument('--scrdir',default=SCRDIR,help='Script folder (%(default)s)')
parser.add_argument('--topdir',default=TOPDIR,help='Top folder (%(default)s)')
parser.add_argument('--s1_data',default=None,help='Sentinel-1 data folder ({})'.format(S1_DATA))
parser.add_argument('--s2_data',default=None,help='Sentinel-2 data folder ({})'.format(S2_DATA))
parser.add_argument('--s2_path',default=S2_PATH,help='Sentinel-2 path on NAS (%(default)s)')
parser.add_argument('--unzip',default=UNZIP,help='Unzip command for L2A (%(default)s)')
parser.add_argument('-c','--skip_calc_trans',default=False,action='store_true',help='Skip calc_trans (%(default)s)')
parser.add_argument('-u','--skip_s2_update',default=False,action='store_true',help='Skip sentinel2_update (%(default)s)')
parser.add_argument('-p','--skip_s2_preprocess',default=False,action='store_true',help='Skip sentinel2_preprocess (%(default)s)')
args = parser.parse_args()
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
if len(pids) > 1:
    sys.stderr.write('\nProcess exists >>> {}\n'.format(len(pids)))
    for i in range(len(pids)):
        sys.stderr.write('{:3d} {:8d} {}\n'.format(i+1,pids[i],cmds[i]))
    sys.stderr.flush()
    sys.exit()

dend = datetime.now()
dstr = dend-timedelta(days=280)

for site in ['Bojongsoang','Cihea','Testsite']:
    # Download/Upload GRD, Calculate/Upload Planting
    if site in ['Bojongsoang','Cihea']:
        command = args.python_path
        command += ' "{}"'.format(os.path.join(args.cmddir,'auto_calc_trans.py'))
        command += ' --scrdir "{}"'.format(args.cmddir)
        command += ' --datdir "{}"'.format(args.s1_data)
        command += ' --sites {}'.format(site)
        command += ' --str {:%Y%m%d}'.format(dstr)
        command += ' --end {:%Y%m%d}'.format(dend)
        command += ' --skip_upload'
        try:
            if args.skip_calc_trans:
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

    # Calculate/Upload Preprocess
    command = args.python_path
    command += ' "{}"'.format(os.path.join(args.cmddir,'sentinel2_preprocess.py'))
    command += ' --python_path "{}"'.format(args.python_path)
    command += ' --cmddir "{}"'.format(args.cmddir)
    command += ' --scrdir "{}"'.format(args.scrdir)
    command += ' --site {}'.format(site)
    command += ' --s2_data "{}"'.format(args.s2_data)
    command += ' --geocor_path {}/{}/geocor'.format(args.s2_path,site)
    command += ' --indices_path {}/{}/indices'.format(args.s2_path,site)
    command += ' --parcel_path {}/{}/parcel'.format(args.s2_path,site)
    command += ' --atcor_path {}/{}/atcor'.format(args.s2_path,site)
    command += ' --interp_path {}/{}/interp'.format(args.s2_path,site)
    command += ' --tentative_path {}/{}/tentative_interp'.format(args.s2_path,site)
    command += ' --unzip "{}"'.format(args.unzip)
    command += ' --skip_upload'
    if site in ['Bojongsoang']:
        command += ' --gis_fnam "{}"'.format(gis_bojongsoang)
        command += ' --wv_fnam "{}"'.format(wv_bojongsoang)
        command += ' --subset_region "[107.54,107.75,-7.04,-6.95]"'
        command += ' --resample_region "[790585.0,799555.0,9224425.0,9229335.0]"'
        command += ' --cthr_avg 0.07'
        command += ' --cthr_std 0.06'
    elif site in ['Cihea']:
        command += ' --l2a_dir "!{}"'.format(os.path.join(args.s2_data,'Bojongsoang','L2A'))
        command += ' --search_key R032'
        command += ' --gis_fnam "{}"'.format(gis_cihea)
        command += ' --wv_fnam "{}"'.format(wv_cihea)
    elif site in ['Testsite']:
        command += ' --gis_fnam "{}"'.format(gis_testsite)
        command += ' --geocor_dir "!{}"'.format(os.path.join(args.s2_data,'Cihea','geocor'))
        command += ' --indices_dir "!{}"'.format(os.path.join(args.s2_data,'Cihea','indices'))
        command += ' --skip_geocor'
        command += ' --skip_indices'
    else:
        ValueError('Error, site={}'.format(site))
    if site in ['Bojongsoang','Cihea','Testsite']:
        try:
            if args.skip_s2_preprocess:
                pass
            else:
                call(command,shell=True)
        except Exception as e:
            sys.stderr.write('{}\n'.format(e))
            sys.stderr.flush()
