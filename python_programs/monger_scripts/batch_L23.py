
from numpy import *
from pylab import *
import sys, os
from subprocess import call
import glob
#from osgeo import gdal, gdal_array
import shutil

sys.path.insert(0, 'utilities')
sys.dont_write_bytecode = True

from my_mapping_utilities import *
from my_hdf_cdf_utilities import *
from my_general_utilities import *

from PIL import Image
from PIL import ImageEnhance


# First,   spatially bin all files in filelist (l2bin)
# Second,  create an ascii list of the l2bin files that were generated.
# Third,   use the ascii list of l2bin files to do the temporal average (l3bin)
# Fourth,  map the l3bin file.



# make bl2 files (l2bin)  -- SPATIAL BINNING.
# NOTE: filelist contains the files that will later be temporlly averaged.
#
# >>---> NOTE: This subroutine is called once for a single prod to be binned and mapped.
#
# SUBROUTINE ...
# ===============================================================
def bl2_gen(filelist, l2bin_dir, l2bin_filelist, product, named_flags_2check, space_res):


    print('\ncall to bl2_gen function for product >>>>>>-----------> ' + product)
    print('\nfilelist in l2bin loop ------> ', filelist)
    print('\nspace_res ======  ', str(space_res).strip())

    if not os.path.exists(l2bin_dir):
        os.makedirs(l2bin_dir)

    if product != 'sst':

        for j in range(0,len(filelist)):

            print('\n===============> running l2bin binary for color <==================')
            print('flags to check >>>>>>----------->' +  named_flags_2check + '\n')
            print('l2 file to bin ----> ', filelist[j])
            call(['l2bin',
                  'infile='  + filelist[j],
                  'ofile='   + l2bin_filelist[j],
                  'l3bprod=' + product,                      #<-----<<<      # NOTE: If PACE AOP L2 files, then product was set to 'all' before all to process.
                  'resolution=' + str(space_res).strip(),       #  If set to 'all' then l2bin will bin all products into each l2bin file.
                  'prodtype=' + 'regional',
                  'flaguse=' + named_flags_2check])

    if product == 'sst':
        for j in range(0,len(filelist)):

            print('\n===============> running l2bin binary for sst <==================')
            print('max qual level used = 2    |i.e., exclude -1 = missing and 3, 4 = bad qual...\n')
            call(['l2bin',
                  'infile='  + filelist[j],
                  'ofile='   + l2bin_filelist[j],
                  'l3bprod=' + product,
                  'resolution=' + str(space_res).strip(),
                  'prodtype=' + 'regional',
                  'flaguse=' + 'LAND,HISOLZEN',
                  'qual_prod=' + 'qual_sst',
                  'qual_max=' + '2'])
# ===============================================================



# make ascii file of bl2 files --  ?? THIS LIST WILL CONTAIN B12 FILES TO BE TEMPORALLY AVERAGED
# NOTE: fileslist contains a list of l2bin files genreated in previous call to bl2_gem.
#
# SUBROUTINE ...
# ===============================================================
def ascii_gen(bl2dir, filelist):

    ascii_file_list = bl2dir + '/' + 'ascii_bl2_list.txt'

    f = open(ascii_file_list, 'w')
    for file in filelist:
        if os.path.exists(file):
            f.write(file + '\n')

    f.close()

    return ascii_file_list
# ===============================================================




# make bl3 files (l3bin)
# NOTE: ascii_file_list is a variable name for bl2_dir/ascii_bl2_list.txt
#
# SUBROUTINE ...
# ===============================================================
def bl3_gen(ascii_file_list, input_coords, bl3_fname):
    print('\n====> running l3bin binary <=======\n')
    print('ascii_list is : ', ascii_file_list)

    print('Does file exist?')
    print(os.path.exists(ascii_file_list))

    if not os.path.exists(os.path.dirname(bl3_fname)):
        os.makedirs(os.path.dirname(bl3_fname))

    print('\nbl3_fname --->  ', bl3_fname, '\n')

    call(['l3bin',
        'ifile=' + ascii_file_list,
        'ofile=' + bl3_fname,
        'noext='    + '1'])

    os.remove(ascii_file_list)
# ===============================================================




# make mapped files from l3bin files
#
# SUBROUTINE ...
# ===============================================================
def l3map_gen(product_str,  bl3_fname, out_file, smi_proj, space_res, input_coords):

    print('\n====> running l3mapgen binary <=======')


    if not os.path.exists(os.path.dirname(out_file)):
        os.makedirs(os.path.dirname(out_file))

    north= float(input_coords.north)
    west=  float(input_coords.west)
    south= float(input_coords.south)
    east=  float(input_coords.east)

    l3map_resolution= convert_l2binres_2_l3mapres(space_res)
    lat_center, lon_center =  compute_cntr_latlon(south,west,north,east)

    slat_center=str(lat_center).strip()
    slon_center=str(lon_center).strip()

    test_clat= south + (north-south)/2.0
    stest_clat=str(test_clat).strip()

    if smi_proj == 'platecarree': proj4_cmd_prefix=  '+proj=eqc +lon_0=' + slon_center
    if smi_proj == 'mollweide':   proj4_cmd_prefix=  '+proj=moll +lon_0=' + slon_center
    if smi_proj == 'lambert': proj4_cmd_prefix=      '+proj=lcc +lon_0=' + slon_center
    if smi_proj == 'albersconic': proj4_cmd_prefix=  '+proj=aea +lon_0=' + slon_center + ' +lat_0=' + stest_clat

    proj4_cmd_suffix= ' +x_0=0 +y_0=0 +a=6378137 +b=6378137 +units=m'
    proj4_cmd= proj4_cmd_prefix + proj4_cmd_suffix


    print('Projection --------------> ',   smi_proj)
    print('East-West -------------->  ',   str(input_coords.east).strip(), '   ', str(input_coords.west).strip())
    print('Longitude Center ------->  ',   str(lon_center).strip())

    print('\nbl3_fname --------------->  ', bl3_fname)
    print('out_fname --------------->  ',   out_file)
    print('mapping resolution is --->  ',   l3map_resolution)
    print('product_str is ---------->  ',   product_str, '\n\n\n')

    call(['l3mapgen',
          'ifile=' + bl3_fname,
          'ofile=' + out_file,
           'product=' + product_str,
          'deflate=' + '4',
          'scale_type=' + 'linear',
          'projection='  + 'platecarree',
          'resolution=' + l3map_resolution,
          'interp=' + 'nearest',
          'west=' + str(input_coords.west).strip(),
          'east=' + str(input_coords.east).strip(),
          'north=' + str(input_coords.north).strip(),
          'south=' + str(input_coords.south).strip()])

    if os.path.exists(out_file):
        print('\nwrote file:', out_file)
    else: print('\ncould not generate l3mapgen file!!!')
# ===============================================================




# create png file with coastlines from an mapped (.nc) file using mapplotlib's basemap
#
# SUBROUTINE ...
# ===============================================================
def png_gen(ifile, png_dir, product, meas_names, mappping_approach):    # ifile is the mapped nc file. png_dir not yet created.

    print('\n====> running png_gen <=======\n')
    print('product for which png is being made...  ', product, '\n')

    if product == 'chl_ocx':

        # In going from l3bin to l3mapgen output, seadas (internal to l3mapgen' converts the output
        # product name from chl_ocx to either chl_oc3 (modis) or chl_oc4 (seadas). This next chunk of
        # code changes the product name from chl_ocx to the new name that l3mapgen made when outputting
        # this product to the mapped.nc file...
        # ---
        print('\nNOTE --> encountered product -- chl_ocx --')
        print('         converting this product name to either chl_oc3 or chl_oc4 for modis or seawifs files...\n')

        l3mapgen_prod_list= get_l3mapgen_prod_list(ifile)

        print('         list of variables found in the mapped.nc file --> ', l3mapgen_prod_list)

        if 'chl_oc3'in l3mapgen_prod_list:
            product= 'chl_oc3'
        if 'chl_oc4'in l3mapgen_prod_list:
            product= 'chl_oc4'

        print('         png prod name converted from chl_ocx to --> ', product,  '\n')


    if mappping_approach == 'binmap':
        prod_img = asarray(read_hdf_prod(ifile, product))            #read -smi.nc file
        scale_factor,add_offset= get_l3mapgen_slope_intercept(ifile, product)
        prod_img= scale_factor*prod_img + add_offset

    if mappping_approach == 'str_map': prod_img = asarray(read_hdf_prod(ifile, product + '-mean'))  #read -map.nc file


    bad_locations = where(asarray(prod_img) == nan)
    if bad_locations[0] != -1:
        prod_img[bad_locations] = -32767.0


    if mappping_approach == 'binmap'  : proj_name = get_smi_projection(ifile)
    if mappping_approach == 'str_map' : proj_name = read_hdf_prod(ifile, 'map_projection')[0]

    print('\n\n\nread hdf product type===> ', type(proj_name))

    if mappping_approach == 'binmap'  : extracted_coords = get_hdf_latlon(ifile)

    if mappping_approach == 'str_map' :
        map_bounds =  read_hdf_prod(ifile, 'map_bounds_swne')
        extracted_coords = map_coords.map_coords()
        extracted_coords.south= map_bounds[0]
        extracted_coords.west=  map_bounds[1]
        extracted_coords.north= map_bounds[2]
        extracted_coords.east=  map_bounds[3]


    if not os.path.exists(png_dir):
        os.makedirs(png_dir)
    png_ofile = png_dir + '/' + os.path.basename(ifile)[:-7] + '.png'


    write_png_with_basemap(png_ofile, prod_img, product, extracted_coords, proj_name)

    if os.path.exists(png_ofile):
        print('\nwrote file ', png_ofile, '\n\n')
    else: print('could not generate png!!!')
# ===============================================================




def png_gen_pace_true_color(ifile, png_dir):

    if not os.path.exists(png_dir):
        os.makedirs(png_dir)
    png_ofile = png_dir + '/' + os.path.basename(ifile)[:-7] + '.true_color.png'


    #-------------------------------------------------------------------------------

    product= 'Rrs_630'
    lambda_r= read_hdf_prod(ifile,product)
    bad_loctions=np.where(lambda_r == -32767)
    slope_intercept= get_l3mapgen_slope_intercept(ifile, product)
    lambda_r= lambda_r*slope_intercept[0] + slope_intercept[1]
    lambda_r[bad_loctions]= np.nan

    product='Rrs_533'
    lambda_g= read_hdf_prod(ifile,product)
    bad_loctions=np.where(lambda_g ==-32767)
    slope_intercept= get_l3mapgen_slope_intercept(ifile, product)
    lambda_g= lambda_g*slope_intercept[0] + slope_intercept[1]
    lambda_g[bad_loctions]= np.nan

    product='Rrs_465'
    lambda_b= read_hdf_prod(ifile,product)
    bad_loctions=np.where(lambda_b ==-32767)
    slope_intercept= get_l3mapgen_slope_intercept(ifile, product)
    lambda_b= lambda_b*slope_intercept[0] + slope_intercept[1]
    lambda_b[bad_loctions]= np.nan

    # ------------------------------------------------------------------------------

    img_size= lambda_r.shape
    row_size=img_size[0]
    col_size=img_size[1]

    rgbArray = np.zeros((row_size,col_size,3),dtype=np.float32)
    rgbArray[:,:, 0] =  lambda_r
    rgbArray[:,:, 1] =  lambda_g
    rgbArray[:,:, 2] =  lambda_b
    rgbArray=  255*(rgbArray-np.nanmin(rgbArray))/(np.nanmax(rgbArray)-np.nanmin(rgbArray))

    r= Image.fromarray(rgbArray[:,:, 0]).convert("L")
    g=Image.fromarray(rgbArray[:,:, 1]).convert("L")
    b=Image.fromarray(rgbArray[:,:, 2]).convert("L")

    img= Image.merge("RGB", (r,g,b))

    converter= ImageEnhance.Color(img)
    new_img= converter.enhance(3.5)

    converter= ImageEnhance.Brightness(new_img)
    new_img= converter.enhance(1.5)

    # ------------------------------------------------------------------------------

    extracted_coords = get_hdf_latlon(ifile)
    north= float(extracted_coords.north)
    west=  float(extracted_coords.west)
    south= float(extracted_coords.south)
    east=  float(extracted_coords.east)
    map_data_extent=[west, east, south, north]
    lon_ctr=0.0

    ax= plt.axes(projection=ccrs.PlateCarree(central_longitude=lon_ctr))
    ax.set_extent(map_data_extent, crs=ccrs.PlateCarree())

    # Fill continents with gray and use black for edge (coastline)...
    # ---
    feature = cartopy.feature.NaturalEarthFeature(name='land', category='physical', scale='10m',\
    edgecolor='k', facecolor='gray')
    ax.add_feature(feature)

    # Set up Lat/Lon Labels...
    # ---
    meridians = np.arange(west, east,2.)
    parallels = np.arange(south, north,2.)
    # ---
    ax.set_xticks(meridians, crs=ccrs.PlateCarree())
    ax.set_yticks(parallels, crs=ccrs.PlateCarree())
    # ---
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    # ---
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    # ---

    sat_img= ax.imshow(new_img, transform=ccrs.PlateCarree(), extent=map_data_extent)

    # Save the mapped images as a png file…
    plt.savefig(png_ofile, bbox_inches='tight', dpi=600)

    if os.path.exists(png_ofile):
        print('\nwrote file ', png_ofile, '\n\n')
    else: print('could not generate png!!!')

    # Close plotting function and clear all plotting settings…
    plt.close()









#
# for bin mapping... l2bin each L2 file of a given averging time range ==>
# make and ascii file with the list of binned files ==> l3bin ==> l3mapgen ==> png
# or for straigt mapped... map and then average for given time range ==> png
#
# NOTE: filelist == the list of just OC files or a list of just SST files.
#       time_period will be just 'WKY' or just 'WKY' or just 'MON'
#       sat_type will be the senor name (e.g., SEAWIFS or MODIS etc.)
#       chk will be -----
#       products will be a list of L2 products to map.  In the case that that L2 file
#       are PACE AOP files (and only in this case) products will come into the process
#       subroutine as 'all'. So, products = 'all' triggers a difference sort of processing
#       where all products (all hyperspectral wavelenghts) end up in the same file. In all
#       other cases, a separte map file is made for each invidual product.
# -----------------------------------------------------------------------------------
def process(filelist, time_period, out_dir, products, named_flags_2check, space_res, input_coords, sat_type, year, stats_yesno, smi_proj, mappping_approach):

    print('\n\nMAPPING APPROACH ----> ', mappping_approach)

    if time_period == 'DLY':
        ave_dir = 'daily'
    elif time_period == 'WKY':
        ave_dir = 'weekly'
    elif time_period == 'MON':
        ave_dir = 'monthly'

    # make sub directories to store temporary l2bin and l3bin files...
    # ---
    temp = os.path.dirname(filelist[0])
    l2bin_dir = temp + '/l2bin'
    l3bin_dir = temp + '/l3bin'

    # the variable meas_vec is used sequentially by l2bin, l3bin to
    # compute mean, std and nops
    # ---
    if stats_yesno == 'yes'and time_period != 'DLY':
        meas_vec = ['1', '2', '4']
        meas_names = ['mean', 'variance', 'npoints']
    else:
        meas_vec = ['1']
        meas_names = ['mean']


    # The "get_averages" function takes in the full list of L2 file that are
    # just color or just sst or just hires that were in the orginal l2dir.
    #
    # averages function returns a LIST OF TUPLES. each tuple in the list
    # has 2 elements == ([start, end]-for output l3 filename and a filenames
    # that will go into the a give ave period [file1, file2, file3...]
    #
    # file_group[0]= [start, end]=  [YYYYMMDDYYYYMMDD, YYYYMMDDYYYYMMDD]
    # file_group[1]= [file1, file2,...]
    # ---------------------------------------------------------------------------------

    averages = get_average(filelist, time_period, int(year))

    for file_group in averages:       # cycle through each tuple of averaging dates and filesname sets
                                      # recall: file_group[0]= [start, end] and file_group[1]= [file1, file2,...]

        for prod in products:         # for each averaging period and list of file , cycle through the list of prod to be mapped
                                      # note: in the case of PACE AOP, the product has been named ['all'] - just one "product"

            #-----------------------------------------------------------------------------
            if mappping_approach == 'binmap':
            #-----------------------------------------------------------------------------

                print('PROCESSING L2 to L3 USING L2bin, L3bin -> L3MAPGEN + PNG...\n')

                #  Create l2bin file names...
                #  Note filelist basename of the form: MISSION_INSTRUMENT_TYPE.YYYYMMDDTHHMMSS.prod.nc
                #  So, name.split('.')[0] + '.' + name.split('.')[1] + '.bl2bin'=  MISSION_INSTRUMENT_TYPE.YYYYMMDDTHHMMSS.bl2bin
                #  file_group[1] == list of files a given averaging period
                # ---
                l2_basename= [os.path.basename(name) for name in file_group[1]]
                l2bin_filelist= [l2bin_dir + '/' + name.split('.')[0] + '.' + name.split('.')[1] + '.bl2bin' for name in l2_basename]


                # [1]  Compute l2bin files for a group of L2 files, where group are L2 files within a
                #      specific averaging interval (DLY, WKY, MON)
                #      file_group[0] == the [start, stop] jday for the averaging period.
                #      file_group[1] == list of files a given averaging period
                # ---
                if prod == 'all':
                    print('\n\nabout to call l2bin and getting all prod...\n\n')
                    prod_list_array= get_product_list(file_group[1][0], ['all']) # file_group[1] is the list of L2 files in a given avg period.

                    prefix= asarray([name.split('_')[0] for name in prod_list_array])
                    good_index= where(prefix == 'Rrs')
                    prod_list_array=prod_list_array[good_index]   # create an tmp array with just Rrs products <------------<<<<<<<



                    prod_list_array= prod_list_array[15:140]  # <-----<<<  2bin and mapgen both use these products.
                                                             # <-----<<<  as of 4-20-2023 having more than 128 bands thows an error.
                                                             # <-----<<<  remove this line when the seadas bug is finally resolved.


                    prod_long = ",".join(prod_list_array)  # Turn array into a long string of comma separated products

                    bl2_gen(file_group[1], l2bin_dir, l2bin_filelist, prod_long, named_flags_2check, space_res)

                else: bl2_gen(file_group[1], l2bin_dir, l2bin_filelist, prod, named_flags_2check, space_res)


                # [2]  make an ascii text file containing the list of l2bin files created above.
                # ---
                ascii_file_list = ascii_gen(l2bin_dir, l2bin_filelist)


                # [3]  make bl3 files--- one single file for each file_group == time averging period...
                #      Note: ascii_file_list contains a list of l2bin files for a given averaging time
                #      interval
                # ---
                avg_period_basename= file_group[0][0] + file_group[0][1]  # file_group[0]= [start, end]=  [YYYYMMDDYYYYMMDD, YYYYMMDDYYYYMMDD]
                l3bin_file = l3bin_dir + '/' + avg_period_basename + '.bl3bin'
                bl3_gen(ascii_file_list, input_coords, l3bin_file)


                # [4]   map the resulting l3bin file (i.e., the time averaged file DLY, WKY, MON)
                #      using l3mapgen
                # ---

                # the variable meas_vec is used sequentially by l2bin, l3bin to
                # compute mean, std and nops
                # ---
                if stats_yesno == 'no' or time_period == 'DLY':

                    if prod != 'all':
                        smi_output_dir = out_dir + '/' + ave_dir + '/' + prod + '/' + 'mean'
                        smi_output_file = smi_output_dir + '/' +  file_group[0][0] + file_group[0][1] + '.' + prod +'-' + 'mean' + '.smi.nc'
                        prod_str= prod + ':avg'

                    if prod == 'all':
                        smi_output_dir = out_dir + '/' + ave_dir + '/' + 'AOP' + '/' + 'mean'
                        smi_output_file = smi_output_dir + '/' +  file_group[0][0] + file_group[0][1] + '.' + 'AOP' +'-' + 'mean' + '.smi.nc'

                        prod_list_array= get_product_list(file_group[1][0], ['all']) # file_group[1] is the list of L2 files in a given avg period.

                        prefix= asarray([name.split('_')[0] for name in prod_list_array])
                        good_index= where(prefix == 'Rrs')
                        prod_list_array= prod_list_array[good_index]      # create an tmp array with just Rrs products <-------<<<



                        prod_list_array= prod_list_array[15:140]  # <-----<<<  2bin and mapgen both use these products.
                                                                 # <-----<<<  as of 4-20-2023 having more than 128 bands thows an error.
                                                                 # <-----<<<  remove this line when the seadas bug is finally resolved.


                        prod_list_array= char.add(prod_list_array,':avg')
                        prod_str = ",".join(prod_list_array)              # Turn array into a long string of comma separated products



                if stats_yesno == 'yes'and time_period != 'DLY':

                    if prod != 'all':
                        smi_output_dir = out_dir + '/' + ave_dir + '/' + prod + '/' + 'stats'
                        smi_output_file = smi_output_dir + '/' +  file_group[0][0] + file_group[0][1] + '.' + prod +'-' + 'stats' + '.smi.nc'
                        prod_str= prod + ':avg' + ',' +  prod + ':var' ',' + prod + ':nobs'

                    if prod == 'all':
                        smi_output_dir = out_dir + '/' + ave_dir + '/' + 'AOP' + '/' + 'stats'
                        smi_output_file = smi_output_dir + '/' +  file_group[0][0] + file_group[0][1] + '.' + 'AOP' +'-' + 'stats' + '.smi.nc'

                        prod_list_array= get_product_list(file_group[1][0], ['all']) # file_group[1] is the list of L2 files in a given avg period.

                        prefix= asarray([name.split('_')[0] for name in prod_list_array])
                        good_index= where(prefix == 'Rrs')
                        prod_list_array= prod_list_array[good_index]      # create an tmp array with just Rrs products <------------<<<<<<<

                        prod_list_array_avg= char.add(prod_list_array,':avg')
                        prod_list_array_nobs= char.add(prod_list_array,':nobs')
                        prod_list_array_var= char.add(prod_list_array,':var')

                        prod_list_array= concatenate([prod_list_array_avg,prod_list_array_nobs,prod_list_array_var])

                        prod_str = ",".join(prod_list_array)    # Turn array into a long string of comma separated products


                if os.path.exists(l3bin_file):
                    l3map_gen(prod_str, l3bin_file, smi_output_file, smi_proj, space_res, input_coords)


                if os.path.exists(smi_output_file) and prod != 'all':
                    png_gen(smi_output_file, smi_output_dir+'/png', prod, 'mean', mappping_approach)


                if os.path.exists(smi_output_file) and prod == 'all':
                    png_gen_pace_true_color(smi_output_file, smi_output_dir+'/png')


            #-----------------------------------------------------------------------------
            if mappping_approach == 'str_map':
            #-----------------------------------------------------------------------------

                print('PROCESSING L2 to L3 USING pyresample.py TO MAP SWATH DATA + PNG...\n')


                if prod != 'all': map_output_dir = out_dir + '/' + ave_dir + '/' + space_res +'m' + '-' + prod + '/' + 'mean'
                if prod == 'all': map_output_dir = out_dir + '/' + ave_dir + '/' + space_res +'m' + '-' + 'AOP' + '/' + 'mean'
                if not os.path.exists(map_output_dir): os.makedirs(map_output_dir)


                map_basename=  file_group[0][0] + file_group[0][1]
                if prod != 'all': map_output_file= map_output_dir + '/' + map_basename + '.' + time_period + '.' + prod + '.map.nc'
                if prod == 'all': map_output_file= map_output_dir + '/' + map_basename + '.' + time_period + '.' + 'AOP' + '.map.nc'
                str_map_gen(file_group[1], map_output_file, prod, smi_proj, input_coords, space_res, named_flags_2check, stats_yesno)


                if os.path.exists(map_output_file):
                    png_gen(map_output_file, map_output_dir+'/png', prod, meas_names[0], mappping_approach)

    # clean up temporary files...
    if mappping_approach == 'binmap':
        shutil.rmtree(l2bin_dir)
        shutil.rmtree(l3bin_dir)
# ===============================================================




#  --- This subroutine gathers a list of the L2 files names from a given l2dir
#
#
#
# SUBROUTINE ...
# ===============================================================
def setup(l2dir, smi_proj, latlon, stats_yesno, color_flags_to_check, sst_flags_to_check):


    # --- Untar and Uncompress and Get List of L2 Files
    #---------------------------------------------------------------------------
    if len(glob.glob(l2dir + '/*.tar')) != 0: untar_ocweb(l2dir)

    while any([is_compressed(fi) for fi in glob.glob(l2dir + '/*')]):
        for fi in glob.glob(l2dir + '/*'): decompress_file(fi)
    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    filelist = asarray(glob.glob(l2dir + '/*L2*'))
    filelist= sort(filelist)

    if len(filelist) == 0:
        print('\n########### PROGRAM batch_binmap.pro HALTED BECAUSE NO L2 FILES FOUND IN THE    #########')
        print('########### SPECIFIED L2DIR. PLEASE GO BACK AND RECHECK THE DIRECTORY PATH THAT #########')
        print('########### WAS SPECIFIED IN THE BATCH_CMD_BINMAP FILE.                         #########\n')
        sys.exit()

    print('\nL2 to L3 processing started...')
    print('total number of files found= ', len(filelist), '\n')
    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    input_coords = map_coords.map_coords()
    if latlon[0] == 'whole':
        input_coords = get_hdf_latlon(filelist[0])
    else:
        input_coords.north = latlon[2]
        input_coords.south = latlon[0]
        input_coords.east = latlon[3]
        input_coords.west = latlon[1]
    #---------------------------------------------------------------------------



    # Extract Year from File Name and check for unique years in the input directory...
    #--------------------------------------------------------------------------------
    root = [os.path.basename(name) for name in filelist]

    l2fname_new_convention= [fname_new_from_old(name) for name in root]

    syear= [name.split('.')[1][0:4] for name in l2fname_new_convention]
    year= int(syear[0])   # just defined 'year' as the first year in this list...
    uniq_syear = unique(syear) #sorted list of unique years

    if len(uniq_syear) > 1:
        print('##### PROGRAM HALTED BECAUSE L2DIR CONTAINS FILES FROM SEPARATE YEARS ####')
        print('##### PLEASE GO BACK AND PARSE L2 FILE INTO SEPARTE UNIQUE YEARS      ####')
        sys.exit()
    print('year -----> ', year)
    #---------------------------------------------------------------------------




    # --- Check for presence of standard resolution (1 km) Level 2 "SST" or "OC" files
    # --- And/Or HiRes OC files. The sst_chk, color_chk, hkm_chk and qkm_chl will be
    # --- vectors filled with ones and zeros (i.e., TRUE or FALSE) for each file name
    # === in the filelist that came from the l2dir.
    #---------------------------------------------------------------------------
    sst_chk =   ['SST' in name for name in root]
    color_chk = ['OC'  in name and 'HKM' not in name and 'QKM' not in name for name in root]
    hkm_chk=    ['HKM' in name for name in root]
    qkm_chk=    ['QKM' in name for name in root]
    #---------------------------------------------------------------------------



    # --- get l2_flags to check
    #---------------------------------------------------------------------------
    mission_instrument_name= [name.split('.')[0] for name in l2fname_new_convention]
    instrument_name= [name.split('_')[1] for name in mission_instrument_name]

    if color_flags_to_check == 'standard':
        color_named_flags_2check = get_sds7_default_l2flags(instrument_name[0], 'color')
    else: color_named_flags_2check = color_flags_to_check

    if sst_flags_to_check == 'standard' and (instrument_name[0]  == 'MODIS' or instrument_name[0]  == 'VIIRS'):
        print('\n', instrument_name[0], 'sst', '\n')
        sst_named_flags_2check = get_sds7_default_l2flags(instrument_name[0], 'sst')
    else: sst_named_flags_2check=sst_flags_to_check
    #---------------------------------------------------------------------------


    return color_chk, sst_chk, hkm_chk, qkm_chk, color_named_flags_2check, sst_named_flags_2check, instrument_name[0], filelist, input_coords, year




# =============================================================================
# MAIN PROGRAM ...
# =============================================================================

def batch_proc_L23(l2dir, output_dir, products, space_res, time_period, color_flags_to_check, sst_flags_to_check, latlon, smi_proj, stats_yesno, straight_map):


    products = products.split(',')          #split string to make a list ['chlor'_a,'sst',...]
    latlon = latlon.split(',')              #split string to make a list ['S','W','N,'E']
    time_period = time_period.split(',')    #split string to make a list ['DLY','WKY','MON']


    # --- get rid of bad average values, i.e. only keep 'DLY', 'WKY', 'MON'
    def f(x): return (x == 'DLY' or x == 'WKY' or x == 'MON')
    time_period = list(filter(f, time_period)) #cut empty groups

    # --- make sure directories are right (/ and ~)
    l2dir = path_reformat(l2dir)
    output_dir = path_reformat(output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


    #sometimes when the batch_L23 program crashes before completion it leves behind the
    #temporary l2bin ad l3bin files.  The next lines insure that they are remove upfront...
    # ------------------------------------------------------------------------------------------
    if os.path.exists(l2dir + '/l2bin'):
        shutil.rmtree(l2dir + '/l2bin')
    if os.path.exists(l2dir + '/l3bin'):
        shutil.rmtree(l2dir + '/l3bin')
    #------------------------------------------------------------------------------------------



    # --- Set up some processing information based on the files that will be
    # --- found in the given l2dir. The setup function returns ###_chk vectors
    # --- with ones and zeros (TRUE and FALSE) for each file found on l2dir.
    # --- Also returned are the instrument name (sat_type)(eg. SEAWIFS or MODIS etc.).
    # --- Also returned are the named l2flags that will be checked with processing
    # --- from L2 to L3. And Finally, it returns a list of the L2 files found in the l2dir.
    #-------------------------------------------------------------------------------------------
    color_chk, sst_chk, hkm_chk, qkm_chk, color_named_flags_2check, sst_named_flags_2check, sat_type, filelist, input_coords, year \
        = setup(l2dir, smi_proj, latlon, stats_yesno, color_flags_to_check, sst_flags_to_check)
    #-------------------------------------------------------------------------------------------




    # Get SEPARATE FILE NAME LISTS of file names for: 1) standard color files (1km OC files)
    # and 2) standard SST files (1km SST) and 3) HiRES files
    #------------------------------------------------------------------------------------------

    # COLOR - standard resolution
    color_file_indices = where( asarray(color_chk)==True )  #This will only be True for none hires sensors/products (SeaWiFS, MODIS, VIIRS)
    if len(filelist[color_file_indices]) != 0:
        color_files = list(asarray(filelist)[color_file_indices])
        color_prod = get_product_list(color_files[0], products)  #color_files and color_prod are for 1km color products (SeaWiFS, MODIS, VIIRS).


        if len(color_prod) > 50: color_prod = ['all']       # if the files is a PACE AOP L2 file or an L2 file genrated from L1 to L2 Batch_Proc,    <=============<<<<<
                                                            # then it will have all the Rrs_nnn parmaters in the L2 file. set to 'all' to inform
                                                            # later subroutinnote calls that it is a PACE file with with all Rrs parameters.
                                                            # needing to be mapped into a single file and then later a single true color png should
                                                            # be made for that file.
                                                            # Used > 50 prod because only Pace with full set of Rrs will have so many products in one file.

    # SST - standard resolution
    sst_file_indices = where( asarray(sst_chk)==True )
    if len(filelist[sst_file_indices]) != 0:
        sst_files = list(asarray(filelist)[sst_file_indices])
        sst_prod = ['sst']



    # HIRES modis color
    hkm_color_file_indices = where( asarray(hkm_chk)==True )
    if len(filelist[hkm_color_file_indices]) != 0:
        hkm_color_files = list(asarray(filelist)[hkm_color_file_indices])
        hkm_color_prod = get_product_list(hkm_color_files[0], ['all'])

    qkm_color_file_indices = where( asarray(qkm_chk)==True )
    if len(filelist[qkm_color_file_indices]) != 0:
        qkm_color_files = list(asarray(filelist)[qkm_color_file_indices])
        qkm_color_prod = get_product_list(qkm_color_files[0], ['all'])
    #-------------------------------------------------------------------------------------------




    # create mapped output for each average period specified (DLY or WKY or MON)
    # Typically time_period will be just ['DLY'] or just ['WKY'] or just ['MON'],
    # But it would be possible to have all three ['DLY','WKY', 'MON'].
    #------------------------------------------------------------------------------------------
    for average in time_period:


        # map any standad resoluton color and sst files ...
        #------------------------------------------------------------------------------------------
         if len(filelist[color_file_indices]) != 0:
              if straight_map == 'no':
                  mappping_approach= 'binmap'
                  proc_space_res= space_res    #space_res is the resoluton for standard l2 binning set in Batch_Proc.py
                  process(color_files, average, output_dir, color_prod, color_named_flags_2check, \
                          proc_space_res, input_coords, sat_type, year, stats_yesno, smi_proj, mappping_approach)

              if straight_map == 'yes':
                  mappping_approach= 'str_map'
                  proc_space_res = str(int(resolution_from_sat_fname(color_files[0])))
                  process(color_files, average, output_dir, color_prod, color_named_flags_2check, \
                          proc_space_res, input_coords, sat_type, year, stats_yesno, smi_proj, mappping_approach)



         if len(filelist[sst_file_indices]) != 0:
             if straight_map == 'no':
                mappping_approach= 'binmap'
                proc_space_res= space_res    #space_res is the resoluton for standard l2 binning set in Batch_Proc.py
                process(sst_files, average, output_dir, sst_prod, sst_named_flags_2check, \
                        proc_space_res, input_coords, sat_type, year, stats_yesno, smi_proj, mappping_approach)

             if straight_map == 'yes':
                mappping_approach= 'str_map'
                proc_space_res = str(int(resolution_from_sat_fname(sst_files[0])))
                process(sst_files, average, output_dir, sst_prod, sst_named_flags_2check, \
                        proc_space_res, input_coords, sat_type, year, stats_yesno, smi_proj, mappping_approach)
        #------------------------------------------------------------------------------------------


        # map any modis hires color files
        #------------------------------------------------------------------------------------------
         if len(filelist[hkm_color_file_indices]) != 0:
              if straight_map == 'no':
                  mappping_approach= 'binmap'
                  proc_space_res= space_res    #space_res is the resoluton for standard l2 binning set in Batch_Proc.py
                  process(hkm_color_files, average, output_dir, hkm_color_prod, color_named_flags_2check, \
                          proc_space_res, input_coords, sat_type, year, stats_yesno, smi_proj, mappping_approach)

              if straight_map == 'yes':
                  mappping_approach= 'str_map'
                  proc_space_res = str(int(resolution_from_sat_fname(hkm_color_files[0])))
                  process(hkm_color_files, average, output_dir, hkm_color_prod, color_named_flags_2check, \
                          proc_space_res, input_coords, sat_type, year, stats_yesno, smi_proj, mappping_approach)


         if len(filelist[qkm_color_file_indices]) != 0:
              if straight_map == 'no':
                  mappping_approach= 'binmap'
                  proc_space_res= space_res    #space_res is the resoluton for standard l2 binning set in Batch_Proc.py
                  process(qkm_color_files, average, output_dir, qkm_color_prod, color_named_flags_2check, \
                          proc_space_res, input_coords, sat_type, year, stats_yesno, smi_proj, mappping_approach)

              if straight_map == 'yes':
                  mappping_approach= 'str_map'
                  proc_space_res = str(int(resolution_from_sat_fname(qkm_color_files[0])))
                  process(qkm_color_files, average, output_dir, qkm_color_prod, color_named_flags_2check, \
                          proc_space_res, input_coords, sat_type, year, stats_yesno, smi_proj, mappping_approach)
        #------------------------------------------------------------------------------------------
