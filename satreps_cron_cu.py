import os
from datetime import datetime
from subprocess import call
from argparse import ArgumentParser,RawTextHelpFormatter

# Constants
HOME = os.environ.get('HOME')
if HOME is None:
    HOME = os.environ.get('USERPROFILE')
TOPDIR = os.path.join(HOME,'Work')
TIME_NOW = datetime.now()

# Default values
BINDIR = os.path.join(HOME,'miniconda3','bin')
if os.path.isdir(BINDIR):
    PYTHON_PATH = os.path.join(BINDIR,'python')
else:
    PYTHON_PATH = os.path.join(HOME,'miniconda3','python')
CMDDIR = os.path.join(HOME,'Automation')
LOGDIR = os.path.join(TOPDIR,'SATREPS','Log')

# Read options
parser = ArgumentParser(formatter_class=lambda prog:RawTextHelpFormatter(prog,max_help_position=200,width=200))
parser.add_argument('--python_path',default=PYTHON_PATH,help='Path to the Python (%(default)s)')
parser.add_argument('--cmddir',default=CMDDIR,help='Command folder (%(default)s)')
parser.add_argument('--logdir',default=LOGDIR,help='Log folder (%(default)s)')
args = parser.parse_args()

logdir = os.path.join(args.logdir,'{:%Y}'.format(TIME_NOW))
if not os.path.exists(logdir):
    os.makedirs(logdir)
if not os.path.isdir(logdir):
    raise IOError('Error, no such directory >>> {}'.format(logdir))
logfile = os.path.join(logdir,'{:%Y%m%d}.log'.format(TIME_NOW))

command = args.python_path
command += ' "{}"'.format(os.path.join(args.cmddir,'satreps_automation_cu.py'))
command += ' --python_path "{}"'.format(args.python_path)
command += ' --pmax 2'
command += ' >>"{}" 2>&1'.format(logfile)
call(command,shell=True)
