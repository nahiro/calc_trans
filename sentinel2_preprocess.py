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

# Default values
SCRDIR = os.path.join(HOME,'SatelliteTool')
TMAX = datetime.now().strftime('%Y%m%d')
DATA_TMAX = TMAX
TMGN = 30

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('--scrdir',default=SCRDIR,help='Script directory (%(default)s)')
parser.add_argument('-s','--tmin',default=None,help='Min date for analysis in the format YYYYMMDD (%(default)s)')
parser.add_argument('-e','--tmax',default=TMAX,help='Max date for analysis in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmin',default=None,help='Min date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--data_tmax',default=DATA_TMAX,help='Max date of input data in the format YYYYMMDD (%(default)s)')
parser.add_argument('--tmgn',default=TMGN,type=float,help='Margin of input data in day (%(default)s)')
args = parser.parse_args()

tmp_fnam = 'temp'
with open(tmp_fnam) as fp:
    fp.write('[DEFAULT]\n')
    fp.write('HOME                                = %(USERPROFILE)s\n')
    fp.write('top_dir                             = %(HOME)s/Work\n')
    fp.write('scr_dir                             = %(HOME)s/SatelliteTool\n')
    fp.write('s1_data                             = %(top_dir)s/Sentinel-1_Data\n')
    fp.write('s1_analysis                         = %(top_dir)s/Sentinel-1_Analysis/Current\n')
    fp.write('s2_data                             = %(top_dir)s/Sentinel-2_Data\n')
    fp.write('s2_analysis                         = %(top_dir)s/Sentinel-2_Analysis/Current\n')
    fp.write('gis_fnam                            = %(top_dir)s/Shapefile/All_area_polygon_20210914/All_area_polygon_20210914.shp\n')
    fp.write('[main]\n')
    fp.write('#main.start_date                     =\n')
    fp.write('#main.end_date                       =\n')
    fp.write('main.first_date                     =\n')
    fp.write('main.last_date                      =\n')
    fp.write('main.s2_data                        = %(s2_data)s\n')
    fp.write('main.s2_analysis                    = %(s2_analysis)s\n')
    fp.write('main.download                       = False\n')
    fp.write('main.geocor                         = True\n')
    fp.write('main.parcel                         = True\n')
    fp.write('main.atcor                          = True\n')
    fp.write('main.interp                         = True\n')
    fp.write('main.phenology                      = False\n')
    fp.write('main.extract                        = False\n')
    fp.write('main.formula                        = False\n')
    fp.write('main.estimate                       = False\n')
    fp.write('main.no_gui                         = True\n')
