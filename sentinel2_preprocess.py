import os
import sys
import re
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
