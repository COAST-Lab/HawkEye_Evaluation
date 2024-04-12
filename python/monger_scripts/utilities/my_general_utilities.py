#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
sys.dont_write_bytecode = True
from subprocess import call
import time

import numpy as np
import glob
import zipfile, tarfile
import shutil

from my_hdf_cdf_utilities import *
import map_coords

import subprocess #Added for Sean Bailey's fix in lines 172... to avoid reading hdf file
import bz2
import datetime
#from numpy import *  commented out on Janury 2020




def fname_convention(fname):
    # Determine if fnme convention is orginal or new convention...
    # ---
    file_basename= os.path.basename(fname)
    first_fname_piece=  file_basename.split('_',1)[0]

    #PACE_OCI_SIM.20220321T170000.L2.OC_BGC.V8.nc

    missions_list= ['SEASTAR', 'AQUA', 'TERRA', 'SNPP', 'NOAA20', 'ENVISAT', 'S3A', 'S3B', 'S2A', 'S2B', 'LANDSAT8','SEAHAWK1','PACE']
    sentinel_2_3_meris_landsat_L1A=  '_OL_1' in file_basename or '_MSIL1' in file_basename  or '.N1' in file_basename or 'LC08' in file_basename


    if first_fname_piece in missions_list and not sentinel_2_3_meris_landsat_L1A:
        fname_type= 'new'

    else: fname_type= 'old'

    return fname_type

# Converts old ocssw filename convention with julia day to Mission_Instrument_Type.YYYYMMDDTHHMMSS

def fname_new_from_old(fname):
    file_basename= os.path.basename(fname)
    fname_type= fname_convention(file_basename)  # retruns 'new' or 'old'  if sentinel, meris or landsat L1, then also old...
    sentinel_meris_landsat_L1A= '_OL_1' in file_basename or '_MSIL1' in file_basename  or 'MER_' in file_basename or 'LC08' in file_basename

    if fname_type == 'old' :

        if not sentinel_meris_landsat_L1A:

            YYYYDDD= file_basename[1:8]
            YYYYMMDD= datetime.datetime.strptime(YYYYDDD, '%Y%j').date().strftime('%Y%m%d')
            HHMMSS=   file_basename[8:14]
            new_ocssw_time= YYYYMMDD + 'T' + HHMMSS

            if file_basename[0] == 'S' and not 'MLAC' in file_basename and not 'GAC' in file_basename:
                new_l2fname= 'SEASTAR_SEAWIFS' + '.' + new_ocssw_time

            if file_basename[0] == 'S' and 'MLAC' in file_basename:
                new_l2fname= 'SEASTAR_SEAWIFS_MLAC' + '.' + new_ocssw_time

            if file_basename[0] == 'S' and 'GAC' in file_basename:
                new_l2fname= 'SEASTAR_SEAWIFS_GAC' + '.' + new_ocssw_time

            if file_basename[0] == 'A':
                new_l2fname= 'AQUA_MODIS' + '.' + new_ocssw_time

            if file_basename[0] == 'T':
                new_l2fname= 'TERRA_MODIS' + '.' + new_ocssw_time

            if file_basename[0] == 'V' and 'SNPP' in file_basename:
                new_l2fname= 'SNPP_VIIRS' + '.' + new_ocssw_time

            if file_basename[0] == 'V'and 'JPSS' in file_basename:
                new_l2fname= 'NOAA20_VIIRS' + '.' + new_ocssw_time

            if file_basename[0] == 'H':
                new_l2fname= 'ISS_HICO' + '.' + new_ocssw_time

        '''
        if 'N1' in file_basename:
            merris_date=  file_basename[14:22]
            merris_time=  file_basename[23:29]
            meris_date_time= merris_date + 'T' + merris_time

            if 'FRS' in file_basename: new_l2fname= 'ENVISAT_MERIS_FRS' + '.' + meris_date_time
            if 'RR' in file_basename: new_l2fname= 'ENVISAT_MERIS_RR' + '.' + meris_date_time
        '''



        if 'MER_' in file_basename:
            meris_date_time= file_basename[20:35]
            if 'FRS' in file_basename: new_l2fname= 'ENVISAT_MERIS_FRS' + '.' + meris_date_time
            if 'RR' in file_basename: new_l2fname= 'ENVISAT_MERIS_RR' + '.' + meris_date_time

        if 'S3A' in file_basename or 'S3B' in file_basename:
            olci_date_time= file_basename[16:31]

        if 'S3A' in file_basename:
            if 'EFR'in file_basename: new_l2fname= 'S3A_OLCI_EFR' + '.' + olci_date_time
            if 'ERR'in file_basename: new_l2fname= 'S3A_OLCI_ERR' + '.' + olci_date_time

        if 'S3B' in file_basename:
            if 'EFR'in file_basename: new_l2fname= 'S3B_OLCI_EFR' + '.' + olci_date_time
            if 'ERR'in file_basename: new_l2fname= 'S3B_OLCI_ERR' + '.' + olci_date_time


        if '_MSIL1' in file_basename:
            msi_date_time=  file_basename[11:26]

        if 'S2A' in file_basename: new_l2fname= 'S2A_MSI' + '.' + msi_date_time

        if 'S2B' in file_basename: new_l2fname= 'S2B_MSI' + '.' +  msi_date_time


        if 'LC08' in file_basename:
            split_name= file_basename.split('_')
            YYYMMDD= split_name[3]
            oli_date_time= YYYMMDD + 'T' + '000000'
            new_l2fname= 'LANDSAT8_OLI' + '.' + oli_date_time


        return(new_l2fname)


    if fname_type == 'new' :
        split_name= file_basename.split('.')
        new_l2fname= split_name[0] + '.' + split_name[1]

        return(new_l2fname)


def YYYYDDDHHMMSS_from_new_fname(ifile):
    file_basename= os.path.basename(ifile)
    YYYYMMDDTHHMMSS= file_basename.split('.')[1]
    root_year=  YYYYMMDDTHHMMSS[0:4]
    root_mom=   YYYYMMDDTHHMMSS[4:6]
    root_day=   YYYYMMDDTHHMMSS[6:8]
    root_HHMMSS=YYYYMMDDTHHMMSS[9:15]
    root_jday= datetime.datetime.strptime(root_year + '-' + root_mom +'-'+ root_day, '%Y-%m-%d').timetuple().tm_yday
    YYYYDDDHHMMSS= root_year + '%03d' % root_jday + root_HHMMSS
    return(YYYYDDDHHMMSS)


def rebin(a,new_shape):
    a_view= a.reshape(new_shape[0],a.shape[0]/new_shape[0],new_shape[1],a.shape[1]/new_shape[1])
    return a_view.mean(axis=3).mean(axis=1)



def filebreak(full_fname):

    if isinstance(full_fname,str) == 1:
       full_fname= [full_fname]

    result= np.empty([len(full_fname),2], dtype=object)

    for i in range(len(full_fname)):
        result[i,0]=os.path.dirname(full_fname[i])
        result[i,1]=os.path.basename(full_fname[i])

    return result


def untar_ocweb(indir):

    tar_fnames= glob.glob(indir + '/*.tar')
    for name in tar_fnames:
        os.system('tar -C ' + indir + ' -xvf ' + name)
    os.system('mv ' + indir + '/requested_files/* ' + indir)
    os.system('rmdir ' + indir + '/requested_files')
    os.system('rm ' + indir + '/*.tar')






# unzips and extracts tar and zip to same directory
# puts old compressed files in separate directory
# input:
#   file ==> zipped file
#
def decompress_file(file):
    file_base = os.path.basename(file)
    path = os.path.dirname(file)
    new_dir = os.path.dirname(path) + '/compressed/'

    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    if zipfile.is_zipfile(file):
        zip = zipfile.ZipFile(file)
        zip.extractall(path + '/')
        shutil.move(file, new_dir + file_base)
    elif file[-3:] == 'bz2':
        print('extracting bz2')
        print(file)
        os.system('bunzip2 -k ' + file)
        shutil.move(file, new_dir + file_base)
    elif tarfile.is_tarfile(file):
        print('extracting tar')
        print(file)
        print(path)
        os.system('tar -C ' + path + ' -xvf ' + file)
        print('check 1')
        print(glob.glob(path + '/*'))
        shutil.move(file, new_dir + file_base)
        print('check 2')
        print(glob.glob(path + '/*'))
    elif (file.find('.gz') != -1):
        outfile = file[:file.rindex('.')]
        os.system("gunzip -c " + file + ' > ' + outfile)
        shutil.move(file, new_dir + file_base)
    else:
        print("Wrong archive or filename")



#
# returns True is file is a zipped or tarred file
# else returns false
#
def is_compressed(file):

    if os.path.isfile(file) ==True:
        return zipfile.is_zipfile(file) or tarfile.is_tarfile(file) or (file.find('.gz') != -1) or (file.find('bz2') != -1)
    else: return ('')



# inputs:
#   data ==> 2D array of values
#   latitudes ==> 1D array of latitudes
#   longitudes ==> 1D array of longitudes
#   xdim ==> number of x pixels in output image
#   ydim ==> number of y pixels in output image
# output: 2D array of size (xdim, ydim)
#
def map_resize(data, latitudes, longitudes, xdim, ydim):
    lon1 = -180.0
    lon2 = 180.0
    lat1 = -90.0
    lat2 = 90.0

    mapped = np.empty((ydim,xdim))
    mapped[:,:] = np.nan

    pixels_per_lat = ydim/(lat2 - lat1)
    pixels_per_lon = xdim/(lon2 - lon1)

    # map longitudes and latitudes to pixel number
    lon_pix = np.where(longitudes <= 180, (longitudes+180)*pixels_per_lon, (longitudes-179)*pixels_per_lon)
    lat_pix = [(lat + 90)*pixels_per_lat for lat in latitudes]

    # put each lat/lon in its spot on rectangular grid
    def func(lat,lon,value): mapped[lat,lon] = value
    list(map( lambda i: [func(lat_pix[i], lon_pix[j], data[i,j]) for j in range(0,len(lon_pix))] ,list(range(0,len(lat_pix))) ))


    return mapped



#
# get rid of ~ at beginning and / at end of file name
#
def path_reformat(path):
    path = path.strip()

    # get rid of troublesome '/' at end
    if path[-1] == '/':
        path = path[:-1]

    # get complete path
    if path[0] == '~':
        path = os.path.expanduser(path)

    return path


# input: file ==> data file with name including 'satID,year,jday,hour,min,sec', e.g. 'A2013125220000'
# output: integer julian day
#
def get_jday(file):
    file_base = os.path.basename(file)

    if file_base[0] != 'L' and file_base[0:3] != 'S2A' and file_base[0:3] != 'S2B': return int(file_base[5:8])
    if file_base[0] == 'L' : return int(file_base[13:16])
    if file_base[0:3] == 'S2A' or file_base[0:3] == 'S2B': return int(file_base[7:10])


def leap_year_check(year):
    if year % 4 == 0 and year % 100 != 0: year_type= 'leap_year'
    elif year % 400 ==0: year_type= 'leap_year'
    elif year % 100 == 0:year_type= 'not_leap_year'
    else: year_type= 'not_leap_year'

    return(year_type)


#
# input: list of files [file1,file2,...], list of averages ['DLY','WKY','MON'] and an integer year
# output: [([start, end], [file1,file2,...]), ([start, end], [file1,file2,...]), ([start, end] ,[file1,file2,...]), ...]
#
def get_average(filelist, time_period, year):


    file_basename= [os.path.basename(fname_new_from_old(name)) for name in filelist]


    file_mission_instrument_type=  [name.split('.')[0] for name in file_basename]
    file_mmdd= [name.split('.')[1][4:8] for name in file_basename]
    file_mon=  [name.split('.')[1][4:6] for name in file_basename]
    file_day=  [name.split('.')[1][6:8] for name in file_basename]
    file_jday= []
    for i in range(len(file_basename)):
        file_jday.append(datetime.datetime.strptime(str(year) + '-' + file_mon[i] +'-'+file_day[i], '%Y-%m-%d').timetuple().tm_yday)


    if time_period == 'MON':
        mon_num= np.arange(12) + 1
        mon_start_day= start_day=np.ones(12)
        if leap_year_check(year) == 'not_leap_year':
            mon_end_day=   np.array([31,28,31,30,31,30,31,31,30,31,30,31])
        if leap_year_check(year) == 'leap_year':
            mon_end_day=   np.array([31,29,31,30,31,30,31,31,30,31,30,31])
        ngroups=len(mon_num)

    if time_period == 'WKY':
        start_jday = np.arange(1,365,8)
        end_jday = np.asarray([i+7 for i in start_jday])
        if leap_year_check(year) == 'not_leap_year': end_jday[len(start_jday)-1]=365
        if leap_year_check(year) == 'leap_year': end_jday[len(start_jday)-1]=366
        ngroups=len(start_jday)

    if time_period == 'DLY':
        unique_mmdd= np.unique(file_mmdd)
        ngroups=len(unique_mmdd)

    grouping_list = [([],[]) for i in range(0,ngroups)] #initialize list of tuples


    for i in range(0,ngroups):
        # For each tuple of the grouping list, add  vector of the
        # start day and end day.. ([start, end])...
        # ---
        if time_period == 'MON':
            grouping_list[i][0].append(file_mission_instrument_type[0] + '.' + str(year) + '%02d' % mon_num[i] + '%02d' % mon_start_day[i])
            grouping_list[i][0].append(str(year) + '%02d' % mon_num[i] + '%02d' % mon_end_day[i])

        if time_period == 'WKY':
            start_YYYYMMDD= datetime.datetime.strptime(str(year) + '%03d' % start_jday[i], '%Y%j').date().strftime('%Y%m%d')
            end_YYYYMMDD=   datetime.datetime.strptime(str(year) + '%03d' % end_jday[i], '%Y%j').date().strftime('%Y%m%d')
            grouping_list[i][0].append(file_mission_instrument_type[0] + '.' + start_YYYYMMDD)
            grouping_list[i][0].append(end_YYYYMMDD)

        if time_period == 'DLY':
            grouping_list[i][0].append(file_mission_instrument_type[0] + '.' + str(year)+unique_mmdd[i])
            grouping_list[i][0].append(str(year)+unique_mmdd[i])


    # For each tuple of the grouping list, assign l2 files names for the
    # corresponding time period.
    # ---
    for i in range(0,len(filelist)):

        if time_period == 'MON':
            for j in range(0,ngroups):
                if int(file_mon[i]) == mon_num[j] and int(file_day[i]) >= mon_start_day[j] and int(file_day[i]) <= mon_end_day[j]:
                    grouping_list[j][1].append(filelist[i])


        if time_period == 'WKY':
            for j in range(0,ngroups):
                if int(file_jday[i]) >= start_jday[j] and int(file_jday[i]) <= end_jday[j]:
                    grouping_list[j][1].append(filelist[i])


        if time_period == 'DLY':
            for j in range(0,ngroups):
                if file_mmdd[i] == unique_mmdd[j]:
                    grouping_list[j][1].append(filelist[i])



    def f(x): return len(x[1])!=0
    grouping_list = list(filter(f, grouping_list)) #cut empty groups

    return grouping_list






def bulk_extract_meris(l1a_dir, extract_dir, extract_latlon, remove_original=False):
#-----------------------------------------------------------------------

    if not os.path.exists(extract_dir): os.makedirs(extract_dir)

    latlon = extract_latlon.split(',')
    south=   latlon[0]
    west=    latlon[1]
    north=   latlon[2]
    east=    latlon[3]


    for fi in glob.glob(l1a_dir + '/' + '*FRS*N1*'): decompress_file(fi)


    fname_l1a = glob.glob(l1a_dir + '/*FRS*N1*')            #re-query now without .gz in fname
    root_names = [os.path.basename(i) for i in fname_l1a]   #list of file names split from path


    for i in range(len(root_names)):

        root_pieces= root_names[i].split('_')

        resoluton= root_pieces[1]
        yyyy=        root_pieces[2][6:10]
        mm=          root_pieces[2][10:12]
        dd=          root_pieces[2][12:14]
        hhmmss=      root_pieces[3]


        result= time.strptime(dd+' '+ mm+' '+yyyy, '%d %m %Y')
        jday= result[7]   # the function time.structure returns a full time structure (tuple)
                          # of which the 7th elsement is the julian day === year_day


        if jday <= 9: s_jday=  '00' + str(jday)
        if jday >= 10 and jday <= 99: s_jday=  '0' + str(jday)
        if jday >= 100: s_jday=  str(jday)

        ofname= extract_dir + '/' + 'M' + yyyy + s_jday + hhmmss + '.L1B_' + resoluton

        #find start and stop scan lines to coorsponding to prescribed lat/lon bounds
        #then extract the full meris N1 scene to the smaller extarced scene.
        #note new extraced file has the classic obpg name convention
        #---



        p= subprocess.Popen('lonlat2pixline -v ' + fname_l1a[i] + ' ' + west  + ' ' + south  + ' ' + east + ' ' + north, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout,stderr = p.communicate()
        stdout=stdout.decode('ascii')

        print(stdout)

        for line in stdout.split('\n'):
            if 'sline' in line:
                junk = line.split('=')
                sline= junk[1]
            if 'eline' in line:
                junk = line.split('=')
                eline= junk[1]

            if 'spixl' in line:
                junk = line.split('=')
                spixl= junk[1]
            if 'epixl' in line:
                junk = line.split('=')
                epixl= junk[1]



        print('sline= ',  sline)
        print('eline= ',  eline)
        print('spixl= ',  spixl)
        print('epixl= ',  epixl)

        print('\nextracting meris file ---> ',  fname_l1a[i])
        print('new extraced file to be generated:-----> ', ofname)
        print('\n')

        subprocess.Popen( 'l1bextract_meris ' + fname_l1a[i] +' '+ spixl +' '+ epixl +' '+ sline +' '+ eline +' '+ ofname,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)



def extract_viirs(fname_l1a, fname_geo, extract_latlon):
#-----------------------------------------------------------------------

    root_name =  os.path.basename(fname_l1a)[0:14]

    print('\nroot_name= ', root_name, '\n')

    ofname=      root_name + '.L1A_SNPP.nc'    # NOTE: without a PATH this file will be created in the directory where python is launched - typically ~/python_programs
    ofname_geo=  root_name + '.GEO'            # The intent is to later remove the temporary extracted files...


    latlon = extract_latlon.split(',')
    south=   latlon[0]
    west=    latlon[1]
    north=   latlon[2]
    east=    latlon[3]


    #find start and stop scan lines to coorsponding to prescribed lat/lon bounds
    #then extract VIIRS scene to the smaller extracted scene...
    # ---
    #p=subprocess.Popen(['lonlat2pixline', '-v', fname_l1a, fname_geo, west, south, east, north], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #p.wait()
    #stdout,stderr = p.communicate()

    p=subprocess.Popen(['lonlat2pixline', fname_l1a, fname_geo, west, south, east, north], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout,stderr = p.communicate()
    stdout=stdout.decode('ascii')


    for line in stdout.split('\n'):

        if 'spixl' in line:
            junk = line.split('=')
            spixl= junk[1]
        if 'epixl' in line:
            junk = line.split('=')
            epixl= junk[1]

        if 'sline' in line:
            junk = line.split('=')
            sline= junk[1]
        if 'eline' in line:
            junk = line.split('=')
            eline= junk[1]


    print('\n extracting viirs file ---> ',  fname_l1a)
    print(' new extraced file to be generated:-----> ', ofname)
    print('\n')

    proc = subprocess.call(['l1aextract_viirs' , fname_l1a, spixl, epixl ,sline , eline , ofname])


    print('\n generating a geofile from the extracted viirs file')
    print(' new extraced geofile to be generated:-----> ', ofname_geo)
    print('\n')

    subprocess.call(['geolocate_viirs',
                      'verbose=True',
                      'ifile='        + ofname,
                      'geofile_mod='  + ofname_geo,
                      'terrain_path=' + os.environ['OCDATAROOT']+'/viirs/dem'])


    print('\nReturning the follwing extracted file names to the the main program batch_L12.py ...')
    print(ofname, ofname_geo)
    print(' ')


    return  ofname, ofname_geo




def bulk_extract_viirs(l1a_dir, extract_dir, extract_latlon, remove_original=False):
#-----------------------------------------------------------------------



    if not os.path.exists(extract_dir): os.makedirs(extract_dir)

    latlon = extract_latlon.split(',')
    south=   latlon[0]
    west=    latlon[1]
    north=   latlon[2]
    east=    latlon[3]

    for fi in glob.glob(l1a_dir + '/' + 'V*L1A*'): decompress_file(fi)    # umcompress all files...

    fname_l1a = glob.glob(l1a_dir + '/V*L1A*')              #re-query list that it now without .gz in fname


    for i in range(len(fname_l1a)):

        root_name = os.path.basename(fname_l1a[i])   # split basename from path
        fname_geo_basename=  root_name[0:14] + '.GEO-M_SNPP.nc'

        # Check to see if GEO file exists in the l1a_dir...
        if os.path.isfile(l1a_dir + '/' + fname_geo_basename):
            fname_geo = l1a_dir + '/' + fname_geo_basename
            print('\n\nUsing VIIRS GEO File found in the l1a_dir Directory... ', fname_geo)
            cmd= 'cp ' + fname_geo + ' ' + extract_dir
            subprocess.Popen(cmd, shell=True)
        else:
            # Get the GEO file from the OBPG Website and place it in the L1A dir..
            fname_geo_basename=  root_name[0:14] + '.GEO-M_SNPP.nc'
            url_file= 'http://oceandata.sci.gsfc.nasa.gov/cgi/getfile/' + fname_geo_basename
            cmd= 'wget ' + url_file
            process = subprocess.Popen(cmd, shell=True)
            process.wait()
            cmd1= 'cp ' + fname_geo_basename + ' ' + extract_dir
            subprocess.Popen(cmd1, shell=True)
            cmd2= 'mv ' + fname_geo_basename + ' ' + l1a_dir
            subprocess.Popen(cmd2, shell=True)
            fname_geo =   l1a_dir + '/' +  fname_geo_basename


        print('\nUsing the following full L1A VIIRS and Full GEO files. Output will')
        print('be an extracted L1A VIIRS and an extracted GEO file...\n')
        print(fname_l1a[i],fname_geo)
        print('\n')


        #find start and stop scan lines to coorsponding to prescribed lat/lon bounds
        #then extract VIIRS scene to the smaller extracted scene...
        # ---
        p= subprocess.Popen('lonlat2pixline -v ' + fname_l1a[i] + ' ' + fname_geo + ' ' + west  + ' ' + south  + ' ' + east + ' ' + north, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout,stderr = p.communicate()
        stdout=stdout.decode('ascii')

        for line in stdout.split('\n'):

            if 'spixl' in line:
                junk = line.split('=')
                spixl= junk[1]
            if 'epixl' in line:
                junk = line.split('=')
                epixl= junk[1]

            if 'sline' in line:
                junk = line.split('=')
                sline= junk[1]
            if 'eline' in line:
                junk = line.split('=')
                eline= junk[1]


        ofname=      extract_dir + '/' +   root_name
        ofname_geo=  extract_dir + '/' +   fname_geo_basename

        print('\nextracting viirs file ---> ',  fname_l1a[i])
        print('new extraced file to be generated:-----> ', ofname)
        print('\n')

        subprocess.Popen('l1aextract_viirs ' + fname_l1a[i] +' '+ spixl +' '+ epixl +' '+ sline +' '+ eline +' '+ ofname,     shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        print('\ngenerating new geofile from the extracted viirs file ---> ',  ofname)
        print('new extraced geofile to be generated:-----> ', ofname_geo)
        print('\n')

        subprocess.Popen('geolocate_viirs ' + 'ifile= ' + ofname + ' ' + 'geofile_mod= ' +  ofname_geo,     shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)




def wget_oceans_gsfc(fname):
#-----------------------------------------------------------------------

    # USAGE:  Type in a Unix Terminal Window:  wget_oceans_gsfc('my_list_of_files_to_get.txt')

    # where my_list_of_files_to_get.txt  is a standard text file containing the list of all
    # files (including "http://...") that you want to retreive.  To get the list of files
    # see below.

    #when at your home institution, first check the wget is installed on your computer by typing
    #the following at the unix prompt: which  wget
    #if wget is not installed then go on the web a search for wget for your type of machine (mac vs linux)
    #Install wget in /usr/local/bin and double check that /usr/local/bin in the the PATH by typing
    #echo $PATH

    #Go to the oceancolor website's file serach page and specify the files you want:
        #>>>----->  http://oceandata.sci.gsfc.nasa.gov/cgi/file_search.cgi

        #specify the search criteria for the files you want (no leading blank space before or
        #after specificed search term).

        # NOTE: >>------> select all three options at the bottom of the page (i.e., check Downlaod result and Add URL)

    #save the file list as a text file (or copy and past from web page list into a new text doc) to a new
    #directtory where you want to save the downloaded files. Then cd to that directory and:
        # 1. launch python
        # 2. type:  from my_general_utilities import wget_oceans_gsfc
        # 3. Type:  wget_oceans_gsfc('your_fname.txt')


    f = open(fname)
    all_lines = f.readlines()
    f.close()

    call(['wget', '--version'])

    for url_name in all_lines:
        if url_name[0:5] == 'http:':
            print('\n---------- getting http://... files ---------')
            call(['wget', url_name.strip('\n')])
        if url_name[0:5] == 'https':
            print('\n---------- getting https://... files ---------')
            call(['wget',
                  'load-cookies=' + '~/.urs_cookies',
                  'save-cookies=' + '~/.urs_cookies',
                  '--auth-no-challenge=on',
                  '--keep-session-cookies',
                  '--no-check-certificate',
                  url_name.strip('\n')])





def wget_level1_2_manifest_files(fname):
#-----------------------------------------------------------------------

    # USAGE:  Type in a Unix Terminal Window:  wget_oceans_gsfc('my_list_of_files_to_get.txt')

    # where my_list_of_files_to_get.txt  is a standard text file containing the list of all
    # files (including "http://...") that you want to retreive.  To get the list of files
    # see below.

    #when at your home institution, first check the wget is installed on your computer by typing
    #the following at the unix prompt: which  wget
    #if wget is not installed then go on the web a search for wget for your type of machine (mac vs linux)
    #Install wget in /usr/local/bin and double check that /usr/local/bin in the the PATH by typing
    #echo $PATH

    #Go to the oceancolor website's file serach page and specify the files you want:
        #>>>----->  http://oceandata.sci.gsfc.nasa.gov/cgi/file_search.cgi

        #specify the search criteria for the files you want (no leading blank space before or
        #after specificed search term).

        # NOTE: >>------> select all three options at the bottom of the page (i.e., check Downlaod result and Add URL)

    #save the file list as a text file (or copy and past from web page list into a new text doc) to a new
    #directtory where you want to save the downloaded files. Then cd to that directory and:
        # 1. launch python
        # 2. type:  from my_general_utilities import wget_oceans_gsfc
        # 3. Type:  wget_oceans_gsfc('your_fname.txt')


    f = open(fname)
    all_lines = f.readlines()
    f.close()


    for url_name in all_lines:
        if url_name[0:5] == 'http:':
            print('\n\n---------- getting file: ', url_name, '\n\n')
            call(['wget', url_name.strip('\n')])
        if url_name[0:5] == 'https':
            print('\n\n---------- getting file: ', '"' + url_name.strip('\n') + '"', '\n\n')
            call('wget --content-disposition --auth-no-challenge=on load-cookies=~/.urs_cookies save-cookies=~/.urs_cookies --keep-session-cookies --no-check-certificate' + '"' + url_name.strip('\n') + '"', shell=True)




def wget_aviso(username, password, filelist):
#-----------------------------------------------------------------------

    # NOTE:---> When you get your own user account, replace below
    #           cornell3:prt45cv12 with your own username:password


    # NOTE---> cd to the directory where the text containing the list of
    #          files (which should also be the directory where you want the
    #          new files to downlaod).
    #          # 1. type: python
    #          # 2. type: from my_general_utilities import wget_aviso
               # 3. Type:  wget_aviso('username', 'password','your_fname.txt')


    f = open(filelist)
    all_lines = f.readlines()
    f.close()


    url_path=  'ftp://' + username + ':' + password + '@ftp.aviso.altimetry.fr/global/delayed-time/grids/madt/all-sat-merged'

    uv_chk = np.asarray(['_uv_' in name for name in all_lines])
    if uv_chk.all() == True: url_path=  url_path + '/uv'

    h_chk=   np.asarray(['_h_'  in name for name in all_lines])
    if h_chk.all() == True: url_path =  url_path + '/h'

    if uv_chk.all() == True or h_chk.all() == True:

        for aviso_fname in all_lines:

            aviso_fname= aviso_fname.strip('\n')

            if aviso_fname[0:4] == 'File':                #some recs have the form:   "File:dt_global_allsat_madt_uv_20120107_20140106.nc.gz  2483 KB  3/3/14  3:31:00 AM"
                split_result= aviso_fname.split(':')      #this piece of code remotes the: "File:"
                aviso_fname=  split_result[1]


            split_result = aviso_fname.split(' ')         #some recs have the form:   "dt_global_allsat_madt_uv_20120107_20140106.nc.gz  2483 KB  3/3/14  3:31:00 AM"
            aviso_fname= split_result[0]                  #this piece of code removes text trailing info to leave only "dt_global_allsat_madt_uv_20120107_20140106.nc.gz"

            split_result= aviso_fname.split('_')

            yyyymmdd= split_result[5]
            s_year= yyyymmdd[0:4]
            url_path_year= url_path + '/' + s_year

            call(['wget', url_path_year + '/' +  aviso_fname])







def wget_ghrsst_sst(year, start_day, end_day):
#-----------------------------------------------------------------------

    import re
    import requests

    year= str(year)

    jday_vec=      start_day + np.arange(end_day-start_day+1)
    sjday_vec=     str(jday_vec)

    sjday_vec = list(map(str, jday_vec))

    for i in range(len(sjday_vec)):
        if len(sjday_vec[i]) == 1: sjday_vec[i] = '00' + sjday_vec[i]
        if len(sjday_vec[i]) == 2: sjday_vec[i] =  '0' +  sjday_vec[i]


    for i in range(len(sjday_vec)):

        pf_dir='https://www.ncei.noaa.gov/data/oceans/ghrsst/L4/GLOB/JPL/MUR/'+ year + '/' + sjday_vec[i] + '/'

        result= requests.get(pf_dir).text
        clean= re.compile('<.*?>')
        clean_result= re.sub(clean,'', result).split(';')  # still has a bunch of trailing grabage after .nc

        print(clean_result,'\n\n')

        for name in clean_result:
            match= re.search('.nc', name)
            if match != None:
                name_only= name[0:match.start()+3].strip('\n')
                call(['wget',
                  'load-cookies=' + '~/.urs_cookies',
                  'save-cookies=' + '~/.urs_cookies',
                  '--auth-no-challenge=on',
                  '--keep-session-cookies',
                  '--no-check-certificate',
                  pf_dir + name_only])










def wget_avhrr_pathfinder_sst(year, month_num):

    import re
    import requests

    file_date= year + month_num

    pf_dir='https://www.ncei.noaa.gov/data/oceans/pathfinder/Version5.3/L3C/' + year + '/data/'
    result= requests.get(pf_dir).text
    clean= re.compile('<.*?>')
    clean_result= re.sub(clean,'', result).split(';')  # still has a bunch of trailing grabage after .nc

    for name in clean_result:
        match= re.search('.nc', name)
        if match != None:
            name_only= name[0:match.start()+3].strip('\n')
            if file_date in name_only and 'night' in name_only:
                print(pf_dir + name_only)
                call(['wget',
                  'load-cookies=' + '~/.urs_cookies',
                  'save-cookies=' + '~/.urs_cookies',
                  '--auth-no-challenge=on',
                  '--keep-session-cookies',
                  '--no-check-certificate',
                  pf_dir + name_only])







def wget_ssmi(year, satellite):

    # Note:  For this little function to work, you need to have the .netrc file in your home directory
    #        with  machine ftp.ssmi.com and also username and password
    # current version as of March 2023 == v07.0.1   See https://data.remss.com/windsat/bmaps_v07.0.1/y2008/m01/

    version= '8'

    month_list= np.array(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])

    day_list=   np.array(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', \
                          '13', '14', '15','16', '17', '18','19', '20', '21','22', '23', '24', \
                          '25', '26','27', '28', '29','30', '31'])

    #month_list= np.array(['01'])         # <----<<<<<   if you want to restrict the range of month...
    #day_list=   np.array(['01', '02'])   # <----<<<<<   if you want to restrict the range of the day of the month.


    for month in month_list:

        url_path=  'https://data.remss.com/ssmi' + '/' + satellite + '/' + 'bmaps_' + 'v0' + version +  '/y' + year + '/m' + month

        for day in day_list:
            fname= satellite + '_' + year + month + day + 'v' + version + '.gz'   # I am cheating a bit here by hardcoding in v7...
            print(url_path + '/' + fname)
            call(['wget', url_path + '/' + fname])







def wget_windsat(year):

    # Note:  For this little function to work, you need to have the .netrc file in your home directory
    #        with  machine ftp.ssmi.com and also username and password
    # current version as of March 2023 == v07.0.1   See https://data.remss.com/windsat/bmaps_v07.0.1/y2008/m01/

    version= '7.0.1'


    month_list= np.array(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])

    day_list=   np.array(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', \
                          '13', '14', '15','16', '17', '18','19', '20', '21','22', '23', '24', \
                          '25', '26','27', '28', '29','30', '31'])


    #month_list= np.array(['01'])         #<----<<<<<   if you want to restrict the range of month...
    #day_list=   np.array(['01', '02'])   #<----<<<<<   if you want to restrict the range of the day of the month.

    for month in month_list:

        url_path=  'https://data.remss.com/windsat' + '/' + 'bmaps_' + 'v0' + version +  '/y' + year + '/m' + month

        for day in day_list:
            fname= 'wsat_' + year + month + day + 'v' + version + '.gz'   # I am cheating a bit here by hardcoding in v7...
            print(url_path + '/' + fname)
            call(['wget', url_path + '/' + fname])



def wget_quiksat(year):

    # Note:  For this little function to work, you need to have the .netrc file in your home directory
    #        with  machine ftp.ssmi.com and also username and password
    # current version as of March 2023 == v07.0.1   See https://data.remss.com/windsat/bmaps_v07.0.1/y2008/m01/

    version= '4'


    month_list= np.array(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])

    day_list=   np.array(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', \
                          '13', '14', '15','16', '17', '18','19', '20', '21','22', '23', '24', \
                          '25', '26','27', '28', '29','30', '31'])


    #month_list= np.array(['01'])         #<----<<<<<   if you want to restrict the range of month...
    #day_list=   np.array(['01', '02'])   #<----<<<<<   if you want to restrict the range of the day of the month.

    for month in month_list:

        url_path=  'https://data.remss.com/qscat' + '/' + 'bmaps_' + 'v0' + version +  '/y' + year + '/m' + month

        for day in day_list:
            fname= 'qscat_' + year + month + day + 'v' + version + '.gz'   # I am cheating a bit here by hardcoding in v7...
            print(url_path + '/' + fname)
            call(['wget', url_path + '/' + fname])




def wget_ascat(year, satellite):

    # Note:  For this little function to work, you need to have the .netrc file in your home directory
    #        with  machine ftp.ssmi.com and also username and password
    # current version as of March 2023 == v07.0.1   See https://data.remss.com/windsat/bmaps_v07.0.1/y2008/m01/

    if satellite == 'metopa':
        version= '2.1.1'
        file_prefix= 'ascata'
    if satellite == 'metopb':
        version= '2.1'
        file_prefix= 'ascatb'
    if satellite == 'metopc':
        version= '2.1'
        file_prefix= 'ascatc'

    month_list= np.array(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])

    day_list=   np.array(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', \
                          '13', '14', '15','16', '17', '18','19', '20', '21','22', '23', '24', \
                          '25', '26','27', '28', '29','30', '31'])

    #month_list= np.array(['01'])         # <----<<<<<   if you want to restrict the range of month...
    #day_list=   np.array(['01', '02'])   # <----<<<<<   if you want to restrict the range of the day of the month.


    for month in month_list:

        url_path=  'https://data.remss.com/ascat' + '/' + satellite + '/' + 'bmaps_' + 'v0' + version +  '/y' + year + '/m' + month

        for day in day_list:
            fname= file_prefix + '_' + year + month + day + '_v0' + version + '.gz'   # I am cheating a bit here by hardcoding in v7...
            print(url_path + '/' + fname)
            call(['wget', url_path + '/' + fname])




def wget_neci_oisst(year):

    url= 'https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr'
    month= np.array(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])

    for i in range(len(month)):
        url_path=  url + '/' + year + month[i] +'/'
        print(url_path)
        call(['wget', '-r', '-l1', '--no-parent', '-q', '-nd', '-A.nc', '--load-cookies', '~/.urs_cookies', '--save-cookies', '~/.urs_cookies', '--auth-no-challenge=on', '--keep-session-cookies', '--content-disposition', url_path])



def rebin_down_nan(orig_img, new_ydim, new_xdim):
#-----------------------------------------------------------------------

    #THIS FUNCTION ACTS JUST LIKE IDL'S REBIN FUNCTION WHEN REDUCING AN ARRAY BUT WITH THE
    #IMPORTANT EXCEPTION OF ALLOWING NAN IN THE ORIGINAL ARRAY TO BE TREATED AS MISSING
    #VALUES WHEN AVERAGING OVER PIXEL BLOCKS IN THE ORGINAL ARRAY

    #WRITTEN BY BRUCE MONGER, CORNELL UNIVERSITY, FEBRUARY 14, 2015

    orig_ydim, orig_xdim = orig_img.shape


    if (np.mod(orig_xdim, new_xdim) != 0) or (np.mod(orig_ydim, new_ydim) != 0):
        print('dimensions of new array must be integer value of orginal array dimmension')
        return ['']


    new_img=   np.zeros((new_ydim,new_xdim), dtype=float)
    xbox=      int(orig_xdim/new_xdim)
    ybox=      int(orig_ydim/new_ydim)


    start_xi=  np.arange(new_xdim)*xbox
    end_xi=    start_xi + (xbox-1)
    start_yi=  np.arange(new_ydim)*ybox
    end_yi=    start_yi + (ybox-1)


    for i in range(new_ydim):
        for j in range(new_xdim):
            box=   orig_img[start_yi[i]:end_yi[i],start_xi[j]:end_xi[j]]
            new_img[i,j]=  np.nanmean(box)

    return new_img



def get_ancillary_list_fname(l1a_fname):

    if len(os.path.basename(l1a_fname)) == 13:  # if basename YYYYDDDHHMMSS, call with -s
        p= subprocess.Popen('getanc -v --disable-download -s' + ' ' + os.path.basename(l1a_fname), shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        p= subprocess.Popen('getanc -v  --disable-download'  + ' ' + l1a_fname, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, err = p.communicate()
    output=output.decode('ascii')


    anc_fname= ''
    for line in output.splitlines():
        if 'Created' in line:
            anc_fname = line.split()[1].strip("''")

    return(anc_fname)


def wget_and_move(anc_list):

    # Examples: 'met1=/Applications/seadas-7.5.1/ocssw/var/anc/2017/218/N201721818_MET_NCEPR2_6h.hdf'
    #           'met1=/Applications/seadas-7.5.1/ocssw/var/anc/2015/218/N201521812_MET_NCEPR2_6h.hdf'
    #           'ozone1=/Applications/seadas-7.5.1/ocssw/var/anc/2015/218/N201521800_O3_AURAOMI_24h.hdf'

    anc_list= np.unique(anc_list)

    for name in anc_list:
        if ('sstfile' in name or 'icefile' in name or 'met1' in name or 'met2' in name or 'met3' in name or 'ozone1' in name or 'ozone2' in name or 'ozone3' in name or 'no2' in name or 'ATT' in name or  'EPH' in name):
            anc_full_local_fname= name.split('=')[1].strip('\n')
            anc_basename= os.path.basename(anc_full_local_fname)
            anc_local_path= os.path.dirname(anc_full_local_fname)
            anc_ocssw_url_fname= 'https://oceandata.sci.gsfc.nasa.gov/cgi/getfile' + '/' + anc_basename

            if not os.path.exists(anc_full_local_fname):
                call(['wget', '-q', '--load-cookies', '~/.urs_cookies', '--save-cookies', '~/.urs_cookies', '--auth-no-challenge=on', '--keep-session-cookies', '--content-disposition','--no-check-certificate', anc_ocssw_url_fname])
                if os.path.exists(os.getcwd() + '/' + anc_basename + '.bz2'):
                    call('bunzip2 ' + os.getcwd() + '/' + anc_basename + '.bz2', shell=True)
                if os.path.exists(os.getcwd() + '/' + anc_basename + '.gz'):
                    call('gunzip ' + os.getcwd() + '/' + anc_basename + '.gz', shell=True)
                call('mkdir -p ' + anc_local_path, shell=True)
                call('mv ' + os.getcwd() + '/' + anc_basename + ' ' + anc_full_local_fname, shell=True)

                p= subprocess.Popen(["file", anc_full_local_fname], stdout=subprocess.PIPE)
                output, err = p.communicate()
                output=output.decode('ascii')

                if 'bzip2' in output:
                    call('bunzip2 ' + anc_full_local_fname, shell=True)
                    if os.path.exists(anc_full_local_fname + '.out'):
                        call('mv ' + anc_full_local_fname + '.out' + ' ' + anc_full_local_fname, shell=True)
                    if 'gzip' in output:
                        call('gunzip ' + anc_full_local_fname, shell=True)


def my_getanc(l1a_file):
#-----------------------------------------------------------------------

# -d in call to getanc.py prevents download and leaves behind a text file with
# ancillary local filename and corect path to store the files on the local machine...
# ---

    if len(os.path.basename(l1a_file)) == 13:  # if basename YYYYDDDHHMMSS, call with -s  which means use as start time
        #call('getanc -v -d -s ' + l1a_file, shell=True)
        call('getanc -v  --disable-download -s ' + l1a_file, shell=True)
    #else: call('getanc -v -d ' + l1a_file, shell=True)  # else call with full fname
    else: call('getanc --disable-download ' + l1a_file, shell=True)  # else call with full fname

    ancillary_file= get_ancillary_list_fname(l1a_file)

    f = open(ancillary_file)
    all_lines = f.readlines()
    f.close()

    wget_and_move(all_lines)



def my_modis_atteph(l1a_file):

# -d in call to getanc prevents download and leaves behind a text file with
# ancillary local filename and corect path to store the files on the local machine...
# ---


    #call('modis_atteph -v -d ' +  l1a_file, shell=True)
    call('modis_atteph -v --disable-download ' +  l1a_file, shell=True)  #new line for seadas 8.  Jan 4 2022
    atteph_file=  os.path.basename(l1a_file) + '.atteph'

    f = open(atteph_file)
    all_lines = f.readlines()
    f.close()

    wget_and_move(all_lines)
