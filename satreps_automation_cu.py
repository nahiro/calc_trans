import os
import sys
import re
import psutil
from datetime import datetime,timedelta
from subprocess import call

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

HOME = os.environ.get('USERPROFILE')
if HOME is None:
    HOME = os.environ.get('HOME')
TOPDIR = os.path.join(HOME,'Work')

python_path = os.path.join(HOME,'miniconda3','bin','python')
cmddir = os.path.join(HOME,'Automation')
scrdir = os.path.join(HOME,'SatelliteTool')
s1_data = os.path.join(TOPDIR,'Sentinel-1_Data')
s2_data = os.path.join(TOPDIR,'Sentinel-2_Data')
s2_path = '/SATREPS/ipb/User/1_Spatial-information/Sentinel-2'
dend = datetime.now()
dstr = dend-timedelta(days=280)
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
        command += ' --skip_upload'
        try:
            call(command,shell=True)
        except Exception as e:
            sys.stderr.write('{}\n'.format(e))
            sys.stderr.flush()

    # Download/Upload L2A
    if site in ['Bojongsoang']:
        command = python_path
        command += ' "{}"'.format(os.path.join(cmddir,'sentinel2_update.py'))
        command += ' --scrdir "{}"'.format(cmddir)
        command += ' --datdir "{}"'.format(s2_data)
        command += ' --sites {}'.format(site)
        command += ' --str {:%Y%m%d}'.format(dstr)
        command += ' --end {:%Y%m%d}'.format(dend)
        command += ' --skip_upload'
        try:
            call(command,shell=True)
        except Exception as e:
            sys.stderr.write('{}\n'.format(e))
            sys.stderr.flush()

    # Calculate/Upload Preprocess
    command = python_path
    command += ' "{}"'.format(os.path.join(cmddir,'sentinel2_preprocess.py'))
    command += ' --cmddir "{}"'.format(cmddir)
    command += ' --scrdir "{}"'.format(scrdir)
    command += ' --site {}'.format(site)
    command += ' --s2_data "{}"'.format(s2_data)
    command += ' --geocor_path {}/{}/geocor'.format(s2_path,site)
    command += ' --indices_path {}/{}/indices'.format(s2_path,site)
    command += ' --parcel_path {}/{}/parcel'.format(s2_path,site)
    command += ' --atcor_path {}/{}/atcor'.format(s2_path,site)
    command += ' --interp_path {}/{}/interp'.format(s2_path,site)
    command += ' --tentative_path {}/{}/tentative_interp'.format(s2_path,site)
    command += ' --skip_upload'
    if site in ['Bojongsoang']:
        command += ' --gis_fnam "{}"'.format(gis_bojongsoang)
        command += ' --wv_fnam "{}"'.format(wv_bojongsoang)
        command += ' --subset_region "[107.54,107.75,-7.04,-6.95]"'
        command += ' --resample_region "[790585.0,799555.0,9224425.0,9229335.0]"'
        command += ' --cthr_avg 0.08'
    elif site in ['Cihea']:
        command += ' --l2a_dir "!{}"'.format(os.path.join(s2_data,'Bojongsoang','L2A'))
        command += ' --search_key R032'
        command += ' --gis_fnam "{}"'.format(gis_cihea)
        command += ' --wv_fnam "{}"'.format(wv_cihea)
    elif site in ['Testsite']:
        command += ' --gis_fnam "{}"'.format(gis_testsite)
        command += ' --geocor_dir "!{}"'.format(os.path.join(s2_data,'Cihea','geocor'))
        command += ' --indices_dir "!{}"'.format(os.path.join(s2_data,'Cihea','indices'))
        command += ' --skip_geocor'
        command += ' --skip_indices'
    else:
        ValueError('Error, site={}'.format(site))
    if site in ['Bojongsoang','Cihea','Testsite']:
        try:
            #call(command,shell=True)
            pass
        except Exception as e:
            sys.stderr.write('{}\n'.format(e))
            sys.stderr.flush()
