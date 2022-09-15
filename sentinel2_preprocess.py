import os
import sys
import re
import tempfile
from glob import glob
from datetime import datetime,timedelta
import numpy as np
from subprocess import call
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
HOME = os.environ.get('HOME')
if HOME is None:
    HOME = os.environ.get('USERPROFILE')
TOPDIR = os.path.join(HOME,'Work')

# Default values
SITE = 'Cihea'
SERVER = 'satreps-nas'
PORT = 443
PYTHON_PATH = os.path.join(HOME,'miniconda3','python')
CMDDIR = os.path.join(HOME,'Automation')
SCRDIR = os.path.join(HOME,'SatelliteTool')
S2_DATA = os.path.join(TOPDIR,'Sentinel-2_Data')
GIS_FNAM = os.path.join(TOPDIR,'Shapefile','All_area_polygon_20210914','All_area_polygon_20210914.shp')
WV_FNAM = os.path.join(TOPDIR,'WorldView','wv2_180629_mul.tif')
RESAMPLE_PATH = '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/resample'
PARCEL_PATH = '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/parcel'
ATCOR_PATH = '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/atcor'
INTERP_PATH = '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/interp'
TENTATIVE_PATH = '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2/Cihea/tentative_interp'
TMAX = datetime.now().strftime('%Y%m%d')
GROW_PERIOD = 120 # day
TMGN = 90 # day
TSND = 30 # day

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('-S','--site',default=SITE,help='Site name (%(default)s)')
parser.add_argument('--server',default=None,help='Name of the server (%(default)s)')
parser.add_argument('-P','--port',default=None,type=int,help='Port# of the server (%(default)s)')
parser.add_argument('--python_path',default=PYTHON_PATH,help='Path to the Python (%(default)s)')
parser.add_argument('--cmddir',default=CMDDIR,help='Command folder (%(default)s)')
parser.add_argument('--scrdir',default=SCRDIR,help='Script folder (%(default)s)')
parser.add_argument('--s2_data',default=S2_DATA,help='Sentinel-2 data folder (%(default)s)')
parser.add_argument('--gis_fnam',default=GIS_FNAM,help='Parcel data file (%(default)s)')
parser.add_argument('--wv_fnam',default=WV_FNAM,help='WorldView data file (%(default)s)')
parser.add_argument('--resample_path',default=RESAMPLE_PATH,help='Sentinel-2 resample on NAS (%(default)s)')
parser.add_argument('--parcel_path',default=PARCEL_PATH,help='Sentinel-2 parcel on NAS (%(default)s)')
parser.add_argument('--atcor_path',default=ATCOR_PATH,help='Sentinel-2 atcor on NAS (%(default)s)')
parser.add_argument('--interp_path',default=INTERP_PATH,help='Sentinel-2 interp on NAS (%(default)s)')
parser.add_argument('--tentative_path',default=TENTATIVE_PATH,help='Sentinel-2 tentative_interp on NAS (%(default)s)')
parser.add_argument('-s','--tmin',default=None,help='Min date to send in the format YYYYMMDD (%(default)s)')
parser.add_argument('-e','--tmax',default=TMAX,help='Max date to send in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmin',default=None,help='Min date to calculate in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmax',default=None,help='Max date to calculate in the format YYYYMMDD (%(default)s)')
parser.add_argument('--grow_period',default=GROW_PERIOD,type=int,help='Length of growing period in day (%(default)s)')
parser.add_argument('--tmgn',default=TMGN,type=int,help='Margin of calculation period in day (%(default)s)')
parser.add_argument('--tsnd',default=TSND,type=int,help='Duration of data to send in day (%(default)s)')
parser.add_argument('--skip_geocor',default=False,action='store_true',help='Skip geocor (%(default)s)')
parser.add_argument('--skip_parcel',default=False,action='store_true',help='Skip parcel (%(default)s)')
parser.add_argument('--skip_atcor',default=False,action='store_true',help='Skip atcor (%(default)s)')
parser.add_argument('--skip_interp',default=False,action='store_true',help='Skip interp (%(default)s)')
parser.add_argument('--skip_upload',default=False,action='store_true',help='Skip upload (%(default)s)')
parser.add_argument('--keep_tentative',default=False,action='store_true',help='Keep tentative interp (%(default)s)')
parser.add_argument('-v','--verbose',default=False,action='store_true',help='Verbose mode (%(default)s)')
parser.add_argument('-d','--debug',default=False,action='store_true',help='Debug mode (%(default)s)')
args = parser.parse_args()
site_low = args.site.lower()
if site_low == 'none':
    s2_data = args.s2_data
else:
    s2_data = os.path.join(args.s2_data,args.site)
tmax = datetime.strptime(args.tmax,'%Y%m%d')
if args.tmin is not None:
    tmin = datetime.strptime(args.tmin,'%Y%m%d')
else:
    tmin = tmax-timedelta(days=args.tsnd)
if args.data_tmax is not None:
    d2 = datetime.strptime(args.data_tmax,'%Y%m%d')
else:
    d2 = tmax
if args.data_tmin is not None:
    d1 = datetime.strptime(args.data_tmin,'%Y%m%d')
else:
    d1 = d2-timedelta(days=(args.grow_period*2+args.tmgn*2))
data_years = np.arange(d1.year,d2.year+1,1)

with tempfile.NamedTemporaryFile(mode='w',suffix='.ini') as fp:
    fp.write('[DEFAULT]\n')
    fp.write('scr_dir                             = {}\n'.format(args.scrdir))
    fp.write('s2_data                             = {}\n'.format(s2_data))
    fp.write('gis_fnam                            = {}\n'.format(args.gis_fnam))
    fp.write('[main]\n')
    fp.write('#main.start_date                     =\n')
    fp.write('#main.end_date                       =\n')
    fp.write('main.first_date                     =\n')
    fp.write('main.last_date                      =\n')
    fp.write('main.s2_data                        = {}\n'.format(s2_data))
    fp.write('main.download                       = False\n')
    if args.skip_geocor:
        fp.write('main.geocor                         = False\n')
    else:
        fp.write('main.geocor                         = True\n')
    if args.skip_parcel:
        fp.write('main.parcel                         = False\n')
    else:
        fp.write('main.parcel                         = True\n')
    if args.skip_atcor:
        fp.write('main.atcor                          = False\n')
    else:
        fp.write('main.atcor                          = True\n')
    if args.skip_interp:
        fp.write('main.interp                         = False\n')
    else:
        fp.write('main.interp                         = True\n')
    fp.write('main.phenology                      = False\n')
    fp.write('main.extract                        = False\n')
    fp.write('main.formula                        = False\n')
    fp.write('main.estimate                       = False\n')
    fp.write('main.no_gui                         = True\n')
    fp.write('[geocor]\n')
    fp.write('geocor.ref_fnam                     = {}\n'.format(args.wv_fnam))
    fp.write('geocor.band_fnam                    = {}\n'.format(os.path.join(s2_data,'band_names.txt')))
    fp.write('#geocor.python_path                  = {}\n'.format(args.python_path))
    fp.write('geocor.scr_dir                      = {}\n'.format(args.scrdir))
    fp.write('[parcel]\n')
    fp.write('parcel.gis_fnam                     = {}\n'.format(args.gis_fnam))
    fp.write('parcel.mask_parcel                  = {}\n'.format(os.path.join(s2_data,'parcel_mask.tif')))
    fp.write('#parcel.python_path                  = {}\n'.format(args.python_path))
    fp.write('parcel.scr_dir                      = {}\n'.format(args.scrdir))
    fp.write('[atcor]\n')
    fp.write('atcor.gis_fnam                      = {}\n'.format(args.gis_fnam))
    fp.write('atcor.mask_studyarea                = {}\n'.format(os.path.join(s2_data,'studyarea_mask.tif')))
    fp.write('atcor.mask_parcel                   = {}\n'.format(os.path.join(s2_data,'parcel_mask.tif')))
    fp.write('#atcor.stat_fnam                     =\n')
    fp.write('#atcor.inds_fnam                     =\n')
    fp.write('#atcor.csv_flag                      = True\n')
    fp.write('#atcor.oflag                         = [False,False,False,False,False]\n')
    fp.write('#atcor.python_path                   = {}\n'.format(args.python_path))
    fp.write('atcor.scr_dir                       = {}\n'.format(args.scrdir))
    fp.write('[interp]\n')
    fp.write('#interp.csv_flag                     = True\n')
    fp.write('#interp.oflag                        = [False,True]\n')
    fp.write('#interp.python_path                  = {}\n'.format(args.python_path))
    fp.write('interp.scr_dir                      = {}\n'.format(args.scrdir))
    fp.seek(0)
    command = 'python'
    command += ' "{}"'.format(os.path.join(args.scrdir,'satellite_main.py'))
    command += ' "{}"'.format(fp.name)
    if args.debug:
        sys.stderr.write('{}\n'.format(command))
        sys.stderr.flush()
    else:
        call(command)

if not args.skip_geocor and not args.skip_upload:
    resample_dnam = os.path.join(s2_data,'resample')
    if not os.path.isdir(resample_dnam):
        pass
    else:
        for ystr in sorted(os.listdir(resample_dnam)):
            if not re.search('^\d\d\d\d$',ystr):
                continue
            year = int(ystr)
            if not year in data_years:
                continue
            dnam = os.path.join(resample_dnam,ystr)
            for f in sorted(os.listdir(dnam)):
                m = re.search('^('+'\d'*8+')_resample\.tif$',f)
                if not m:
                    continue
                dstr = m.group(1)
                d = datetime.strptime(dstr,'%Y%m%d')
                if d < tmin or d > tmax:
                    continue
                fnam = os.path.join(dnam,f)
                if args.debug:
                    sys.stderr.write('{}\n'.format(fnam))
                    sys.stderr.flush()
                fnams = glob(os.path.join(dnam,'{}_resample.*'.format(dstr)))
                if len(fnams) > 0:
                    command = 'python'
                    command += ' "{}"'.format(os.path.join(args.cmddir,'file_station_upload_files.py'))
                    for fnam in fnams:
                        command += ' "{}"'.format(fnam)
                    if args.server is not None:
                        command += ' --server {}'.format(args.server)
                    if args.port is not None:
                        command += ' --port {}'.format(args.port)
                    command += ' --srcdir {}/{}'.format(args.atcor_path,ystr)
                    if args.debug:
                        sys.stderr.write('{}\n'.format(command))
                        sys.stderr.flush()
                    else:
                        call(command)

if not args.skip_parcel and not args.skip_upload:
    parcel_dnam = os.path.join(s2_data,'parcel')
    if not os.path.isdir(parcel_dnam):
        pass
    else:
        for ystr in sorted(os.listdir(parcel_dnam)):
            if not re.search('^\d\d\d\d$',ystr):
                continue
            year = int(ystr)
            if not year in data_years:
                continue
            dnam = os.path.join(parcel_dnam,ystr)
            for f in sorted(os.listdir(dnam)):
                m = re.search('^('+'\d'*8+')_parcel\.npz$',f)
                if not m:
                    continue
                dstr = m.group(1)
                d = datetime.strptime(dstr,'%Y%m%d')
                if d < tmin or d > tmax:
                    continue
                fnam = os.path.join(dnam,f)
                if args.debug:
                    sys.stderr.write('{}\n'.format(fnam))
                    sys.stderr.flush()
                fnams = glob(os.path.join(dnam,'{}_parcel.*'.format(dstr)))
                if len(fnams) > 0:
                    command = 'python'
                    command += ' "{}"'.format(os.path.join(args.cmddir,'file_station_upload_files.py'))
                    for fnam in fnams:
                        command += ' "{}"'.format(fnam)
                    if args.server is not None:
                        command += ' --server {}'.format(args.server)
                    if args.port is not None:
                        command += ' --port {}'.format(args.port)
                    command += ' --srcdir {}/{}'.format(args.atcor_path,ystr)
                    if args.debug:
                        sys.stderr.write('{}\n'.format(command))
                        sys.stderr.flush()
                    else:
                        call(command)

if not args.skip_atcor and not args.skip_upload:
    atcor_dnam = os.path.join(s2_data,'atcor')
    if not os.path.isdir(atcor_dnam):
        pass
    else:
        for ystr in sorted(os.listdir(atcor_dnam)):
            if not re.search('^\d\d\d\d$',ystr):
                continue
            year = int(ystr)
            if not year in data_years:
                continue
            dnam = os.path.join(atcor_dnam,ystr)
            for f in sorted(os.listdir(dnam)):
                m = re.search('^('+'\d'*8+')_atcor\.npz$',f)
                if not m:
                    continue
                dstr = m.group(1)
                d = datetime.strptime(dstr,'%Y%m%d')
                if d < tmin or d > tmax:
                    continue
                fnam = os.path.join(dnam,f)
                if args.debug:
                    sys.stderr.write('{}\n'.format(fnam))
                    sys.stderr.flush()
                fnams = glob(os.path.join(dnam,'{}_atcor.*'.format(dstr)))
                if len(fnams) > 0:
                    command = 'python'
                    command += ' "{}"'.format(os.path.join(args.cmddir,'file_station_upload_files.py'))
                    for fnam in fnams:
                        command += ' "{}"'.format(fnam)
                    if args.server is not None:
                        command += ' --server {}'.format(args.server)
                    if args.port is not None:
                        command += ' --port {}'.format(args.port)
                    command += ' --srcdir {}/{}'.format(args.atcor_path,ystr)
                    if args.debug:
                        sys.stderr.write('{}\n'.format(command))
                        sys.stderr.flush()
                    else:
                        call(command)

if not args.skip_interp and not args.skip_upload:
    interp_dnam = os.path.join(s2_data,'interp')
    tentative_dnam = os.path.join(s2_data,'tentative_interp')
    if not os.path.isdir(interp_dnam):
        pass
    else:
        for ystr in sorted(os.listdir(interp_dnam)):
            if not re.search('^\d\d\d\d$',ystr):
                continue
            year = int(ystr)
            if not year in data_years:
                continue
            # Upload interp
            dnam = os.path.join(interp_dnam,ystr)
            for f in sorted(os.listdir(dnam)):
                m = re.search('^('+'\d'*8+')_interp\.npz$',f)
                if not m:
                    continue
                dstr = m.group(1)
                d = datetime.strptime(dstr,'%Y%m%d')
                if d < tmin or d > tmax:
                    continue
                fnam = os.path.join(dnam,f)
                if args.debug:
                    sys.stderr.write('{}\n'.format(fnam))
                    sys.stderr.flush()
                if not args.keep_tentative:
                    gnams = glob(os.path.join(tentative_dnam,ystr,'{}_interp.*'.format(dstr)))
                    if len(gnams) > 0:
                        for gnam in gnams:
                            os.remove(gnam)
                            if args.verbose:
                                sys.stderr.write('Removed {}\n'.format(gnam))
                                sys.stderr.flush()
                fnams = glob(os.path.join(dnam,'{}_interp.*'.format(dstr)))
                if len(fnams) > 0:
                    command = 'python'
                    command += ' "{}"'.format(os.path.join(args.cmddir,'file_station_upload_files.py'))
                    for fnam in fnams:
                        command += ' "{}"'.format(fnam)
                    if args.server is not None:
                        command += ' --server {}'.format(args.server)
                    if args.port is not None:
                        command += ' --port {}'.format(args.port)
                    command += ' --srcdir {}/{}'.format(args.interp_path,ystr)
                    if args.debug:
                        sys.stderr.write('{}\n'.format(command))
                        sys.stderr.flush()
                    else:
                        call(command)
            # Upload tentative interp
            dnam = os.path.join(tentative_dnam,ystr)
            for f in sorted(os.listdir(dnam)):
                m = re.search('^('+'\d'*8+')_interp\.npz$',f)
                if not m:
                    continue
                dstr = m.group(1)
                d = datetime.strptime(dstr,'%Y%m%d')
                if d < tmin or d > tmax:
                    continue
                fnam = os.path.join(dnam,f)
                if args.debug:
                    sys.stderr.write('{}\n'.format(fnam))
                    sys.stderr.flush()
                fnams = glob(os.path.join(dnam,'{}_interp.*'.format(dstr)))
                if len(fnams) > 0:
                    command = 'python'
                    command += ' "{}"'.format(os.path.join(args.cmddir,'file_station_upload_files.py'))
                    for fnam in fnams:
                        command += ' "{}"'.format(fnam)
                    if args.server is not None:
                        command += ' --server {}'.format(args.server)
                    if args.port is not None:
                        command += ' --port {}'.format(args.port)
                    command += ' --srcdir {}/{}'.format(args.tentative_path,ystr)
                    if args.debug:
                        sys.stderr.write('{}\n'.format(command))
                        sys.stderr.flush()
                    else:
                        call(command)
