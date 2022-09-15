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

time.sleep(1000)
