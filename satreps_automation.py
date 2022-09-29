import os
import sys
import re
import psutil
from datetime import datetime,timedelta
from subprocess import call

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
s1_data = os.path.join(TOPDIR,'Sentinel-1_Data')
s2_data = os.path.join(TOPDIR,'Sentinel-2_Data')
s2_path = '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2'
dend = datetime.now()
dstr = dend-timedelta(days=180)
gis_bojongsoang = os.path.join(TOPDIR,'Shapefile','Bojongsoang','Bojongsoang.shp')
gis_cihea = os.path.join(TOPDIR,'Shapefile','All_area_polygon_20210914','All_area_polygon_20210914.shp')
gis_testsite = os.path.join(TOPDIR,'Shapefile','Testsite_polygon_20210914','Testsite_polygon_20210914.shp')
wv_bojongsoang = os.path.join(TOPDIR,'WorldView','wv2_190816_mul.tif')
wv_cihea = os.path.join(TOPDIR,'WorldView','wv2_180629_mul.tif')

for site in ['Bojongsoang','Cihea','Testsite']:
    # Download/Upload GRD, Calculate/Upload Planting
    if site in ['Bojongsoang','Cihea']:
        command = python_path
        command += ' "{}"'.format(os.path.join(cmddir,'auto_calc_trans.py'))
        command += ' --scrdir "{}"'.format(cmddir)
        command += ' --datdir "{}"'.format(s1_data)
        command += ' --sites {}'.format(site)
        command += ' --str {:%Y%m%d}'.format(dstr)
        command += ' --end {:%Y%m%d}'.format(dend)
        command += ' --skip_copy'
        try:
            call(command,shell=True)
        except Exception:
            pass

    # Download/Upload L2A
    if site in ['Bojongsoang']:
        command = python_path
        command += ' "{}"'.format(os.path.join(cmddir,'sentinel2_update.py'))
        command += ' --scrdir "{}"'.format(cmddir)
        command += ' --datdir "{}"'.format(s2_data)
        command += ' --sites {}'.format(site)
        command += ' --str {:%Y%m%d}'.format(dstr)
        command += ' --end {:%Y%m%d}'.format(dend)
        command += ' --skip_copy'
        try:
            call(command,shell=True)
        except Exception:
            pass

    # Calculate/Upload Preprocess
    command = python_path
    command += ' "{}"'.format(os.path.join(cmddir,'sentinel2_preprocess.py'))
    command += ' --cmddir "{}"'.format(cmddir)
    command += ' --scrdir "{}"'.format(scrdir)
    command += ' --site {}'.format(site)
    command += ' --s2_data "{}"'.format(s2_data)
    command += ' --geocor_path {}/{}/geocor'.format(s2_path,site)
    command += ' --parcel_path {}/{}/parcel'.format(s2_path,site)
    command += ' --atcor_path {}/{}/atcor'.format(s2_path,site)
    command += ' --interp_path {}/{}/interp'.format(s2_path,site)
    command += ' --tentative_path {}/{}/tentative_interp'.format(s2_path,site)
    if site in ['Bojongsoang']:
        command += ' --gis_fnam "{}"'.format(gis_bojongsoang)
        command += ' --wv_fnam "{}"'.format(wv_bojongsoang)
    elif site in ['Cihea']:
        command += ' --l2a_dir "!{}"'.format(os.path.join(s2_data,'Bojongsoang','L2A'))
        command += ' --search_key R032'
        command += ' --gis_fnam "{}"'.format(gis_cihea)
        command += ' --wv_fnam "{}"'.format(wv_cihea)
    elif site in ['Testsite']:
        command += ' --gis_fnam "{}"'.format(gis_testsite)
        command += ' --indices_dir "!{}"'.format(os.path.join(s2_data,'Cihea','indices'))
        command += ' --skip_geocor'
        command += ' --skip_indices'
    else:
        ValueError('Error, site={}'.format(site))
    if site in ['Cihea','Testsite']:
        try:
            call(command,shell=True)
        except Exception:
            pass
