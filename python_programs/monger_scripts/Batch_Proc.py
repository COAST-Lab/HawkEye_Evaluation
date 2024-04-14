#! /usr/bin python
import sys

sys.path.insert(0, 'utilities')
sys.dont_write_bytecode = True

import batch_L12
import batch_L23

#           To execute, edit the directories and variables below,
#         and call this python script from the command line by typing:
#
#                         python Batch_Proc.py

###############################################################################
# Define the Input and Desired Output Data Processing Levels
# And Then Specify the Directories for Each Data Level
###############################################################################

#-----------------------------------------------------------------------------
# Input Data Level - Choices Are: '1' for Level-1 files or '2' for Level-2 files
#-----------------------------------------------------------------------------
Input_Level ='2'

#-----------------------------------------------------------------------------
# Output Data Level - Choices are '2' for Level-2 files or '3' for Level-3 files
#------------------------------------------------------------------------------
Final_level = '3'


#  -------------------------------------------------------------------------
#  Location of the Level-1 Files:
#  -------------------------------------------------------------------------
l1a_dir = '/Users/coastlab/data/satellite_matchups/landsat/l1a/LC08_L1TP_015036_20230503_20230509_02_T1'

#  -------------------------------------------------------------------------
#  Location where Level-2 Files will be written when processed from
#  Level-1 to Level-2.  Or... Location where Level-2 Files were downloaded
#  from Ocean Color Web
#  -------------------------------------------------------------------------
l2_dir = '/Users/coastlab/data/satellite_matchups/sensors/modisa/l2'

#  -------------------------------------------------------------------------
#  Location where Level-3 Files will be written when processed from
#  Level-1 to Level-3 or Level-2 to Level-3.
#  -------------------------------------------------------------------------
binmap_dir ='/Users/coastlab/data/satellite_matchups/sensors/modisa/l2-l3'

#  -------------------------------------------------------------------------
#  Setup Latitude and Longitude for Level-3 file generation
#  Note: Latitude-Longitude Order MUST BE: 'south, west, north, east'
#
#  Note Also, that West Longitude and North Latitude are demoted with negative values
#  and East Longitude and South Latitude are denoted with positive.
#
#  Crossing the Dateline:  Use only positive Longitude values of 0-360.
#  -------------------------------------------------------------------------
latlon = '34.10,-77.85,34.25,-77.70'     # Lat/Lon Order is S,W,N,E   --Masonboro Inlet
#latlon = '33.75, -78.25, 34.5, -77.5'   # Lat/Lon Order is S,W,N,E   --Wilmington
#latlon = '33,-79,36,-76'                # Lat/Lon Order is S,W,N,E   --Onslow Bay
#latlon = '30,-78,54,-50'                # Lat/Lon Order is S,W,N,E   --Test for OCI L2
#latlon = '-20.,176,-15,182'             # Lat/Lon Order is S,W,N,E   --Fiji
#latlon = '18.,-158.5,22,-153.5'         # Lat/Lon Order is S,W,N,E   --Hawaii
#latlon = '18.75,-155.75,19.75,-154.75'  # Lat/Lon Order is S,W,N,E   --Southeast Coast Big Island
#############################################################################
#  ------------>  Optional L1 -> L2 Processing Variables   <---------------
#############################################################################

# LIST OF OC PRODUCTS TO BE GENERATED FROM LEVEL-1 RAW DATA VIA L2GEN
# ------------------------------------------------------------------
# The ocean color (and/or sst) list of products to be derived in L1 to L2 via
# l2gen function in seadas is set with the varable: 'prod_list_L12'
#
# Set: prod_list_L12 = 'OC_suite' to produce a standard suite of OC products
# (see batch_l2.py) for current suite. Otherwise set prod_list_L12 to a narrow
# list of specific OC products for example: prod_list_L12 ='chlor_a,pic,poc'
#
# For the case of modis and virrsn you also have the option to set sst output
# Options Are: prod_list_L12 = 'sst' or 'none' (future plans will allow sst4)
# -----------------------------

prod_list_L12 =    'kd_490'
#prod_list_L12 =    'chlor_a,Rrs_nnn,pic,poc,kd_490'  # NOTE: Comma separated (no spaces) list of products.
                              #
                              # PACE NOTE: Use Rrs_nnn to produce all Rrs
                              #            wavelengths.For hyperspectral PACE L1 data,
                              #            you will likey want to use Rrs_nnn to have all
                              #            hyperspectral wavelengths

prod_list_L12_sst= 'sst'      # Options are 'sst' or 'none'



# NOTE: As of January 2022 viirsj1 sst data cannot be proessed.
# The Goddard folks explain that this is a personel issue and not a
# technical issue.

# High Resolution Product processing for "MODIS" ONLY" --- OPTIONS: 'on' or 'off'
# ---------------------------
hires = 'off'


# NOTE: --->  Processing hires bands is a 'slow' process if the lat/lon limits
#exceed 3 or 4-deg lat/lon. If you are running modis be sure to extract the
#the L1A files with tight bounds at the time of ordering the data.
#
#For FRS Meris data, extraction of L1B files is not possible. In this case
#use the function:bulk_extract_meris(l1a_dir, extract_dir, extract_latlon)
#that is contained in my_general_utilities.py to first extract the L1B. This
#will make new extracted files (without removing originals).
#l1a_dir= dir of unxtracted files: extract_dir= director to place new extraced
#files: extract_latlon= comma delimed string of tight lat/lon bounds swne
# for example '36.0,-72.0, 38.0,-70.0'   Then use extracted files any normal
#Level-1 file for processing...


# Use of Short Wave Infrared --- Options: 'on' or 'off'
# ------------------------------------------------------
swir_onoff = 'off'


# L2GEN NOTE:
# There are about 1 billion different options you can choose to
# alter how l2gen processes your data and all and 99.999% are outside the
# scope of this class, but open a terminal window and type l2gen to see
# all 1 billion options.  If some options interest you, then go to
# batch_L12.py and manually add them to: l2gen CALL([...,...,...,]).
#--------------------------------------------------------------------------





###############################################################################
#   ------------>  Optional L2 -> L3 Processing  Variables  <---------------
###############################################################################

# Force Staraight Map (yes/no)???
# ----------------------------------
straight_map= 'no'  # options are yes or no...

                    # PACE ONLY NOTE:  At this point, the only option for PACE
                    #                  data is straight_map = 'no'.


# If straight map set to no, then give l2bin size -Spatial Binning Resolution
# Options Are:
# ---
# 'H'= 0.5km,          'Q'= 250m,         'HQ'=100m,      'HH'=50m
# '1'= 1.1km,          '2'= 2.3km,        '4'= 4.6km,     '9'= 9.2km,  '18'= 18.5km,  '36'= 36km
# 'QD'= 0.25 degree,   'HD'= 0.5 degree,  '1D'= 1 degree
#-------------------------------
#space_res = '1'
space_res = '1'


# l3bin -Temporal Binning (Averaging Period) daily, weekly, or monthly
# Options Are: DLY, WKY, or MON
# ------------------------------
time_period = 'DLY'


# Binning or Straight Mapping Statistics Output, on or off.
# This tunes on file output of variance and numer of pixel in binning process
# Default is no, options are 'yes' or  'no'
# -----------------------------
stats_yesno = 'yes'


# Quality Flags to be used for color products. #Default is 'standard' as set
# prescibed in the SeaDAS Installation Directory. Otherwise provide your own
# list of named flags to check (a single string of comma separated)
# Same thing goes sst products...
#------------------------------

#color_flags= 'standard'  # color_flags= 'ATMFAIL,LAND,HILT,HISATZEN,STRAYLIGHT,CLDICE,COCCOLITH,LOWLW,CHLWARN,CHLFAIL,NAVWARN,MAXAERITER,ATMWARN,HISOLZEN,NAVFAIL,FILTER,HIGLINT,ATMWARN,HISOLZEN'

color_flags = 'ATMFAIL,LAND,HILT,HISATZEN,STRAYLIGHT,CLDICE,COCCOLITH,LOWLW,CHLWARN,CHLFAIL,NAVWARN'

# HAWKEYE NOTE:   >>> It seems that if either MAXAERITER or ATMWARN are used, all chl values as flagged when doing straight map.
#                     Consider using:  color_flags='ATMFAIL,LAND,HILT,HISATZEN,STRAYLIGHT,CLDICE,COCCOLITH,LOWLW,CHLWARN,CHLFAIL,NAVWARN'

#color_flags= 'ATMFAIL,LAND,CLDICE,HILT'
#color_flags= 'standard'

sst_flags =  'standard'


# If you have L2 files with more products than you want to map right now, then
# you can choose to limit which products in the L2 are mapped to L3.
# Options are:   prod_list_L23 ='all'  for all products in the L2 file to be
# mapped or else a specific list of products, for example..
# prod_list_L23 ='chlor_a,pic,poc,cdom_index'
# ----------------------------
#prod_list_L23 = 'all'
prod_list_L23 = 'all'
                             # PACE NOTE: If you are processing Level-2 PACE data
                             #            that was either downloaed as Level-2 AOP files or
                             #            processed here from L1 to L2,then you must use
                             #            prod_list_L23 = 'all' to map all hyerspecteral
                             #            wavelenghts.


# Projection for standard mapped image.
smi_proj = 'platecarree'

###############################################################################




# ---> Do Not Touch the Stuff Below...
################################################################################
################################################################################
################################################################################

if Input_Level == '1' and Final_level == '3':
    batch_L12.batch_proc_L12(l1a_dir, l2_dir, prod_list_L12, prod_list_L12_sst, swir_onoff, hires, latlon)
    batch_L23.batch_proc_L23(l2_dir, binmap_dir, prod_list_L23, space_res,time_period, color_flags, sst_flags, latlon, smi_proj, stats_yesno, straight_map)
elif Input_Level =='1' and Final_level == '2':
    batch_L12.batch_proc_L12(l1a_dir, l2_dir, prod_list_L12, prod_list_L12_sst, swir_onoff, hires, latlon)
elif Input_Level == '2' and Final_level == '3':
    batch_L23.batch_proc_L23(l2_dir, binmap_dir, prod_list_L23, space_res,time_period, color_flags, sst_flags, latlon, smi_proj, stats_yesno, straight_map)
else:
    print('#####  Please specify different input and output levels  #####')
    sys.exit()
