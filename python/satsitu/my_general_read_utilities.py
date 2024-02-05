
import numpy as np
from my_hdf_cdf_utilities import *


from matplotlib import *
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import *
from my_hdf_cdf_utilities import *
from my_mapping_utilities import *
from my_general_utilities import *
import map_coords
from pylab import *
import math
import os

from netCDF4 import Dataset
from pyhdf.SD import *

from datetime import date, timedelta


def read_ghrsst_sst(fname):
#---------------------------------------------------------------

    root_name= os.path.basename(fname)
    pf_check= "AVHRR_Pathfinder" in root_name

    if pf_check == 1:
        sst= read_hdf_prod(fname, 'sea_surface_temperature',nc_autoscale=True).squeeze()
    else: sst= read_hdf_prod(fname, 'analysed_sst',nc_autoscale=True).squeeze()

    sst_data = sst.data
    sst_mask = sst.mask


    masked_locations= np.where(sst_mask)
    sst_data[masked_locations] = np.nan


    sst_data= sst_data - 273.15 #converting from Kelvin to Celsius



    if pf_check == 1: sst_data= flipud(sst_data)

    return sst_data


'''
def read_quikscat_wind(fname):

# Read Quikscat wind downloaded from the PODAAC DRIVE
#---------------------------------------------------------------

    rainqc=0

    asc_wind_U= read_hdf_prod(fname,'asc_avg_wind_vel_u')
    asc_wind_V= read_hdf_prod(fname,'asc_avg_wind_vel_v')

    des_wind_U= read_hdf_prod(fname,'des_avg_wind_vel_u')
    des_wind_V= read_hdf_prod(fname,'des_avg_wind_vel_v')

    asc_rain_flag= read_hdf_prod(fname,'asc_rain_flag')
    des_rain_flag= read_hdf_prod(fname,'des_rain_flag')


    # flag bad data due to rain at the prescribed qc level maximum
    # flage level is 7.  Best data is 7 worst data is zero ...
    # --- set bad data to zero ---
    asc_wind_U[np.where(asc_rain_flag != rainqc)]=0
    asc_wind_V[np.where(asc_rain_flag != rainqc)]=0

    des_wind_U[np.where(des_rain_flag != rainqc)]=0
    des_wind_V[np.where(des_rain_flag != rainqc)]=0


    # average assending and decending wind for u and v respectively
    # slope = 0.01
    data_cnt_asc= asc_wind_U != 0
    data_cnt_des= des_wind_U != 0
    total_cnt = 1*data_cnt_asc + 1*data_cnt_des       #1* converts True,False to 1s, 0s
    wind_u= (asc_wind_U + des_wind_U)*0.01/total_cnt
    wind_u[where(total_cnt == 0)]= np.nan

    data_cnt_asc= asc_wind_V != 0
    data_cnt_des= des_wind_V != 0
    total_cnt = 1*data_cnt_asc + 1*data_cnt_des       #1* converts True,False to 1s, 0s
    wind_v= (asc_wind_V + des_wind_V)*0.01/total_cnt
    wind_v[where(total_cnt == 0)]= np.nan


    wind_uv = np.zeros((2,720,1440))
    wind_uv[0,:,:] =  np.roll(wind_u, 720,1)
    wind_uv[1,:,:] =  np.roll(wind_v, 720,1)

                                            #np.roll --->  shifts lon from 0-360 --->  -180 to 180

    return wind_uv

'''


def read_ssmi_speed(filename):
#---------------------------------------------------------------

    #Note: binarydata= (2,5,720,1440, dtype=int8)
    #Full Data Array that will be read in from the hard drive
    #1440 and 720 are the xpixel and ypixel number
    #5 is the number of geophyical variable with wind = var 1
    #2 is the day/evening pass for each of the five variables

    #Note:  multipliers to change binary DN data to real
    #geophysical values  xscale=np.asarray([6,.2,.3,.01,.1])


    f1 = open(filename, 'rb')
    data = np.fromfile(f1, dtype=np.uint8)
    f1.close()

    #binarydata= data.reshape(1440,720,5,2)
    binarydata= data.reshape(2,5,720,1440)

    speed_am= binarydata[0,1,:,:]      #1=speed variable, 0=morning
    speed_pm= binarydata[1,1,:,:]      #1=speed variable, 1=evening


    bad_am_locations= np.where(speed_am > 250)
    bad_pm_locations= np.where(speed_pm > 250)

    speed_am=  speed_am*0.2   #scale factor for wind speed
    speed_pm=  speed_pm*0.2   #scale factor for wind speed


    speed_am[bad_am_locations]=  np.nan
    speed_pm[bad_pm_locations]=  np.nan

    total_array  = nan_to_num(speed_am) + nan_to_num(speed_pm)
    total_counts = (~isnan(speed_am)).astype(int) + (~isnan(speed_pm)).astype(int)
    speed_am_pm  = total_array/total_counts

    speed_am_pm = np.roll(speed_am_pm,720,1)

    return speed_am_pm




def read_ssmi_monthly(filename):
#---------------------------------------------------------------

    #Note: binarydata= (4,720,1440, dtype=int8)
    #Full Data Array that will be read in from the hard drive
    #1440 and 720 are the xpixel and ypixel number
    #5 is the number of geophyical variable with wind = var 1
    #2 is the day/evening pass for each of the five variables

    #Note:  multipliers to change binary DN data to real
    #geophysical values  xscale=np.asarray([6,.2,.3,.01,.1])


    f1 = open(filename, 'rb')
    data = np.fromfile(f1, dtype=np.uint8)
    f1.close()

    #binarydata= data.reshape(1440,720,5,2)
    binarydata= data.reshape(4,720,1440)

    speed= binarydata[0,:,:]      #1=speed variable, 0=morning

    bad_locations= np.where(speed > 250)
    speed=  speed*0.2   #scale factor for wind speed
    speed[bad_locations]=  np.nan

    speed = np.roll(speed,720,1)
    speed= np.flipud(speed)

    return speed




def read_ascat_wind(filename):
#---------------------------------------------------------------

    # Note: binarydata= (2,5,720,1440, dtype=int8)
    # Full Data Array that will be read in from the hard drive
    #
    #   Dimensions 1440 and 720 are the xpixel and ypixel number

    #   Dimension 5 is the number of geophyical variables
    #   UTC Time = var 0
    #   wind speed = var 1
    #   wind direction = var 2
    #   Rain Flag = var 3
    #   Sum of Squares Map = var 4
    #
    #   Dimension 2 is the day/evening pass for each of the five variables

    #For Details, See: http://www.remss.com/missions/ascat/

    f1 = open(filename, 'rb')
    data = np.fromfile(f1, dtype=np.uint8)
    f1.close()

    binarydata= data.reshape(2,5,720,1440)

    speed_am= binarydata[0,1,:,:]      #1=speed variable, 0=morning
    speed_pm= binarydata[1,1,:,:]      #1=speed variable, 1=evening

    direction_am=binarydata[0,2,:,:]
    direction_pm=binarydata[1,2,:,:]

    rain_flag_am=binarydata[0,3,:,:]
    rain_flag_pm=binarydata[0,3,:,:]

    #-------------------------------------------------
    bad_am_locations= np.where(speed_am > 250)
    bad_pm_locations= np.where(speed_pm > 250)

    bad_am_direction=np.where(direction_am > 250)
    bad_pm_direction=np.where(direction_pm > 250)

    am_first_rain_bit_set= np.bitwise_and(rain_flag_am,1) # 1 if set or 0 is not set
    pm_first_rain_bit_set= np.bitwise_and(rain_flag_pm,1) # 1 if set or 0 is not set

    rain_locations_am= np.where(am_first_rain_bit_set == 1) # rain present if fist bit set
    rain_locations_pm= np.where(pm_first_rain_bit_set == 1) # rain present if fist bit set
    #-------------------------------------------------

    speed_am=  speed_am*0.2   #scale factor for wind speed (m/sec)
    speed_pm=  speed_pm*0.2   #scale factor for wind speed (m/sec)

    direction_am=direction_am*1.5      #scale factor for direction (degrees)
    direction_pm=direction_pm*1.5      #scale factor for direction (degrees)

    #------------------------------------------------
    speed_am[bad_am_locations]=  np.nan
    speed_pm[bad_pm_locations]=  np.nan

    speed_am[bad_am_direction]=  np.nan
    speed_pm[bad_pm_direction]=  np.nan

    speed_am[rain_locations_am]=  np.nan
    speed_pm[rain_locations_pm]=  np.nan
    #-------------------------------------------------

    u_am=speed_am*np.sin(direction_am*(np.pi/180.))
    v_am=speed_am*np.cos(direction_am*(np.pi/180.))

    u_pm=speed_pm*np.sin(direction_pm*(np.pi/180.))
    v_pm=speed_pm*np.cos(direction_pm*(np.pi/180.))



    total_u_array  = nan_to_num(u_am) + nan_to_num(u_pm)
    total_u_counts = (~isnan(u_am)).astype(int) + (~isnan(u_pm)).astype(int)
    u_am_pm  = total_u_array/total_u_counts

    u_am_pm = np.roll(u_am_pm,720,1)


    total_v_array  = nan_to_num(v_am) + nan_to_num(v_pm)
    total_v_counts = (~isnan(v_am)).astype(int) + (~isnan(v_pm)).astype(int)
    v_am_pm  = total_v_array/total_v_counts

    v_am_pm = np.roll(v_am_pm,720,1)

    uv = np.zeros((2,720,1440))
    uv[0,:,:] = np.flipud(u_am_pm)
    uv[1,:,:] = np.flipud(v_am_pm)

    return uv





def read_windsat_wind(filename, windprod):
#---------------------------------------------------------------

    # Note: binarydata= (2,9,720,1440, dtype=int8)
    # Full Data Array that will be read in from the hard drive
    #
    #   Dimensions 1440 and 720 are the xpixel and ypixel number
    #
    #   Dimension 9 is the number of geophyical variables
    #var 0 -- Time (TIME),
    #var 1 -- Sea Surface Temperature (SST),
    #var 2 -- 10-meter Surface Wind Speed at Low Frequency (WSPD_LF),
    #var 3 -- 10-meter Surface Wind Speed at Medium Frequency (WSPD_MF),
    #var 4 -- Atmospheric Water Vapor (VAPOR),
    #var 5 -- Cloud Liquid Water (CLOUD),
    #var 6 -- Rain Rate (RAIN),
    #var 7 -- All-Weather 10-meter Surface Wind speed (WSPD_AW),
    #var 8 -- Surface Wind Direction (WDIR).
    #
    #   Dimension 2 is the day/evening pass for each of the five variables

    #Note: WDIR: Because of its polarimetric channels, WindSat can measure surface wind direction.
    #WDIR is only provided if the wind speed exceeds 3 m/s and the rain rate is below 15 mm/hr.

    #For Details, See: http://www.remss.com/missions/windsat/

    f1 = open(filename, 'rb')
    data = np.fromfile(f1, dtype=np.uint8)
    f1.close()

    binarydata= data.reshape(2,9,720,1440)

    if windprod == 'WSPD_LF': var=2
    if windprod == 'WSPD_MF': var=3
    if windprod == 'WSPD_AW': var=7


    speed_am= binarydata[0,var,:,:]      #1=speed variable, 0=morning
    speed_pm= binarydata[1,var,:,:]      #1=speed variable, 1=evening

    direction_am=binarydata[0,8,:,:]
    direction_pm=binarydata[1,8,:,:]

    #-------------------------------------------------
    bad_am_locations= np.where(speed_am > 250)
    bad_pm_locations= np.where(speed_pm > 250)

    bad_am_direction=np.where(direction_am > 250)
    bad_pm_direction=np.where(direction_pm > 250)

    #-------------------------------------------------

    speed_am=  speed_am*0.2   #scale factor for wind speed (m/sec)
    speed_pm=  speed_pm*0.2   #scale factor for wind speed (m/sec)

    direction_am=direction_am*1.5      #scale factor for direction (degrees)
    direction_pm=direction_pm*1.5      #scale factor for direction (degrees)

   #-------------------------------------------------
    speed_am[bad_am_locations]=  np.nan
    speed_pm[bad_pm_locations]=  np.nan

    speed_am[bad_am_direction]=  np.nan
    speed_pm[bad_pm_direction]=  np.nan

    #-------------------------------------------------


    u_am=speed_am*np.sin(direction_am*(np.pi/180.))
    v_am=speed_am*np.cos(direction_am*(np.pi/180.))

    u_pm=speed_pm*np.sin(direction_pm*(np.pi/180.))
    v_pm=speed_pm*np.cos(direction_pm*(np.pi/180.))



    total_u_array  = nan_to_num(u_am) + nan_to_num(u_pm)
    total_u_counts = (~isnan(u_am)).astype(int) + (~isnan(u_pm)).astype(int)
    u_am_pm  = total_u_array/total_u_counts

    u_am_pm = np.roll(u_am_pm,720,1)


    total_v_array  = nan_to_num(v_am) + nan_to_num(v_pm)
    total_v_counts = (~isnan(v_am)).astype(int) + (~isnan(v_pm)).astype(int)
    v_am_pm  = total_v_array/total_v_counts

    v_am_pm = np.roll(v_am_pm,720,1)

    uv = np.zeros((2,720,1440))
    uv[0,:,:] = np.flipud(u_am_pm)
    uv[1,:,:] = np.flipud(v_am_pm)

    return uv




def read_quikscat_wind(filename):
#---------------------------------------------------------------

    # Note: binarydata= (2,5,720,1440, dtype=int8)
    # Full Data Array that will be read in from the hard drive
    #
    #   Dimensions 1440 and 720 are the xpixel and ypixel number

    #   Dimension 5 is the number of geophyical variables
    #   UTC Time = var 0
    #   wind speed = var 1
    #   wind direction = var 2
    #   Rain Flag = var 3
    #   Sum of Squares Map = var 4
    #
    #   Dimension 2 is the day/evening pass for each of the five variables

    #For Details, See: http://www.remss.com/missions/ascat/

    f1 = open(filename, 'rb')
    data = np.fromfile(f1, dtype=np.uint8)
    f1.close()

    binarydata= data.reshape(2,4,720,1440)

    speed_am= binarydata[0,1,:,:]      #1=speed variable, 0=morning
    speed_pm= binarydata[1,1,:,:]      #1=speed variable, 1=evening

    direction_am=binarydata[0,2,:,:]
    direction_pm=binarydata[1,2,:,:]

    rain_flag_am=binarydata[0,3,:,:]
    rain_flag_pm=binarydata[0,3,:,:]

    #-------------------------------------------------
    bad_am_locations= np.where(speed_am > 250)
    bad_pm_locations= np.where(speed_pm > 250)

    bad_am_direction=np.where(direction_am > 250)
    bad_pm_direction=np.where(direction_pm > 250)

    am_first_rain_bit_set= np.bitwise_and(rain_flag_am,1) # 1 if set or 0 is not set
    pm_first_rain_bit_set= np.bitwise_and(rain_flag_pm,1) # 1 if set or 0 is not set

    rain_locations_am= np.where(am_first_rain_bit_set == 1) # rain present if fist bit set
    rain_locations_pm= np.where(pm_first_rain_bit_set == 1) # rain present if fist bit set
    #-------------------------------------------------

    speed_am=  speed_am*0.2   #scale factor for wind speed (m/sec)
    speed_pm=  speed_pm*0.2   #scale factor for wind speed (m/sec)

    direction_am=direction_am*1.5      #scale factor for direction (degrees)
    direction_pm=direction_pm*1.5      #scale factor for direction (degrees)

    #------------------------------------------------
    speed_am[bad_am_locations]=  np.nan
    speed_pm[bad_pm_locations]=  np.nan

    speed_am[bad_am_direction]=  np.nan
    speed_pm[bad_pm_direction]=  np.nan

    speed_am[rain_locations_am]=  np.nan
    speed_pm[rain_locations_pm]=  np.nan
    #-------------------------------------------------

    u_am=speed_am*np.sin(direction_am*(np.pi/180.))
    v_am=speed_am*np.cos(direction_am*(np.pi/180.))

    u_pm=speed_pm*np.sin(direction_pm*(np.pi/180.))
    v_pm=speed_pm*np.cos(direction_pm*(np.pi/180.))



    total_u_array  = nan_to_num(u_am) + nan_to_num(u_pm)
    total_u_counts = (~isnan(u_am)).astype(int) + (~isnan(u_pm)).astype(int)
    u_am_pm  = total_u_array/total_u_counts

    u_am_pm = np.roll(u_am_pm,720,1)


    total_v_array  = nan_to_num(v_am) + nan_to_num(v_pm)
    total_v_counts = (~isnan(v_am)).astype(int) + (~isnan(v_pm)).astype(int)
    v_am_pm  = total_v_array/total_v_counts

    v_am_pm = np.roll(v_am_pm,720,1)

    uv = np.zeros((2,720,1440))
    uv[0,:,:] = np.flipud(u_am_pm)
    uv[1,:,:] = np.flipud(v_am_pm)

    return uv








def read_altimetry_dates(ifile):
    elapsed_days= read_hdf_prod(ifile,'time').squeeze()  # number of days since 1950-01-01 00:00:00.
    start_day= date(1950,1,1)

    date_list=[]
    for name in elapsed_days:
        delta = timedelta(int(name))
        data_date = start_day + delta
        string_time= data_date.strftime('%Y-%m-%d')
        date_list.append(string_time)

    print('\nnaltimetry data dates: ',date_list,'\n' )
    return date_list



def read_altimetry_adh(ifile):
#---------------------------------------------------------------

    date_list= read_altimetry_dates(ifile)
    adt_full = read_hdf_prod(ifile,'adt').squeeze()
    print('\n adt data have units of meters...\n')
    return date_list, adt_full


def read_altimetry_uv(ifile):
#---------------------------------------------------------------
    date_list= read_altimetry_dates(ifile)

    u= read_hdf_prod(ifile,'ugos')
    v= read_hdf_prod(ifile,'vgos')
    #uv = np.where(uv == -2147483647, np.nan, uv)       #set missing data to NAN

    print('\naviso uv data have units of meters/sec...\n')

    return date_list,u,v








def read_reynolds_oi(ifile):
#---------------------------------------------------------------
    f1 = open(ifile, 'rb')
    data = fromfile(f1, dtype=np.float32)
    f1.close()

    data=data.newbyteorder()   #swap the byte order
    sst=  data[8:64800+8]      #skip 8 hearder pieces of information

    input_sst_dir = os.path.dirname(ifile)

    land_file= input_sst_dir + '/' + 'lstags.onedeg.dat'
    f1 = open(land_file, 'rb')
    land = fromfile(f1, dtype=np.int32)
    f1.close()

    land=land.newbyteorder()
    land_locations= np.where(land == 0)
    bad_locations1= np.where(sst < 1.8)
    bad_locations2= np.where(sst > 35.0)

    sst[land_locations]=np.nan
    sst[bad_locations1]=np.nan
    sst[bad_locations2]=np.nan

    sst=sst.reshape(180,360)

    return sst



def read_icesat2_prod(ifile,track_name,prod):
#---------------------------------------------------------------
# Note, this code hacked form the read_hdf_prod found in my_had_cdf_utilities
# The main change is that this hack will read through all 6 alongtack datasets
# where each track is stored as a separate group.
# Note: autoscaling is set to on now so no need to remove missing data.
# --

    f = Dataset(ifile, 'r')

    group_names= list(f.groups.keys())  #get group names (e.g. geophtsical_data_sets or navigation)

    for grp_name in group_names:
        if grp_name == track_name:
            var_name= list(f.groups[grp_name].variables.keys())  #get names of objects within each group (e,g. chlor_a or longitude)
            for vn in var_name:
                if vn == prod:
                    p =  f.groups[grp_name].variables[vn]
                    data=  p[:]
                    f.close()
                    return data
