import sys
import psutil
import time

for p in psutil.process_iter(attrs=['pid','name','cmdline']):
    print(p.info['cmdline'])

time.sleep(1000)
