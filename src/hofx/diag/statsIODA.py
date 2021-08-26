class IODAstatistics:

    def __init__(self, ob_dict, variable, outdir):
        # body of the constructor

        obsspace = ob_dict['obs space']
        self.obsname = obsspace['name']
        self.obsfile = os.path.basename(obsspace['obsdataout']['obsfile'])
        self.obspath = os.path.join(ob_dict['diag_dir'], self.obsfile)
        self.cycle = self.obsfile.split('/')[-1].split('.')[-2]
        self.str_channels = obsspace['channels'] if 'channels' in \
            obsspace else None

        self.variable = variable
        self.outfig = outdir

        self.metadata = {'obs name': self.obsname,
                         'cycle': self.cycle,
                         'outfig': self.outfig}

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
            OUT.rmse = np.around(np.sqrt(np.nanmean(np.square(data))), decimals=4)
        else:
            OUT.bias = np.nan
            OUT.rmse = np.nan

        return OUT

    def create_stats_df(self, channels=None):
        """
        Creates a dataframe of stats for GSI and UFO omf information.
        The stats include n, bias, and rmse.
        """
        df_dict = {}

        # GSI data
        gsi_data = self._get_data(obsspace, variable=f"GsiHofX/{self.variable}")
        gsiBC_data = self._get_data(obsspace, variable=f"GsiHofXBc/{self.variable}")
        gsi_error = self._get_data(obsspace, variable=f"GsiFinalObsError/{self.variable}")
        gsi_use_flag = self._get_data(obsspace, variable=f"VarMetaData/gsi_use_flag")

        # UFO data
        ufo_data = self._get_data(obsspace, variable=f"hofx/{self.variable}")
        ufo_eff_qc = self._get_data(obsspace, variable=f"EffectiveQC/{self.variable}")

        # Obs data
        obs_data = self._get_data(obsspace, variable=f"ObsValue/{self.variable}")
        obs_data[np.abs(obs_data) > 1e6] = np.nan

        # OmF data
        gsi_omf = obs_data-gsi_data
        gsiBC_omf = obs_data-gsiBC_data
        ufo_omf = obs_data-ufo_data

        # Loop through channels
        for chan in channels:
            df_dict[f'Channel {chan}'] = {}

            # Gets proper indexed channel
            chanCoords = self._get_indexed_channels(obsspace)
            chanIndex = chanCoords.index(chan)

            # GSI QC'd data
            gsi_qc_data = gsi_data[:, chanIndex][np.where(np.abs(gsi_error[:, chanIndex]) < 1e6)]
            gsiBC_qc_data = gsiBC_data[:, chanIndex][np.where(np.abs(gsi_error[:, chanIndex]) < 1e6)]

            # UFO QC'd data
            ufo_qc_data = ufo_data[:, chanIndex][np.where(ufo_eff_qc[:, chanIndex] == 0)]

            # QC'd omf data - need to index obs correctly to make sure len is same
            ufo_qc_omf = obs[:, chanIndex][np.where(ufo_eff_qc[:, chanIndex] == 0)] - ufo_qc_data
            gsi_qc_omf = obs[:, chanIndex][np.where(np.abs(gsi_error[:, chanIndex]) < 1e6)] - gsi_qc_data
            gsiBC_qc_omf = obs[:, chanIndex][np.where(np.abs(gsi_error[:, chanIndex]) < 1e6)] - gsiBC_qc_data

            # sets non assimilated data empty arrays for gsi
            if gsi_use_flag[chanIndex] != 1:
                gsi_qc_data = []
                gsiBC_qc_data = []
                gsi_qc_omf = []
                gsiBC_qc_omf = []

            # Get n of regular data
            ufo_stats = self._statistics(ufo_data[:, chanIndex])
            gsi_stats = self._statistics(gsi_data[:, chanIndex])
            gsiBC_stats = self._statistics(gsiBC_data[:, chanIndex])

            df_dict[f'Channel {chan}']['UFO count'] = ufo_stats.n
            df_dict[f'Channel {chan}']['GSI count'] = gsi_stats.n
            df_dict[f'Channel {chan}']['GSI BC count'] = gsiBC_stats.n

            # Bias and RMSE of regular omf
            ufo_omf_stats = self._statistics(ufo_omf[:, chanIndex])
            gsi_omf_stats = self._statistics(gsi_omf[:, chanIndex])
            gsiBC_omf_stats = self._statistics(gsiBC_omf[:, chanIndex])

            df_dict[f'Channel {chan}']['UFO omf bias'] = ufo_omf_stats.bias
            df_dict[f'Channel {chan}']['GSI omf bias'] = gsi_omf_stats.bias
            df_dict[f'Channel {chan}']['GSI BC omf bias'] = gsiBC_omf_stats.bias

            df_dict[f'Channel {chan}']['UFO omf rmse'] = ufo_omf_stats.rmse
            df_dict[f'Channel {chan}']['GSI omf rmse'] = gsi_omf_stats.rmse
            df_dict[f'Channel {chan}']['GSI BC omf rmse'] = gsiBC_omf_stats.rmse

            # Get n of qc data
            ufo_qc_stats = self._statistics(ufo_qc_data)
            gsi_qc_stats = self._statistics(gsi_qc_data)
            gsiBC_qc_stats = self._statistics(gsiBC_qc_data)

            df_dict[f'Channel {chan}']['UFO qc count'] = ufo_qc_stats.n
            df_dict[f'Channel {chan}']['GSI qc count'] = gsi_qc_stats.n
            df_dict[f'Channel {chan}']['GSI BC qc count'] = gsiBC_qc_stats.n

            # Bias and RMSE of regular omf
            ufo_qc_omf_stats = self._statistics(ufo_qc_omf)
            gsi_qc_omf_stats = self._statistics(gsi_qc_omf)
            gsiBC_qc_omf_stats = self._statistics(gsiBC_qc_omf)

            df_dict[f'Channel {chan}']['UFO qc omf bias'] = ufo_qc_omf_stats.bias
            df_dict[f'Channel {chan}']['GSI qc omf bias'] = gsi_qc_omf_stats.bias
            df_dict[f'Channel {chan}']['GSI BC qc omf bias'] = gsiBC_qc_omf_stats.bias

            df_dict[f'Channel {chan}']['UFO qc omf rmse'] = ufo_qc_omf_stats.rmse
            df_dict[f'Channel {chan}']['GSI qc omf rmse'] = gsi_qc_omf_stats.rmse
            df_dict[f'Channel {chan}']['GSI BC qc omf rmse'] = gsiBC_qc_omf_stats.rmse

        df = pd.DataFrame(df_dict).transpose().reset_index()
        df = df.rename(columns={'index': 'Channels'})

        return


def gen_statistics(ob_dict, variable, outdir='./'):

    # Creates object
    diag = IODAstatistics(ob_dict, variable, outdir)

    # Gets obspace
    obsspace = ioda.ObsSpace(diag.obspath)

    # If yaml includes channels, will do radiance things
    if diag.str_channels:
        # Grabs channels
        inputchans = diag.get_input_channels(diag.str_channels)

        df = diag.create_stats_df(channels=inputchans)

    df.to_csv(f'{diag.obsname}.{diag.variable}.{diag.cycle}.stats')

    return
