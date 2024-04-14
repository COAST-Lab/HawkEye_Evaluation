from subprocess import call
import os
def create_tif_vrt(
        file_path, nc_format, nc_variable, tif_path, variable, vrt_path, clip_shp, overwrite=True):

    if overwrite:
        if nc_variable is None:
            nc_variable = '//geophysical_data/{}'.format(variable)
        gdal_trans = 'gdal_translate -r cubic -of VRT ' \
                     ' -unscale -a_nodata -32767.0 -ot Float32 -a_srs EPSG:4326 ' \
                     ' {}:"{}":{}  ' \
                     '"{}"'.format(nc_format, file_path, nc_variable, vrt_path)

        call(gdal_trans, shell=True)
        if variable == 'sss':
            tps = ''
        else:
            tps = '-tps'

        gdal_wrap = 'gdalwarp -of GTIFF {} -q -overwrite -multi -wo NUM_THREADS=ALL_CPUS -ot Float32 -wo NUM_THREADS=ALL_CPUS -cutline "{}" -crop_to_cutline ' \
                    '-dstalpha "{}"  "{}"'.format(tps, clip_shp, vrt_path, tif_path)

        call(gdal_wrap, shell=True)

    else:

        if nc_variable is None:
            nc_variable = '//geophysical_data/{}'.format(variable)
        if not os.path.isfile(vrt_path):
            gdal_trans = 'gdal_translate -r cubic -of VRT ' \
                         ' -unscale -a_nodata -32767.0 -ot Float32 -a_srs EPSG:4326 ' \
                         ' {}:"{}":{}  ' \
                         '"{}"'.format(nc_format, file_path, nc_variable,
                                       vrt_path)

            call(gdal_trans, shell=True)

        if not os.path.isfile(tif_path.replace('000', '00')):

            if variable == 'sss':
                tps = ''
            else:
                tps = '-tps'

            gdal_wrap = 'gdalwarp -of GTIFF {} -q  -multi -ot Float32 -wo NUM_THREADS=ALL_CPUS -cutline "{}" -crop_to_cutline ' \
                        '-dstalpha "{}"  "{}"'.format(tps, clip_shp,
                                                      vrt_path, tif_path)

            call(gdal_wrap, shell=True)


def create_tif(
        file_path, nc_format, nc_variable, tif_path, variable, overwrite=True):

    if overwrite:
        if nc_variable is None:
            nc_variable = '//geophysical_data/{}'.format(variable)
        gdal_trans = 'gdal_translate -r cubic -of GTIFF ' \
                     ' -unscale -a_nodata -32767.0 -ot Float32 -a_srs EPSG:4326 ' \
                     ' {}:"{}":{}  ' \
                     '"{}"'.format(nc_format, file_path, nc_variable, tif_path)

        call(gdal_trans, shell=True)


    else:

        if nc_variable is None:
            nc_variable = '//geophysical_data/{}'.format(variable)
        if not os.path.isfile(tif_path):
            gdal_trans = 'gdal_translate -r cubic -of GTIFF ' \
                         ' -unscale -a_nodata -32767.0 -ot Float32 -a_srs EPSG:4326 ' \
                         ' {}:"{}":{}  ' \
                         '"{}"'.format(nc_format, file_path, nc_variable,
                                       tif_path)

            call(gdal_trans, shell=True)
