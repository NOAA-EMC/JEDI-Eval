from netCDF4 import Dataset
import sys
import numpy as np
import pandas as pd
import os
import ioda


class IODAstatistics:

    def __init__(self, ob_dict, variable, cycle, outdir):
        """
        Body of the constructor that saves some file sensative
        metadata.

        Args:
            ob_dict : (dict) observation dictionary from input yaml file
            variable : (str) variable name
            cycle : (str) cycle time
            outdir : (str) path to where stats will be saved
        """

        obsspace = ob_dict['obs space']
        self.obsname = obsspace['name']
        self.obsfile = os.path.basename(obsspace['obsdataout']['obsfile'])
        self.obspath = os.path.join(ob_dict['diag_dir'], self.obsfile)
        self.cycle = cycle
        self.str_channels = obsspace['channels'] if 'channels' in \
            obsspace else None

        self.variable = variable
        self.outdir = outdir

        self.metadata = {'obs name': self.obsname,
                         'cycle': self.cycle,
                         'outdir': self.outdir}

    def get_input_channels(self, channels):
        """
        Creates a list of inputted channels as integers from string.
        """

        changroups = [c.strip() for c in channels.split(',')]
        inputchans = []

        for c in changroups:
            if '-' in c:
                comps = c.split('-')
                x = range(int(comps[0]), int(comps[1])+1)
                inputchans.extend(x)
            else:
                inputchans.extend([int(c)])

        return inputchans

    def _get_data(self, obsspace, variable):
        """
        Grabs data specific to variable from IODA
        obsspace.
        """
        var = obsspace.Variable(variable)
        data = var.read_data()

        return data

    def _get_lat_lon(self, obsspace):
        """
        Grabs lat and lon data from IODAv2 file.
        """
        lats = self._get_data(obsspace, variable='MetaData/latitude')
        lons = self._get_data(obsspace, variable='MetaData/longitude')

        return lats, lons

    def _get_indexed_channels(self, obsspace):
        """
        Grab list of all channels from obs space.
        """

        chansCoords = self._get_data(obsspace, variable='nchans')
        chansCoords = [int(i) for i in chansCoords]

        return chansCoords

    def _statistics(self, data):
        """
        Calculates n, bias and rmse.
        """
        OUT = type('', (), {})

        OUT.n = len(data)
        if OUT.n != 0:
            OUT.bias = np.around(np.nanmean(data), decimals=4)
            OUT.rmse = np.around(np.sqrt(np.nanmean(np.square(data))),
                                 decimals=4)
        else:
            OUT.bias = np.nan
            OUT.rmse = np.nan

        return OUT

    def extract_data(self, obsspace):
        """
        Stores appropriate data to compute stats in object.
        """

        # GSI data
        gsi_data = self._get_data(obsspace,
                                  variable=f"GsiHofX/{self.variable}")
        gsiBC_data = self._get_data(obsspace,
                                    variable=f"GsiHofXBc/{self.variable}")
        gsi_error = self._get_data(obsspace,
                                   variable=("GsiFinalObsError/"
                                             f"{self.variable}"))

        # UFO data
        ufo_data = self._get_data(obsspace,
                                  variable=f"hofx/{self.variable}")
        ufo_eff_qc = self._get_data(obsspace,
                                    variable=f"EffectiveQC/{self.variable}")

        # Obs data
        obs_data = self._get_data(obsspace,
                                  variable=f"ObsValue/{self.variable}")
        obs_data[np.abs(obs_data) > 1e6] = np.nan

        # GSI use flag (radiance only) and obs_type (conventional)
        if self.variable in ['brightness_temperature',
                             'integrated layer ozone in air']:

            gsi_use_flag = self._get_data(obsspace,
                                          variable=f"VarMetaData/gsi_use_flag")
            obs_type = None

        else:
            obs_type = self._get_data(obsspace,
                                      variable=f"ObsType/{self.variable}")
            gsi_use_flag = None

        # OmF data
        gsi_omf = obs_data-gsi_data
        gsiBC_omf = obs_data-gsiBC_data
        ufo_omf = obs_data-ufo_data

        self.data = {
            'GSI': {
                'hofx': gsi_data,
                'error': gsi_error,
                'use_flag': gsi_use_flag,
                'omf': gsi_omf,
                'obs_type': obs_type
            },
            'GSI BC': {
                'hofx': gsiBC_data,
                'error': gsi_error,
                'use_flag': gsi_use_flag,
                'omf': gsiBC_omf,
                'obs_type': obs_type
            },
            'UFO': {
                'hofx': ufo_data,
                'eff_qc': ufo_eff_qc,
                'omf': ufo_omf,
                'obs_type': obs_type
            },
            # THIS NEEDS TO BE CHANGED WHEN
            # HOFX BC DATA IS ADDED
            'UFO BC': {
                'hofx': ufo_data,
                'eff_qc': ufo_eff_qc,
                'omf': ufo_omf,
                'obs_type': obs_type
            },
            'Obs': obs_data
        }

        return

    def _return_data(self, data_type, chanIndex=None, obstypeIndex=None):
        """
        Returns properly indexed hofx, omf, and qc data.
        """

        if data_type in ['UFO', 'UFO BC']:
            if chanIndex:
                # Radiance data
                data = self.data[data_type]['hofx'][:, chanIndex]
                omf = self.data[data_type]['omf'][:, chanIndex]
                qc_indx = np.where(
                    self.data[data_type]['eff_qc'][:, chanIndex] == 0)
                qc_data = data[qc_indx]
                qc_omf = self.data['Obs'][:, chanIndex][qc_indx] - qc_data
            else:
                # Conventional data
                data = self.data[data_type]['hofx'][obstypeIndex]
                omf = self.data[data_type]['omf'][obstypeIndex]
                qc_indx = np.where(
                    self.data[data_type]['eff_qc'][obstypeIndex] == 0)
                qc_data = data[qc_indx]
                qc_omf = self.data['Obs'][obstypeIndex][qc_indx] - qc_data

        elif data_type in ['GSI', 'GSI BC']:
            if chanIndex:
                # Radiance data
                data = self.data[data_type]['hofx'][:, chanIndex]
                omf = self.data[data_type]['omf'][:, chanIndex]
                qc_indx = np.where(
                    self.data[data_type]['error'][:, chanIndex] < 1e6)
                qc_data = data[qc_indx]
                qc_omf = self.data['Obs'][:, chanIndex][qc_indx] - qc_data

                # sets non assimilated data empty arrays for gsi
                if self.data[data_type]['use_flag'][chanIndex] != 1:
                    qc_data = []
                    qc_omf = []

            else:
                # Conventional data
                data = self.data[data_type]['hofx'][obstypeIndex]
                omf = self.data[data_type]['omf'][obstypeIndex]
                qc_indx = np.where(
                    self.data[data_type]['error'][obstypeIndex] < 1e6)
                qc_data = data[qc_indx]
                qc_omf = self.data['Obs'][obstypeIndex][qc_indx] - qc_data

        return data, omf, qc_data, qc_omf

    def create_stats_df(self, obsspace, data_type, channels=None):
        """
        Creates a dataframe of stats for GSI and UFO omf information.
        The stats include n, bias, and rmse.
        """
        df_dict = {}

        # Radiance data
        if channels:
            for chan in channels:
                key = f'Channel {chan}'
                df_dict[key] = {}

                # Gets proper indexed channel
                chanCoords = self._get_indexed_channels(obsspace)
                chanIndex = chanCoords.index(chan)

                hofx, omf, qc_hofx, qc_omf = self._return_data(data_type,
                                                               chanIndex=chanIndex)

                # Get n of hofx data
                hofx_stats = self._statistics(hofx)
                df_dict[key][f'{data_type} count'] = hofx_stats.n

                # Bias and RMSE of omf
                omf_stats = self._statistics(omf)
                df_dict[key][f'{data_type} omf bias'] = omf_stats.bias
                df_dict[key][f'{data_type} omf rmse'] = omf_stats.rmse

                # Get n of qc hofx
                qc_hofx_stats = self._statistics(qc_hofx)
                df_dict[key][f'{data_type} qc count'] = qc_hofx_stats.n

                # Bias and RMSE of qc omf
                qc_omf_stats = self._statistics(qc_omf)
                df_dict[key][f'{data_type} qc omf bias'] = qc_omf_stats.bias
                df_dict[key][f'{data_type} qc omf rmse'] = qc_omf_stats.rmse

            df = pd.DataFrame(df_dict).transpose()

        # Conventional data
        else:
            obs_type = self.data[data_type]['obs_type']
            mask = np.ma.masked_where(obs_type < 0, obs_type)

            for obtype in np.unique(mask)[:-1]:
                key = f'{obtype}'
                df_dict[key] = {}

                # Finds index where obs type is specific value
                obstypeIndex = np.where(obs_type == obtype)

                hofx, omf, qc_hofx, qc_omf = self._return_data(data_type,
                                                               obstypeIndex=obstypeIndex)

                # Get n of hofx data
                hofx_stats = self._statistics(hofx)
                df_dict[key][f'{data_type} count'] = hofx_stats.n

                # Bias and RMSE of omf
                omf_stats = self._statistics(omf)
                df_dict[key][f'{data_type} omf bias'] = omf_stats.bias
                df_dict[key][f'{data_type} omf rmse'] = omf_stats.rmse

                # Get n of qc hofx
                qc_hofx_stats = self._statistics(qc_hofx)
                df_dict[key][f'{data_type} qc count'] = qc_hofx_stats.n

                # Bias and RMSE of qc omf
                qc_omf_stats = self._statistics(qc_omf)
                df_dict[key][f'{data_type} qc omf bias'] = qc_omf_stats.bias
                df_dict[key][f'{data_type} qc omf rmse'] = qc_omf_stats.rmse

            df = pd.DataFrame(df_dict).transpose()

        return df


def gen_statistics(ob_dict, variable, cycle, outdir='./'):

    # Creates object
    diag = IODAstatistics(ob_dict, variable, cycle, outdir)

    # Gets obspace
    obsspace = ioda.ObsSpace(diag.obspath)

    # extract data
    diag.extract_data(obsspace)

    df_list = []

    for d in ['UFO', 'UFO BC', 'GSI', 'GSI BC']:
        # Radiance data
        if diag.str_channels:
            # Grabs channels
            print('in radiance')
            inputchans = diag.get_input_channels(diag.str_channels)

            df = diag.create_stats_df(obsspace, data_type=d,
                                      channels=inputchans)
            df_list.append(df)

        # Conventional data
        elif diag.data[d]['obs_type'] is not None:

            df = diag.create_stats_df(obsspace, data_type=d)
            df_list.append(df)

    df = pd.concat(df_list, axis=1)

    if diag.variable in ['brightness_temperature',
                         'integrated layer ozone in air']:
        df = df.reset_index().rename(columns={'index': 'Channels'})

    else:
        df = df.reset_index().rename(columns={'index': 'Obs Type'})

    # Save to csv file
    df.to_csv((f'{diag.outdir}/{diag.obsname}.{diag.variable}.'
               f'{diag.cycle}.stats'))

    return
