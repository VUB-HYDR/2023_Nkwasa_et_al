'''

this script generates the N/P balance maps and sediment yield on annual basis  - hru or bsn scale

Author  : albert nkwasa
Contact : albert.nkwasa@vub.be
Date    : 2023.01.10


'''
import os
import pandas as pd
import geopandas as gpd
import numpy as np
import csv
import sys
from osgeo import gdal
import rasterio
from geocube.api.core import make_geocube
import warnings

warnings.filterwarnings("ignore")


scale = 'hru'
timestep = 'aa'
# path to TxTInOut folder
target_folder = ''

# #setting the working environment
working_dir = ''
os.chdir(working_dir)
if scale == 'hru':
    try:
        os.makedirs("results_graphs/nutrients_hru")
    except:
        pass


file_ls = '{}/hru_ls_{}.csv'.format(target_folder, timestep)
name_header_ls = ['jday', 'mon', 'day', 'yr', 'unit', 'gis_id', 'name', 'sedyld',
                  'sedorgn(kg/ha)', 'sedorgp(kg/ha)', 'surqno3(kg/ha)', 'lat3no3(kg/ha)', 'surqsolp(kg/ha)', 'usle', 'sedmin', 'tileno3', 'lchlabp', 'tilelabp', 'satexn']
df_ls = pd.read_csv(file_ls, names=name_header_ls, skiprows=3)
df_ls_n = df_ls.drop(['jday', 'mon', 'day', 'yr', 'unit', 'gis_id', 'name', 'sedyld',
                      'sedorgp(kg/ha)', 'surqsolp(kg/ha)', 'usle', 'sedmin', 'tileno3', 'lchlabp', 'tilelabp', 'satexn'], axis=1)


# path to hru shapefile
hru_shp_path = '{}/Watershed/Shapes/hrus1.shp'


# mapping the sediment yield
sed_yld = df_ls[['gis_id', 'sedyld']]
sed_dic = sed_yld.set_index('gis_id').T.to_dict('list')
value_list_sed = sed_dic['sedyld'].to_list()

# working with the HRU shapefile
gdf_sed = gpd.read_file(hru_shp_path)
gdf_sed = gdf_sed.drop(['Channel', 'Landscape', 'Landuse', 'SlopeBand',
                        'Soil', '%Landscape', 'LINKNO'], axis=1)
gdf_sed['sed_yld'] = value_list_sed

if scale == 'hru':
    path_file_sed = 'sed_yld.shp'
    gdf_sed.to_file(path_file_sed)
    # changing the projection and converting to a raster
    output_shp = 'test_{}.shp'
    os.system('ogr2ogr {} -t_srs "EPSG:4326" {}'.format(output_shp, path_file_sed))
    output_raster = 'sed_yld.tif'
    cube = make_geocube(vector_data=output_shp, measurements=[
        'sed_yld'], resolution=(0.25, -0.25), output_crs='epsg:4326', fill=-9999)  # 27.5km resolution--can be adjusted
    cube['sed_yld'].rio.to_raster(output_raster)
    os.remove('test.shp'), os.remove('test.dbf'), os.remove(
        'test.prj'), os.remove('test.shx')


print('\t >finished')
