#! /usr/bin python
import glob
import numpy as np
from subprocess import *
import sys, os
import shutil
import datetime
from my_general_utilities import *

sys.dont_write_bytecode = True
sys.path.insert(0, 'utilities')

#import general_utilities

from my_hdf_cdf_utilities import *
import my_general_utilities as general_utilities



#-------------------------------
#   MODIS PROCESSING STEPS
#-------------------------------

def modis_level12(file_name, root_name, prod_list, prod_list_sst, color_l2_file_fname, sst_l2_file_fname, aerosol_corr_type, hires):

    # file_fname --  is a single l1a file (file_name) which may or may not be in the
    # old file naming convention.
    # root_name --  is the root_name of file_fname and it will always be in the
    # new file naming convention of MISSION_INSTRUMENT_TYPE.YYYYMMDDTHHMMSS
    #
    # -----------------------------------------------------------------------------------------
    # generate geolocation file (modis_GEO)
    # note: cycle up to 5 times because of bug in modis_GEO for Mac Mavericks OS
    # -----------------------------------------------------------------------------------------

    print('\n >=====>  generating geolocation file from modis L1A standard resolution bands...')

    #print('\n >-----> First checking for attitude and ephemeris files needed for modis geolocation...')
    #general_utilities.my_modis_atteph(file_name)

    print('\n -----> calling modis_GEO...\n')
    fname_geo = root_name + '.GEO'
    call('modis_GEO -v -o ' + fname_geo + ' ' + file_name, shell=True)
    if (not os.path.exists(fname_geo)):
       call('modis_GEO -v --refreshDB -o ' + fname_geo + ' ' + file_name, shell=True)
    if (not os.path.exists(fname_geo)):
        seadas_home= os.environ['OCSSWROOT']
        call('rm %s/run/var/log/ancillary_data.db' % seadas_home , shell=True)
        call('modis_GEO -v -o ' + fname_geo + ' ' + file_name, shell=True)


    # -----------------------------------------------------------------------------------------
    # generate L1B from L1A (modis_L1B)
    # note: cycle up to 5 times because of bug in modis_L1B for Mac Mavericks OS
    # -----------------------------------------------------------------------------------------

    print('\n >=====>  generating Level-1B file from Level-1A file and Geolocation File...')
    print('\n -----> hires status= ', hires, '\n\n')

    if hires == 'off':

        fname_l1b = root_name + '.L1B_LAC'
        cnt = 0
        while (not os.path.exists(fname_l1b)) and cnt <= 5:
            print('\n\n ----> starting modis_L1B for standard resolution...\n\n')
            call('modis_L1B -v --del-hkm --del-qkm -o ' + fname_l1b + ' ' + file_name + ' ' + fname_geo, shell=True)
            cnt+=1

    elif hires == 'on':

         fname_l1b =     root_name + '.L1B_LAC'
         fname_l1b_hkm = root_name + '.L1B_HKM'
         fname_l1b_qkm = root_name + '.L1B_QKM'
         cnt = 0
         while (not os.path.exists(fname_l1b)) and cnt <= 5:
             print('\n\n ----> starting modis_L1B for hires bands...\n\n')
             call('modis_L1B -v -o ' + fname_l1b + ' ' + file_name + ' ' + fname_geo + ' -k ' + fname_l1b_hkm + ' -q ' + fname_l1b_qkm, shell=True)
             cnt+=1

    #sys.exit('exit after L1B generation')

    # -----------------------------------------------------------------------------------------
    # call l2gen c-compiled function for modis
    # -----------------------------------------------------------------------------------------

    print('\n >=====>  checking for best ancillary data (Met and Ozone) locally and retrieving from web if needed...\n\n')

    call('getanc -v --refreshDB ' + file_name, shell=True)

    if general_utilities.fname_convention(file_name) == 'old':
        old_root_name= os.path.basename(file_name)[0:14]
        fname_ancil_list = old_root_name + '.L1A_LAC.x.hdf.anc'
    else: fname_ancil_list= root_name + '.anc'

    print('\n\nname of ancillary file determined from get_ancillary_list_fname ---> ',fname_ancil_list, '\n\n')


    if prod_list_sst == 'none':

         print('\n >=====> generating level-2 OC data without SST using l2gen...')

         call(['l2gen',
               'ifile='      + fname_l1b,
               'ofile1='     + color_l2_file_fname,
               'l2prod1='    + prod_list,
               'geofile='    + fname_geo,
               'oformat='    + 'netcdf4',
               'par=' + fname_ancil_list,
               'resolution=' + '1000',
               'proc_sst='   + '0',
               'aer_opt='    + aerosol_corr_type])


    if prod_list_sst != 'none':

        print('\n >=====> generating level-2 OC data with SST data using l2gen...')

        if 'qual_sst' not in prod_list_sst: prod_list_sst= prod_list_sst + ',qual_sst'


        call(['l2gen',
              'ifile='      + fname_l1b,
              'ofile1='     + color_l2_file_fname,
              'l2prod1='    + prod_list,
              'ofile2='     + sst_l2_file_fname,
              'l2prod2='    + prod_list_sst,
              'geofile='    + fname_geo,
              'oformat='    + 'netcdf4',
              'par=' + fname_ancil_list,
              'resolution=' + '1000',
              'proc_sst='   + '1',
              'aer_opt='    + aerosol_corr_type])


    # if high-resolution is specified
    if hires == 'on':

        print('\n >=====>  generating HIRES level-2 data from level-1 data using l2gen...\n')

        call(['l2gen',
             'ifile=' + fname_l1b,
             'ofile1=' + color_l2_file_fname + '_HKM',
             'l2prod1=' + 'chl_oc2',
             'geofile=' + fname_geo,
             'oformat='    + 'netcdf4',
             'par=' + fname_ancil_list,
             'resolution=' + '500',
             'aer_opt=' + aerosol_corr_type,
             'ctl_pt_incr=' + '1'])

        call(['l2gen',
             'ifile=' + fname_l1b,
             'ofile1=' + color_l2_file_fname + '_QKM',
             'l2prod1=' + 'Rrs_645,Rrs_859',
             'geofile=' + fname_geo,
             'oformat='    + 'netcdf4',
             'par=' + fname_ancil_list,
             'resolution=' + '250',
             'aer_opt=' + aerosol_corr_type,
             'ctl_pt_incr=' + '1'])



# -----------------------------------------------------------------------------------------
#   call l2gen for seawifs/meris/hico PROCESSING STEPS
# -----------------------------------------------------------------------------------------

def seawifs_hico_level12(file_name, root_name, prod_list, color_l2_file_fname):

    # file_fname --  is a single l1a file (file_name) which may or may not be in the
    # old file naming convention.
    # root_name --  is the root_name of file_fname and it will always be in the
    # new file naming convention of MISSION_INSTRUMENT_TYPE.YYYYMMDDTHHMMSS
    #

    # get ancillary data (getanc)
    print('\n >=====>  checking for best ancillary data (Met and Ozone) locally and retrieving from web if needed...')

    mission_instrument= root_name.split('.')[0]
    instrument= mission_instrument.split('_')[1]

    if general_utilities.fname_convention(file_name) == 'old':

        if instrument== 'HICO':
            os.system('getanc -v -s ' + os.path.basenme(file_name)[1:14])
            fname_ancil_list= general_utilities.get_ancillary_list_fname(os.path.basename(file_name)[1:14])
        if instrument != 'HICO':
            os.system('getanc -v ' + file_name)
            fname_ancil_list= general_utilities.get_ancillary_list_fname(file_name)

    if  general_utilities.fname_convention(file_name) == 'new':
        os.system('getanc -v ' + file_name)
        fname_ancil_list= general_utilities.get_ancillary_list_fname(file_name)

    print('\n >=====> generating level-2 OC data from level-1 data using l2gen...')

    call(['l2gen',
          'ifile='   + file_name,
          'ofile='   + color_l2_file_fname,
          'l2prod1=' + prod_list,
          'par=' + fname_ancil_list])


# -----------------------------------------------------------------------------------------
#   call l2gen for VIIRS PROCESSING STEPS
# -----------------------------------------------------------------------------------------


def viirs_level12(ifile, root_name, prod_list, color_l2_file_fname, prod_list_sst, sst_l2_file_fname,latlon):

    # ifile --  is a single l1a file (/path/file_name) which may or may not be in the
    # old file naming convention.
    # root_name --  is the root_name (no path) of file_fname and it will always be in the
    # new file naming convention of MISSION_INSTRUMENT_TYPE.YYYYMMDDTHHMMSS
    #


   # NOTE: finding ".x." in the name of the L1A file means that it was extracted when the
   # data order was made and does not require manual extraction prior to level-2 processing
   # ---
   # If you have extracted L1A viirs files, then you need to make geolocation file from
   # the extracted L1A file. To make geolocation file from  L1A file, you need a special
   # dem file(s) added to the the seadas directory.
   # ---
   # The dem dir is downloaded here: https://oceandata.sci.gsfc.nasa.gov/ocssw/dem.tar.gz
   # and it should be placed here after downloading: $OCSSWROOT/share/viirs
   # ---
    if ".x." in ifile and not os.path.exists(os.environ['OCDATAROOT']+'/viirs/dem'):

            print('')
            print('----------------------------------------------------------------------')
            print('You are trying to process an extracted VIIRS file and you do not')
            print('have the neeeded dem file used by geolocate_viirs function to generate')
            print('a geolocation file from an extracted viirs level-1a file.')
            print('')
            print('get the dem dir here: https://oceandata.sci.gsfc.nasa.gov/ocssw/dem.tar.gz')
            print('place the dem directory in: $OCSSWROOT/share/viirs')
            print('----------------------------------------------------------------------')
            print('')
            sys.exit()


    if ".x." in ifile and os.path.exists(os.environ['OCDATAROOT']+'/viirs/dem'):

        print('\nGenerating a geolocation file from an extracted viirs L1A file...\n')

        fname_type=  general_utilities.fname_convention(ifile)
        mission_instrument= root_name.split('.')[0]
        misson= mission_instrument.split('_')[0]

        if fname_type =='old':
            if misson == 'NOAA20': fname_geo= os.path.basename(ifile)[0:14] +  '.GEO-M_JPSS.nc'
            if misson == 'SNPP':   fname_geo= os.path.basename(ifile)[0:14] +  '.GEO-M_SNPP.nc'
        else: fname_geo=  root_name + '.GEO_M.nc'

        call(['geolocate_viirs',
              'ifile='       + ifile,
              'geofile_mod=' + fname_geo,
              'verbose='     + 'True'])

        manual_extraction_done=False

        # ---
        call(['calibrate_viirs',
              'ifile='       + ifile,
              'l1bfile_mod=' + 'l1b_file',
              'verbose='     + 'True'])



    '''
    if not ".x." in ifile:

        print '\nFull viirs L1A data granual found.  Will attempt to extract the file'
        print 'if the viirs dem file has been installed...\n'


        fname_geo_root=  root_name[0:14] + '.GEO-M.nc'

        # Check to see if the full granule GEO file exists in the l1a_dir...
        ifile_dir = os.path.dirname(ifile)
        if os.path.isfile(ifile_dir + '/' + fname_geo_root):
            fname_geo = ifile_dir + '/' + fname_geo_root
            print '\n\nUsing VIIRS GEO File from the L1A Directory... ', fname_geo
        else:
            # Get the full granule GEO file and place it in the l1a_dir
            url_file= 'https://oceandata.sci.gsfc.nasa.gov/cgi/getfile/' + fname_geo_root
            cmd= 'wget ' + url_file
            process = Popen(cmd, shell=True)
            process.wait()
            cmd= 'mv ' + fname_geo_root + ' ' + ifile_dir
            subprocess.Popen(cmd, shell=True)
            fname_geo =   ifile_dir + '/' +  fname_geo_root
            print 'Using VIIRS GEO File DownLoaded from the OPPG Website... ', fname_geo

        if not os.path.exists(os.environ['OCDATAROOT']+'/viirs/dem'):
            print '\n>=====>  The optional OBPG dem digital elevation map file NOT installed!'
            print 'No extraction of L1A VIIRS Will Be Done on L1A file before l2gen processing..'
            manual_extraction_done=False

        if os.path.exists(os.environ['OCDATAROOT']+'/viirs/dem'):
            print '\n>=====>  Optional OBPG dem file has been installed!'
            print 'Will now extract region of interest from L1A VIIRS Using Reduced DEM and'
            print 'generate the corresponding GEO file from the extracted L1A file for subsequent L12 processing...'
            print 'NOTE: This might take a minute of two of cpu time.  Hold tight...'

            extracted_l1a, extracted_geo= general_utilities.extract_viirs(ifile, fname_geo, latlon)

            call(['calibrate_viirs',
                  'ifile='       + extracted_l1a,
                  'l1bfile_mod=' + 'l1b_file',
                  'verbose='     + 'True'])

            fname_geo=  extracted_geo
            manual_extraction_done=True
            '''

    # get ancillary data...
    print('\n >=====>  checking for best ancillary data (Met and Ozone) locally and retrieving from web if needed...')

    call('getanc -v ' + ifile, shell=True)
    fname_ancil_list= general_utilities.get_ancillary_list_fname(ifile)

    if prod_list_sst == 'none' or 'JPSS1' in ifile or 'NOAA20' in ifile:

         print('\n >=====> generating level-2 OC data (without SST) using l2gen...')

         call(['l2gen',
               'ifile='      + 'l1b_file',
               'ofile1='     + color_l2_file_fname,
               'l2prod1='    + prod_list,
               'geofile='    + fname_geo,
               'oformat='    + 'netcdf4',
               'par='        + fname_ancil_list,
               'proc_sst='   + '0'])


    if prod_list_sst != 'none':

        print('\n >=====> generating level-2 OC and SST data using l2gen...')

        if 'qual_sst' not in prod_list_sst: prod_list_sst= prod_list_sst + ',qual_sst'


        call(['l2gen',
              'ifile='      + 'l1b_file',
              'ofile1='     + color_l2_file_fname,
              'l2prod1='    + prod_list,
              'ofile2='     + sst_l2_file_fname,
              'l2prod2='    + prod_list_sst,
              'geofile='    + fname_geo,
              'oformat='    + 'netcdf4',
              'par='        + fname_ancil_list,
              'proc_sst='   + '1'])


    if manual_extraction_done == True:
        os.remove(extracted_l1a)



    os.remove(fname_geo)
    os.remove('l1b_file')

# -----------------------------------------------------------------------------------------
#   call l2gen for Landsat 8 Collection 1  OLI PROCESSING STEPS
# -----------------------------------------------------------------------------------------

def oli_level12(file_name, prod_list, color_l2_file_fname,latlon):


    # Each oli scene (file_name) comes as a direcotry of several files with the first
    # band and the geo file being needed for input to l2gen.  The other companion bands
    # in the directory are found by l2gen automatically...
    # Note:  initial glob.glob for main dir creates a list of file_fname
    # that actually contains a list of directories where was directory is a set of files
    # that collectively represent a single landsat oli scene
    # ---
    first_band_root = file_name.split('/')[-1] # last directory in absolute path

    first_band=glob.glob(file_name + '/' + '*_MTL.txt')[0] # input file for l2gen acting on landsat...

    #ancillary list
    os.system('getanc -v ' + first_band)
    general_utilities.my_getanc(first_band)
    fname_ancil_list = first_band.split('/')[-1] + '.anc'

    print('\n >=====> generating level-2 OC data from level-1 oli data using l2gen...')

    call(['l2gen',
          'ifile='   + first_band,
          'ofile1='  + color_l2_file_fname,
          'l2prod1=' + prod_list,
          'par=' + fname_ancil_list,
          'resolution=' + '30'])




# -----------------------------------------------------------------------------------------
#   call l2gen for OLCI on Sentenal-3 PROCESSING STEPS
# -----------------------------------------------------------------------------------------

def olci_level12(dir_name, root_name, prod_list, color_l2_file_fname,latlon):

    # Each olci scene (file_name) comes as a direcotry of several files with the first
    # band and the geo file being needed for input to l2gen.  The other companion bands
    # in the directory are found by l2gen automatically...
    # Note:  initial glob.glob for main dir creates a list of file_fname
    # that actually contains a list of directories where was directory is a set of files
    # that collectively represent a single oli scene

    # ---
    single_scene_dirname =  dir_name.split('/')[-1]  # last directory in full path (basically the name of the olci directory downloaded and untared.

    if not '_x' in single_scene_dirname:

        latlon = latlon.split(',')
        south=   latlon[0]
        west=    latlon[1]
        north=   latlon[2]
        east=    latlon[3]

        olci_extraction_needed= 'yes'
        #l1bextract_safe_nc replaces olci_L1B_extract for seadas 8
        #call('olci_L1B_extract.py -v' + ' --south=' + south + ' --west=' + west + ' --north=' + north + ' --east=' + east + ' ' + dir_name,  shell=True)
        call('l1bextract_safe_nc -v' + ' --south=' + south + ' --west=' + west + ' --north=' + north + ' --east=' + east + ' ' + dir_name,  shell=True)
        if os.path.exists(dir_name + '.subset'):
            shutil.rmtree(dir_name)
            dir_name= dir_name + '_x'


    first_band=  glob.glob(dir_name + '/' + 'Oa01_radiance.nc')[0] # name of first radiance band in olci directory for given scene

    print('root_name ===> ', root_name)
    print(root_name[1:14] + '.anc')

    # get ancillary data
    print('\n >=====>  checking for best ancillary data (Met and Ozone) locally and retrieving from web if needed...')


    olci_YYYYDDDHHMMSS= general_utilities.YYYYDDDHHMMSS_from_new_fname(root_name)
    os.system('getanc -v -s ' + olci_YYYYDDDHHMMSS)
    #fname_ancil_list = olci_YYYYDDDHHMMSS + '.anc'
    #general_utilities.my_getanc(olci_YYYYDDDHHMMSS)
    fname_ancil_list= general_utilities.get_ancillary_list_fname(olci_YYYYDDDHHMMSS)


    print('\n--------------------------------------')
    print('ifile='   + first_band)
    print('ofile1='  + color_l2_file_fname)
    print('l2prod1=' + prod_list)
    print('par='     + fname_ancil_list)
    print('--------------------------------------\n')

    print('\n >=====> generating level-2 OC data from level-1 olci data using l2gen...')

    os.chdir(dir_name)
    call(['l2gen',
          'ifile='   + 'xfdumanifest.xml',
          'ofile1='  +  color_l2_file_fname,
          'l2prod1=' +  prod_list,
          'par='     +  os.environ['MYPYTHONPROGRAMS'] + '/' + fname_ancil_list])
    os.chdir(os.environ['MYPYTHONPROGRAMS'])



# -----------------------------------------------------------------------------------------
#   call l2gen for MSI on Sentenal-2 PROCESSING STEPS
# -----------------------------------------------------------------------------------------

def msi_level12(dir_name, root_name, prod_list, color_l2_file_fname):

    # Each olci scene (file_name) comes as a direcotry of several files with the first
    # band and the geo file being needed for input to l2gen.  The other companion bands
    # in the directory are found by l2gen automatically...
    # Note:  initial glob.glob for main dir creates a list of file_fname
    # that actually contains a list of directories where was directory is a set of files
    # that collectively represent a single oli scene

    # ---
    single_scene_dirname =  dir_name.split('/')[-1]  # last directory in full path (basically the name of the olci directory downloaded an untared.
    manifest_fname=         glob.glob(dir_name + '/' + 'manifest.safe')[0] # name of fist radiance band in olci directory for given scene


    # get ancillary data
    print('\n >=====>  checking for best ancillary data (Met and Ozone) locally and retrieving from web if needed...')

    msi_YYYYDDDHHMMSS= general_utilities.YYYYDDDHHMMSS_from_new_fname(root_name)
    #os.system('getanc -v -s ' + msi_YYYYDDDHHMMSS)
    #fname_ancil_list =msi_YYYYDDDHHMMSS + '.anc'
    os.system('getanc -v -s ' + msi_YYYYDDDHHMMSS)
    fname_ancil_list= general_utilities.get_ancillary_list_fname(msi_YYYYDDDHHMMSS)



    print('\n--------------------------------------')
    print('ifile='   + manifest_fname)
    print('ofile1='  + color_l2_file_fname)
    print('l2prod1=' + prod_list)
    print('par='     + fname_ancil_list)
    print('--------------------------------------\n')

    print('\n >=====> generating level-2 OC data from level-1 oli data using l2gen...')

    os.chdir(dir_name)
    call(['l2gen',
          'ifile='   +  'manifest.safe',
          'ofile1='  +  color_l2_file_fname,
          'l2prod1=' +  prod_list,
          'par='     +  os.environ['MYPYTHONPROGRAMS'] + '/' + fname_ancil_list])
    os.chdir(os.environ['MYPYTHONPROGRAMS'])



# -----------------------------------------------------------------------------------------
#   call l2gen for OLCI on Sentenal-3 PROCESSING STEPS
# -----------------------------------------------------------------------------------------

def meris_level12(dir_name, root_name, prod_list, color_l2_file_fname):

    # Each meris scene (file_name) comes as a direcotry of several files with the first
    # band and the geo file being needed for input to l2gen.  The other companion bands
    # in the directory are found by l2gen automatically...
    # Note:  initial glob.glob for main dir creates a list of file_fname
    # that actually contains a list of directories where was directory is a set of files
    # that collectively represent a single oli scene

    # ---
    single_scene_dirname =  dir_name.split('/')[-1]  # last directory in full path (basically the name of the olci directory downloaded and untared.

    first_band=  glob.glob(dir_name + '/' + 'M01_radiance.nc')[0] # name of first radiance band in meris directory for given scene

    print('root_name ===> ', root_name)
    print(root_name[1:14] + '.anc')

    # get ancillary data
    print('\n >=====>  checking for best ancillary data (Met and Ozone) locally and retrieving from web if needed...')


    meris_YYYYDDDHHMMSS= general_utilities.YYYYDDDHHMMSS_from_new_fname(root_name)
    os.system('getanc -v -s ' + meris_YYYYDDDHHMMSS)
    #fname_ancil_list = olci_YYYYDDDHHMMSS + '.anc'
    #general_utilities.my_getanc(olci_YYYYDDDHHMMSS)
    fname_ancil_list= general_utilities.get_ancillary_list_fname(meris_YYYYDDDHHMMSS)


    print('\n--------------------------------------')
    print('ifile='   + first_band)
    print('ofile1='  + color_l2_file_fname)
    print('l2prod1=' + prod_list)
    print('par='     + fname_ancil_list)
    print('--------------------------------------\n')

    print('\n >=====> generating level-2 OC data from level-1 meris data using l2gen...\n\n')

    os.chdir(dir_name)
    call(['l2gen',
          'ifile='   + 'xfdumanifest.xml',
          'ofile1='  +  color_l2_file_fname,
          'l2prod1=' +  prod_list,
          'par='     +  os.environ['MYPYTHONPROGRAMS'] + '/' + fname_ancil_list])
    os.chdir(os.environ['MYPYTHONPROGRAMS'])



def hawkeye_level12(file_name, root_name, prod_list, color_l2_file_fname):


    #SEAHAWK1_HAWKEYE.20210927T151412.L1A.nc
    #SEAHAWK1_HAWKEYE.20210927T151412.GEO.nc

    fname_geo = file_name[:-7] + '.GEO.nc'  #remove .L1A.nc and add .GEo.nc
    os.system('geolocate_hawkeye ' + file_name)

    os.system('getanc ' + file_name)
    fname_ancil_list= general_utilities.get_ancillary_list_fname(file_name)

    print('\n\n\n>>>>---------------------> ancillary file name: ',fname_ancil_list)

    call(['l2gen',
          'ifile='   + file_name,
          'ofile='   + color_l2_file_fname,
          'geofile=' + fname_geo,
          'l2prod1=' + prod_list,
          'par=' + fname_ancil_list])

    os.system('rm ' + fname_geo)




def oci_level12(file_name, root_name, prod_list, color_l2_file_fname):


    os.system('getanc -v ' + file_name)
    fname_ancil_list= general_utilities.get_ancillary_list_fname(file_name)
    print('\n\n\n>>>>---------------------> ancillary file name: ',fname_ancil_list)

    call(['l2gen',
          'ifile='   + file_name,
          'ofile='   + color_l2_file_fname,
          'l2prod1=' + prod_list,
          'par='     + fname_ancil_list])











def buffer_jday_zeros(orig_jday):
    if len(orig_jday) == 1:  orig_jday = '00' + orig_jday
    if len(orig_jday) == 2:  orig_jday = '0' + orig_jday
    return  orig_jday


#------------------------------------------------------------------------------
# lists for standard products produced in the L1 to L2 processing step...
# note that is a specific prod_list is prescribed in the Batch_Proce.py then
# the OC_suite below is ignored and processing will produce the products
# precribed in Batch_Proce.py
#------------------------------------------------------------------------------




def get_oc_suite(satellite_name):

    if satellite_name == 'MODIS':
        prod_list = 'Rrs_nnn,chlor_a,Kd_490,pic,poc,ipar,nflh'

    elif satellite_name == 'SEAWIFS' or satellite_name == 'VIIRS':
        prod_list = 'Rrs_nnn,Kd_490,chlor_a,pic,poc,par'

    elif satellite_name == 'MERIS' or satellite_name == 'OLI' or satellite_name == 'OLCI' or satellite_name == 'MSI' or satellite_name == 'LANDSAT8' :
        prod_list = 'Rrs_nnn,Kd_490,chlor_a'

    return prod_list


# -----------------------------------------------------------------------------------------
#       batch processing
# -----------------------------------------------------------------------------------------

def batch_proc_L12(l1a_dir, l2_dir, prod_list, prod_list_sst, swir_onoff, hires, latlon):



    # make sure directories are right (/ and ~)
    l1a_dir = general_utilities.path_reformat(l1a_dir)
    l2_dir = general_utilities.path_reformat(l2_dir)


    # untar any tar files if necessary....
    # Large data orders from the ocweb come as tared directories that contain
    # individually compressed data files.  This function extracts all of compressed
    # data files from all of the tared directories found in l1a_dir...
    # ---
    if len(glob.glob(l1a_dir + '/*.tar')) != 0: general_utilities.untar_ocweb(l1a_dir)


    # decompress files if necessary
    while any([general_utilities.is_compressed(fi) for fi in glob.glob(l1a_dir + '/*')]):
        for fi in glob.glob(l1a_dir + '/*'): general_utilities.decompress_file(fi)



    fname_l1a =      glob.glob(l1a_dir + '/*L1*')

    fname_landsat =  glob.glob(l1a_dir + '/LC*')         # This will find landsat directories not .nc files
    if len(fname_landsat) != 0: fname_l1a=fname_landsat  # each landsat directory is equivalent a single L1A1 .nc file

    fname_meris =  glob.glob(l1a_dir + '/*MER_*')        # if there are meris N1 file directories (equal to level 1 nc files)
    if len(fname_meris) != 0: fname_l1a=fname_meris

    fname_olci =  glob.glob(l1a_dir + '/S3?*')           # this will find olci "directories" not .nc files
    if len(fname_olci) != 0: fname_l1a=fname_olci        # each olci directory is equivalent a single L1A1 .nc file

    fname_msi =  glob.glob(l1a_dir + '/S2?_MSI*')        # this will find msi "directories" not .nc files
    if len(fname_msi) != 0: fname_l1a=fname_msi          # each msi directory is equivalent a single L1A1 .nc file

    if len(fname_l1a) == 0:
        print('There are no L1 files in ' + l1a_dir)     # if not L1A and no Landat 8 then there are no usable level 1 data files..
        sys.exit()


    # if user doesn't specify level 2 directory, make one next to L1 data directory
    # otherwise use the l2dir specificied in BatchProc.py...
    if l2_dir == 'not_specified':
        l2_dir = os.path.dirname(l1a_dir) + '/' + 'L2_files'

    if not os.path.exists(l2_dir):
        os.makedirs(l2_dir)


# -----------------------------------------------------------------------------------


    # Create a new list containing output L2 rootnames cooresponding
    # to the respective input L1A files...
    # ---

    # Get basenames of L1 files (called root_names here)...
    root_name = [os.path.basename(i) for i in fname_l1a]

    #print '\n\nroot_name from fname_l1a at line 644 ===>  ', root_name, '\n\n'

    # The function fname_new_from_old (found in my_general_utilities)
    # Will create the new name convention (as of January 2020) for
    # L2 filename root part that has MISSION_INSTRUMENT_TYPE.YYYYMMDDTHHMMSS
    # ---
    root_name_trim = [general_utilities.fname_new_from_old(name) for name in root_name]

    color_l2_file_fname = [l2_dir + '/' + name + '.L2.OC.nc'  for name in root_name_trim]
    sst_l2_file_fname =   [l2_dir + '/' + name + '.L2.SST.nc' for name in root_name_trim]


    #------------------------------------------------------------------------------

    # set SWIR option for later use in l2gen call...
    if swir_onoff == 'on':
        aerosol_corr_type = '-9'
    else:
        aerosol_corr_type = '-2'

    #------------------------------------------------------------------------------


    # identify satellite by first name in file
    # appropriate satellite name.
    # Note; root_name_trim= MISSION_INSTRUMENT_TYPE.YYYYMMDDTHHMMSS
    # ---
    satellite_name= root_name_trim[0].split('_')[1]
    print('satellite_name =====> ', satellite_name)



    # if "prod_list" was set to "OC_suite" in Batch_Proc.py then get the list
    # of products to be produced in L1 to L2 processing (see very top of this module)
    # ---
    if prod_list == 'OC_suite': prod_list= get_oc_suite(satellite_name)



    # MODIS
    if 'MODIS' in satellite_name:
        for i in range(0,len(fname_l1a)):
            modis_level12(fname_l1a[i], root_name_trim[i], prod_list, prod_list_sst, color_l2_file_fname[i], sst_l2_file_fname[i],  aerosol_corr_type, hires)

    # SEAWIFS, MERIS-RR, HICO
    if ('SEAWIFS' in satellite_name or 'HICO' in satellite_name):
        for i in range(0,len(fname_l1a)):
            seawifs_hico_level12(fname_l1a[i], root_name_trim[i], prod_list, color_l2_file_fname[i])

    # VIIRS
    if 'VIIRS' in satellite_name:
        for i in range(0,len(fname_l1a)):
            viirs_level12(fname_l1a[i], root_name_trim[i], prod_list, color_l2_file_fname[i], prod_list_sst, sst_l2_file_fname[i],latlon)

    # Landsat 8
    if 'OLI' in satellite_name:
        for i in range(0,len(fname_l1a)):
            oli_level12(fname_l1a[i], prod_list, color_l2_file_fname[i], latlon)

    # Sentinal-3 OLCI
    if 'OLCI' in satellite_name:
        for i in range(0,len(fname_l1a)):
            olci_level12(fname_l1a[i], root_name_trim[i], prod_list, color_l2_file_fname[i],latlon)

    # Sentinal-2 MSI
    if 'MSI' in satellite_name:
        for i in range(0,len(fname_l1a)):
            msi_level12(fname_l1a[i], root_name_trim[i], prod_list, color_l2_file_fname[i])

    # Sentinal-2 MSI
    if 'MERIS' in satellite_name:
        for i in range(0,len(fname_l1a)):
            meris_level12(fname_l1a[i], root_name_trim[i], prod_list, color_l2_file_fname[i])

    # Hawkeye
    if 'HAWKEYE' in satellite_name:
        for i in range(0,len(fname_l1a)):
            hawkeye_level12(fname_l1a[i], root_name_trim[i], prod_list, color_l2_file_fname[i])

    # PACE
    if 'OCI' in satellite_name:
        for i in range(0,len(fname_l1a)):
            oci_level12(fname_l1a[i], root_name_trim[i], prod_list, color_l2_file_fname[i])




    # clean up...
    types = ['*.anc','*.atteph','*L1B_LAC','*L1B_HKM*','*L1B_QKM*','*.pcf']
    for t in types:
        for i in glob.glob(l1a_dir + '/' + t): os.remove(i)

    types = ['*.GEO*','*.anc','*.atteph','*L1B_LAC','*L1B_HKM*','*L1B_QKM*','*.pcf']
    for t in types:
        for i in glob.glob(t): os.remove(i)
