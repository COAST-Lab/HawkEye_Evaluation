# For this script to work, the user must input a tab delimited text file of the in situ data file, 
# and the satellite imagery that they would like the data appended. The script only works for the images files on my particular disk drive.
# Simply replace the fnames (lines 26, 34, 39, 44, 49, 54) with your own files and their associated filepaths. 
# This script will locate the data product (eg., chlorophyll a) at each lat/lon in the satellite images, 
# extract the value, and append it to the orgininal in situ data txt file.
# The result will be a new txt file that contains the original in situ measurements along with the desired satellite data.


###

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import glob
import os
from my_hdf_cdf_utilities import *
from my_general_utilities import *

# seabird_fname corresponds to the txt file that contains the data variables retrieved from towing the Acrobat
# hawk_fname corresponds to the L3 chlorophyll satellite image
# modisa_fname corresponds to the L3 chlorophyll satellite image, etc. 


# read in the tab delimited text file of Acrobat data
acrobat_fname = '/Users/macbook/data/acrobat/05052023/wing_angle2_dataonly.txt'
f1 = open(acrobat_fname, 'r')
all_lines = f1.readlines()
f1.close()
header_line = all_lines[0].strip() # first line is the header (also remove '/n')
all_lines = all_lines[1:] # remove header line from the List of lines

# creates a new txt file with the original Acrobat data plus the appended satellite data
output_acrobat_fname = '/Users/macbook/data/acrobat/05052023/satellite_acrobat_chlor'
f2 = open(output_acrobat_fname, 'w')
f2.write(header_line + '\tHawkeye Chl' + '\tModisa Chl' + '\tS3A Chl' + '\tS3B Chl\n')

# read in Hawkeye chlorophyl values at row/col locations of satellite data
hawk_fname = '/Users/macbook/data/satellite_matchups/smaller_area/not_straight_map/hawkeye/l2-l3/daily/chlor_a/mean/SEAHAWK1_HAWKEYE.2023050620230506.chlor_a-mean.smi.nc'
prodname = 'chlor_a'
fill_value = -32767.0

# read in Modis Aqua chlorophyll values at row/col locations of satellite data
modisa_fname = '/Users/macbook/data/satellite_matchups/smaller_area/not_straight_map/modisa/l2-l3/daily/chlor_a/mean/AQUA_MODIS.2023050720230507.chlor_a-mean.smi.nc'
prodname = 'chlor_a'
fill_value = -32767.0

# read in Sentinel 3A chlorophyll values at row/col locations of satellite data
S3A_fname = '/Users/macbook/data/satellite_matchups/smaller_area/not_straight_map/S3A/l2-l3/daily/chlor_a/mean/S3A_OLCI_EFRNT.2023050720230507.chlor_a-mean.smi.nc'
prodname = 'chlor_a'
fill_value = -32767.0

# read in Sentinel 3B chlorophyll values at row/col locations of satellite data
S3B_fname = '/Users/macbook/data/satellite_matchups/smaller_area/not_straight_map/S3B/l2-l3/daily/chlor_a/mean/S3B_OLCI_EFRNT.2023050620230506.chlor_a-mean.smi.nc'
prodname = 'chlor_a'
fill_value = -32767.0


# use this portion only to retrieve the row/col info from the NetCDF files (i.e., satellite images)
## hdf_prod_info(S3A_fname)
## hdf_prod_scale(S3A_fname, prodname)



# creates an array of the chlorophyll values contained within the satellite images. Any erroneous values are labeled NaN.
hawk_chl_array = read_hdf_prod('/Users/macbook/data/satellite_matchups/smaller_area/not_straight_map/hawkeye/l2-l3/daily/chlor_a/mean/SEAHAWK1_HAWKEYE.2023050620230506.chlor_a-mean.smi.nc', 'chlor_a')
bad_loc = np.where(hawk_chl_array == fill_value)
hawk_chl_array[bad_loc] = np.nan

modisa_chl_array = read_hdf_prod('/Users/macbook/data/satellite_matchups/smaller_area/not_straight_map/modisa/l2-l3/daily/chlor_a/mean/AQUA_MODIS.2023050720230507.chlor_a-mean.smi.nc', 'chlor_a')
bad_loc = np.where(modisa_chl_array == fill_value)
modisa_chl_array[bad_loc] = np.nan

S3A_chl_array = read_hdf_prod('/Users/macbook/data/satellite_matchups/smaller_area/not_straight_map/S3A/l2-l3/daily/chlor_a/mean/S3A_OLCI_EFRNT.2023050720230507.chlor_a-mean.smi.nc', 'chlor_a')
bad_loc = np.where(S3A_chl_array == fill_value)
S3A_chl_array[bad_loc] = np.nan

S3B_chl_array = read_hdf_prod('/Users/macbook/data/satellite_matchups/smaller_area/not_straight_map/S3B/l2-l3/daily/chlor_a/mean/S3B_OLCI_EFRNT.2023050620230506.chlor_a-mean.smi.nc', 'chlor_a')
bad_loc = np.where(S3B_chl_array == fill_value)
S3B_chl_array[bad_loc] = np.nan


# this loop goes through the original text document that contains the Acrobat data and splits each column individually, labeling them with their corresponding header info
for i in range(len(all_lines)):
	one_line = all_lines[i].strip()
	one_split_line = one_line.split('\t')
	scan_count = one_split_line[0]
	depth = one_split_line[1]
	temp = one_split_line[2]
	conductivity = one_split_line[3]
	density = one_split_line [4]
	salinity = one_split_line[5]
	time = one_split_line[6]
	turbidity = one_split_line[7]
	CDOM = one_split_line[8]
	chlor_a = one_split_line[9]
	o2_sat = one_split_line[10]
	lat = float(one_split_line[11])
	lon = float(one_split_line[12])
	flag = one_split_line [13]
	# the lat/lon values are the same for the region within the modisa and hawkeye images. this could change for different regions/satellites.
	# S: 32, E: -76, N: 36, W: -78.5


	# convert lat/lon to row/column
	icol_hawk = int((lon + 78.5)*1113.0/2.5)
	irow_hawk = int((36.0 - lat)*1781.0/4.0)

	# converts the lat/lot info to string format
	lat_hawk=str(lat)
	lon_hawk=str(lon)

	print('shape of hawkeye_chl array: ', hawk_chl_array.shape)

	hawk_chl = hawk_chl_array[irow_hawk,icol_hawk]
	print(hawk_chl)


	# convert lat/lon to row/column
	icol_aqua = int((lon + 78.5)*253.0/2.5)
	irow_aqua = int((36.0 - lat)*405.0/4.0)

	# converts the lat/lot info to string format
	lat_aqua=str(lat)
	lon_aqua=str(lon)

	print('shape of modisa_chl array: ', modisa_chl_array.shape)

	modisa_chl = modisa_chl_array[irow_aqua,icol_aqua]
	print(modisa_chl)


	# convert lat/lon to row/column
	icol_S3A = int((lon + 78.5)*557.0/2.5)
	irow_S3A = int((36.0 - lat)*891.0/4.0)

	# converts the lat/lot info to string format
	lat_S3A=str(lat)
	lon_S3A=str(lon)

	print('shape of S3A_chl array: ', S3A_chl_array.shape)

	S3A_chl = S3A_chl_array[irow_S3A,icol_S3A]
	print(S3A_chl)


	# convert lat/lon to row/column
	icol_S3B = int((lon + 80.0)*1011.0/10.0)
	irow_S3B = int((40.0 - lat)*1011.0/10.0)

	# converts the lat/lot info to string format
	lat_S3B=str(lat)
	lon_S3B=str(lon)

	print('shape of SB3_chl array: ', S3B_chl_array.shape)

	S3B_chl = S3B_chl_array[irow_S3B,icol_S3B]
	print(S3B_chl)


	f2.write((one_line) + '\t' + str(hawk_chl) + '\t' + str(modisa_chl) + '\t' + str(S3A_chl) + '\t' + str(S3B_chl) + '\n')


f2.close()