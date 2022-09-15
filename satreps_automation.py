import os
import sys
import re
import psutil
import time

script_name = os.path.basename(sys.argv[0])
pids = []
for p in psutil.process_iter(attrs=['pid','name','cmdline']):
    if p.info['cmdline'] is None:
        continue
    command = ' '.join(p.info['cmdline'])
    if re.search('python',command) and re.search(script_name,command):
        pids.append(p.info['pid'])
if len(pids) > 1:
    sys.stderr.write('Process exists >>> {}'.format(len(pids)))
    sys.stderr.flush()
    sys.exit()

HOME = os.environ.get('USERPROFILE')
if HOME is None:
    HOME = os.environ.get('HOME')
TOPDIR = 'F:\Work'

python_path = os.path.join(HOME,'miniconda3','python.exe')
cmddir = os.path.join(HOME,'Automation')
scrdir = os.path.join(HOME,'SatelliteTool')

for site in ['Cihea','Bojongsoang','Testsite']:
    # Download/Upload GRD, Calculate/Upload Planting
    if site != 'Testsite':
        s1_data = os.path.join(TOPDIR,'Sentinel-1_Data')
        command = python_path
        command += ' "{}"'.format(os.path.join(cmddir,'auto_calc_trans.py'))
        command += ' --datdir "{}"'.format(s1_data)
        command += ' --sites {}'.format(site)
        command += ' --skip_copy'
        call(command,shell=True)

    # Download/Upload L2A, Calculate/Upload Preprocess
    s2_data = os.path.join(TOPDIR,'Sentinel-2_Data',site)
    command = python_path
