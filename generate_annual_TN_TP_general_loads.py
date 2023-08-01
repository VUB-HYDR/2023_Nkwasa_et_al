# usr/bin/env-python3
'''

this script calaculates either TN or TP yearly loading

Author  : albert nkwasa
Contact : albert.nkwasa@vub.be
Date    : 2023.01.10

'''
import os
from osgeo import gdal
import pandas as pd
import datetime
import sys
import warnings
import math
# pylint: disable=unsubscriptable-object

warnings.filterwarnings("ignore")

# path to TxTInOut folder
target_folder = ''

# set working directory
working_dir = ''
os.chdir(working_dir)
try:
    os.makedirs("attr_yr")
except:
    pass
os.chdir('{}/attr_yr'.format(working_dir))


path_to_obs = ''  # path to the observation files
path_to_sim = '{}/channel_sd_yr.csv'.format(target_folder)

# lookup file for channel ID and corresponding GEMstat station
path_to_lookup = '/{}'.format('channel_lookup_attribution.csv')
cha_lookup = pd.read_csv(path_to_lookup)
cha_dic = cha_lookup.set_index('GRDC').T.to_dict('list')


for k in os.listdir(path_to_obs):
    os.chdir(path_to_obs)
    if k.endswith('.csv'):
        file_name = k.split()[-1].split('.')[0]
        for j in cha_dic:
            if j == file_name:
                cha_id = int(cha_dic[j][0])
                obs = pd.read_csv(k)
                obs['date'] = pd.DatetimeIndex(obs['date'])
                # obs_list = obs['flow (m3/s)'].to_list()

                start_date = obs['date'].iloc[0]
                end_date = obs['date'].iloc[-1]

                name_header = ["jday", "mon", "day", "yr", "unit", "gis_id", "name", "area", "precip", "evap", "seep", "flo_stor", "sed_stor", "orgn_stor", "sedp_stor", "no3_stor", "solp_stor", "chla_stor", "nh3_stor", "no2_stor", "cbod_stor", "dox_stor", "san_stor", "sil_stor", "cla_stor", "sag_stor", "lag_stor", "grv_stor", "null1", "flo_in", "sed_in", "orgn_in", "sedp_in",
                               "no3_in", "solp_in", "chla_in", "nh3_in", "no2_in", "cbod_in", "dox_in", "san_in", "sil_in", "cla_in", "sag_in", "lag_in", "grv_in", "null2", "flo_out", "sed_out", "orgn_out", "sedp_out", "no3_out", "solp_out", "chla_out", "nh3_out", "no2_out", "cbod_out", "dox_out", "san_out", "sil_out", "cla_out", "sag_out", "lag_out", "grv_out", "null3", "water_temp"]
                sim = pd.read_csv(path_to_sim,
                                  names=name_header, skiprows=3)
                sim = sim.drop(["jday",  "unit", "name", "area", "precip", "evap", "seep", "flo_stor", "sed_stor", "orgn_stor", "sedp_stor", "no3_stor", "solp_stor", "chla_stor", "nh3_stor", "no2_stor", "cbod_stor", "dox_stor", "san_stor", "sil_stor", "cla_stor", "sag_stor", "lag_stor", "grv_stor", "null1", "flo_in", "sed_in", "orgn_in", "sedp_in",
                                "no3_in", "solp_in", "chla_in", "nh3_in", "no2_in", "cbod_in", "dox_in", "san_in", "sil_in", "cla_in", "sag_in", "lag_in", "grv_in", "null2", "sed_out", "sedp_out", "solp_out", "chla_out", "cbod_out", "dox_out", "san_out", "sil_out", "cla_out", "sag_out", "lag_out", "grv_out", "null3", "water_temp"], axis=1)

                sim['date'] = sim['mon'].map(str) + '-' + \
                    sim['day'].map(str) + '-' + sim['yr'].map(str)
                # sim["vol"] = sim["flo_out"]*(24*60*60)
                sim['tot_n'] = sim["orgn_out"] + sim["no3_out"] + \
                    sim["nh3_out"] + sim["no2_out"]
                # sim["flux"] = (sim["tot_n"] / sim["vol"]) * 1000
                sim["flux"] = sim['tot_n']
                sim = sim.drop(['mon', 'day', 'yr', 'flo_out', 'orgn_out',
                                'no3_out', 'nh3_out', 'no2_out', 'tot_n'], axis=1)
                sim['date'] = pd.DatetimeIndex(sim['date'])
                sim_cha_id = sim[sim['gis_id'] == cha_id]
                # if (sim_cha_id['date'] >= start_date) and (sim_cha_id['date'] <= end_date):

                mask = (sim_cha_id['date'] >= start_date) & (
                    sim_cha_id['date'] <= end_date)
                if mask.any() == True:
                    filtered = sim_cha_id.loc[mask]

                    # apply the filter to the observed file
                    start_date_sim = filtered['date'].iloc[0]
                    end_date_sim = filtered['date'].iloc[-1]
                    filtered_masked = obs.loc[(obs['date'] >= start_date_sim) & (
                        obs['date'] <= end_date_sim)]
                    # using units as flows so that we mantain the same files.
                    obs_list = filtered_masked['flow (m3/s)'].to_list()

                    # now combine the filtered dataframes
                    filtered['flux_obs'] = obs_list
                    # filtered = filtered[filtered['flux_obs'] > 0]
                    filtered = filtered.drop(['gis_id'], axis=1)
                    filtered = filtered.set_index('date')

                    filtered.loc[filtered['flux'] == math.inf, 'flux'] = 0.001
                    os.chdir(
                        '{}/attr_yr'.format(working_dir))
                    filtered.to_csv(
                        '{}_attr_yr.csv'.format(file_name), sep=',')
                else:
                    print('\t > No window time for station {}'.format(j))


print('\t > Finished')
