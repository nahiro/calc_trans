import os
import sys
import re
import tempfile
from datetime import datetime
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
HOME = os.environ.get('HOME')
if HOME is None:
    HOME = os.environ.get('USERPROFILE')
TOPDIR = os.path.join(HOME,'Work')

# Default values
SCRDIR = os.path.join(HOME,'SatelliteTool')
S2_DATA = os.path.join(TOPDIR,'Sentinel-2_Data')
GIS_FNAM = os.path.join(TOPDIR,'Shapefile','All_area_polygon_20210914','All_area_polygon_20210914.shp')
TMAX = datetime.now().strftime('%Y%m%d')
DATA_TMAX = TMAX
TMGN = 30

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('--scrdir',default=SCRDIR,help='Script folder (%(default)s)')
parser.add_argument('--s2_data',default=S2_DATA,help='Sentinel-2 data folder (%(default)s)')
parser.add_argument('--gis_fnam',default=GIS_FNAM,help='Parcel data (%(default)s)')
parser.add_argument('-s','--tmin',default=None,help='Min date for analysis in the format YYYYMMDD (%(default)s)')
parser.add_argument('-e','--tmax',default=TMAX,help='Max date for analysis in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmin',default=None,help='Min date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmax',default=DATA_TMAX,help='Max date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--tmgn',default=TMGN,type=float,help='Margin of input data in day (%(default)s)')
parser.add_argument('--skip_geocor',default=False,action='store_true',help='Skip geocor (%(default)s)')
parser.add_argument('--skip_parcel',default=False,action='store_true',help='Skip parcel (%(default)s)')
parser.add_argument('--skip_atcor',default=False,action='store_true',help='Skip atcor (%(default)s)')
parser.add_argument('--skip_interp',default=False,action='store_true',help='Skip interp (%(default)s)')
args = parser.parse_args()

tmin = datetime.strptime(args.tmin,'%Y%m%d')
tmax = datetime.strptime(args.tmax,'%Y%m%d')
d1 = datetime.strptime(args.data_tmin,'%Y%m%d')
d2 = datetime.strptime(args.data_tmax,'%Y%m%d')
data_years = np.arange(d1.year,d2.year+1,1)

with tempfile.TemporaryFile(suffix='.ini') as fp:
    fp.write('[DEFAULT]\n')
    fp.write('scr_dir                             = {}\n'.format(args.scrdir))
    fp.write('s2_data                             = {}\n'.format(args.s2_data))
    fp.write('gis_fnam                            = {}\n'.format(args.gis_fnam))
    fp.write('[main]\n')
    fp.write('#main.start_date                     =\n')
    fp.write('#main.end_date                       =\n')
    fp.write('main.first_date                     =\n')
    fp.write('main.last_date                      =\n')
    fp.write('main.s2_data                        = {}\n'.format(args.s2_data))
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
    fp.write('geocor.ref_fnam                     = %(top_dir)s/WorldView/wv2_180629_mul.tif\n')
    fp.write('geocor.band_fnam                    = %(s2_data)s/band_names.txt\n')
    fp.write('#geocor.python_path                  = %(python_path)s\n')
    fp.write('geocor.scr_dir                      = %(scr_dir)s\n')
    fp.write('[parcel]\n')
    fp.write('parcel.gis_fnam                     = %(gis_fnam)s\n')
    fp.write('parcel.mask_parcel                  = %(s2_data)s/parcel_mask.tif\n')
    fp.write('#parcel.python_path                  = %(python_path)s\n')
    fp.write('parcel.scr_dir                      = %(scr_dir)s\n')
    fp.write('[atcor]\n')
    fp.write('atcor.gis_fnam                      = %(gis_fnam)s\n')
    fp.write('atcor.mask_studyarea                = %(s2_data)s/studyarea_mask.tif\n')
    fp.write('atcor.mask_parcel                   = %(s2_data)s/parcel_mask.tif\n')
    fp.write('#atcor.stat_fnam                     =\n')
    fp.write('#atcor.inds_fnam                     =\n')
    fp.write('#atcor.csv_flag                      = True\n')
    fp.write('#atcor.oflag                         = [False,False,False,False,False]\n')
    fp.write('#atcor.python_path                   = %(python_path)s\n')
    fp.write('atcor.scr_dir                       = %(scr_dir)s\n')
    fp.write('[interp]\n')
    fp.write('#interp.csv_flag                     = True\n')
    fp.write('#interp.oflag                        = [False,True]\n')
    fp.write('#interp.python_path                  = %(python_path)s\n')
    fp.write('interp.scr_dir                      = %(scr_dir)s\n')

if not args.skip_geocor:
    geocor_dnam = os.path.join(args.s2_data,'geocor')
    for ystr in soreted(os.listdir(geocor_dnam)):
        if not re.search('^\d\d\d\d$',ystr):
            continue
        year = int(ystr)
