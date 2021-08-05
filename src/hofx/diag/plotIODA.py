import numpy as np
import pandas as pd
import os
import ioda
import yaml
import emcpy
from emcpy.plots import map2d, scatter

__all__ = ['gen_diagnostics']


class IODAdiagnostic:

    def __init__(self, ob_dict, variable, plot_type, plot_dir):
        # body of the constructor

        obsspace = ob_dict['obs space']
        self.obsname = obsspace['name']
        self.obsfile = os.path.basename(obsspace['obsdataout']['obsfile'])
        self.obspath = os.path.join(ob_dict['diag_dir'], self.obsfile)
        self.cycle = self.obsfile.split('/')[-1].split('.')[-2]
        self.str_channels = obsspace['channels'] if 'channels' in obsspace else None

        self.variable = variable
        self.outfig = plot_dir

        # separate plotType variables
        self.plot_type = plot_type.split('_')[0]
        self.eval_var = plot_type.split('_')[-1]

        self.metadata = {'obs name': self.obsname,
                         'cycle': self.cycle,
                         'outfig': self.outfig
                        }


    def get_input_channels(self, channels):
        """
        Creates a list of inputted channels as integers from string.
        """

        changroups = channels.split(', ')
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


    def gen_plot_df(self, obsspace, channel=None):
        """
        Generates the dataframe to produce the diagnostic requested.

        Args:
            obsspace : ioda obsspace object
            metadata : dictionary of metadata
            channel : (default=None) If data contains channel data
                      needed to grab appropriate index of from data

        Returns:
            df : pandas dataframe with variable data, latitude and longitude data
        """

        df_dict = {}

        for dvar in self.data_vars:
            data = self._get_data(obsspace, variable=f"{dvar}/{self.variable}")

            if self.variable == 'brightness_temperature':
                chanCoords = self._get_indexed_channels(obsspace)
                chanIndex = chanCoords.index(channel)
                df_dict[f"{dvar}/{self.variable}_{channel}"] = data[:,chanIndex]
            else:
                df_dict[f"{dvar}/{self.variable}"] = data       

        # Grab lat lons; add to df_dict
        lats, lons = self._get_lat_lon(obsspace)

        df_dict['latitude'] = lats
        df_dict['longitude'] = lons

        # Create dataframe
        df = pd.DataFrame(df_dict)

        # add 'diff' column when data vars has 2 variables
        if len(self.data_vars) == 2:
            if channel:
                df[f"diff/{self.variable}_{channel}"] = df[f"{self.data_vars[0]}/{self.variable}_{channel}"] - \
                                                        df[f"{self.data_vars[-1]}/{self.variable}_{channel}"]
            else:
                df[f"diff/{self.variable}"] = df[f"{self.data_vars[0]}/{self.variable}"] - \
                                              df[f"{self.data_vars[-1]}/{self.variable}"]

        return df


    def hofxdiff(self, channel):
        """
        Grabs metadata for hofxdiff evaluation type input.
        """
        plot_opts = {
            'domain': 'global',
            'cmap': 'coolwarm',
            'vmin': 2,
            'vmax': 2,
            'label': 'GSI-UFO',
            'xlabel': 'GSI',
            'ylabel': 'UFO'
            }

        self.metadata = dict(self.metadata, **plot_opts)

        self.plot_var = 'diff'
        self.data_vars = ['GsiHofXBc', 'hofx']

        if channel:
            self.metadata['title'] = (f"{self.obsname} {self.variable}" 
                                      f"\nChannel {channel} - GSI-UFO")

            self.metadata['savefile'] = (f"{self.obsname}_{self.variable}_"
                                         f"channel_{channel}_{self.eval_var}"
                                         f"_{self.plot_type}")
        else:
            self.metadata['title'] = f"{self.obsname} {self.variable} - GSI-UFO"

            self.metadata['savefile'] = (f"{self.obsname}_{self.variable}_"
                                         f"{self.eval_var}_{self.plot_type}")

        return


    def gsiomf(self, channel):
        """
        Grabs metadata for gsiomf evaluation type input.
        """
        plot_opts = {
            'domain': 'global',
            'cmap': 'coolwarm',
            'vmin': -15,
            'vmax': 15,
            'label': 'Obs-GSI',
            'xlabel': 'Obs',
            'ylabel': 'GSI'
            }

        self.metadata = dict(self.metadata, **plot_opts)

        self.plot_var = 'diff'
        self.data_vars = ['ObsValue', 'GsiHofXBc']

        if channel:
            self.metadata['title'] = (f"{self.obsname} {self.variable}" 
                                      f"\nChannel {channel} - Obs-GSI")

            self.metadata['savefile'] = (f"{self.obsname}_{self.variable}_"
                                         f"channel_{channel}_{self.eval_var}"
                                         f"_{self.plot_type}")
        else:
            self.metadata['title'] = f"{self.obsname} {self.variable} - Obs-GSI"

            self.metadata['savefile'] = (f"{self.obsname}_{self.variable}_"
                                         f"{self.eval_var}_{self.plot_type}")

        return


    def ufoomf(self, channel):
        """
        Grabs metadata for ufoomf evaluation type input.
        """
        plot_opts = {
            'domain': 'global',
            'cmap': 'coolwarm',
            'vmin': -15,
            'vmax': 15,
            'label': 'Obs-UFO',
            'xlabel': 'Obs',
            'ylabel': 'UFO'
            }

        self.metadata = dict(self.metadata, **plot_opts)

        self.plot_var = 'diff'
        self.data_vars = ['ObsValue', 'hofx']
        
        if channel:
            self.metadata['title'] = (f"{self.obsname} {self.variable}" 
                                      f"\nChannel {channel} - Obs-UFO")

            self.metadata['savefile'] = (f"{self.obsname}_{self.variable}_"
                                         f"channel_{channel}_{self.eval_var}"
                                         f"_{self.plot_type}")
        else:
            self.metadata['title'] = f"{self.obsname} {self.variable} - Obs-UFO"

            self.metadata['savefile'] = (f"{self.obsname}_{self.variable}_"
                                         f"{self.eval_var}_{self.plot_type}")

        return


    def gsi(self, channel):
        """
        Grabs metadata for gsi evaluation type input.
        """
        plot_opts = {
            'domain': 'global',
            'cmap': 'viridis',
            'vmin': None,
            'vmax': None,
            'label': 'GSI',
            'xlabel': 'GSI',
            'ylabel': None
            }

        self.metadata = dict(self.metadata, **plot_opts)

        self.plot_var = 'GsiHofXBc'
        self.data_vars = ['GsiHofXBc']

        if channel:
            self.metadata['title'] = (f"{self.obsname} {self.variable}" 
                                      f"\nChannel {channel} - GSI")

            self.metadata['savefile'] = (f"{self.obsname}_{self.variable}_"
                                         f"channel_{channel}_{self.eval_var}"
                                         f"_{self.plot_type}")
        else:
            self.metadata['title'] = f"{self.obsname} {self.variable} - GSI"

            self.metadata['savefile'] = (f"{self.obsname}_{self.variable}_"
                                         f"{self.eval_var}_{self.plot_type}")

        return


    def ufo(self, channel):
        """
        Grabs metadata for ufo evaluation type input.
        """
        plot_opts = {
            'domain': 'global',
            'cmap': 'viridis',
            'vmin': None,
            'vmax': None,
            'label': 'UFO',
            'xlabel': 'UFO',
            'ylabel': None
            }

        self.metadata = dict(self.metadata, **plot_opts)

        self.plot_var = 'hofx'
        self.data_vars = ['hofx']

        if channel:
            self.metadata['title'] = (f"{self.obsname} {self.variable}" 
                                      f"\nChannel {channel} - UFO")

            self.metadata['savefile'] = (f"{self.obsname}_{self.variable}_"
                                         f"channel_{channel}_{self.eval_var}"
                                         f"_{self.plot_type}")
        else:
            self.metadata['title'] = f"{self.obsname} {self.variable} - UFO"

            self.metadata['savefile'] = (f"{self.obsname}_{self.variable}_"
                                         f"{self.eval_var}_{self.plot_type}")

        return


    def obs(self, channel):
        """
        Grabs metadata for obs evaluation type input.
        """
        plot_opts = {
            'domain': 'global',
            'cmap': 'viridis',
            'vmin': None,
            'vmax': None,
            'label': 'Observations',
            'xlabel': 'Observations',
            'ylabel': None
            }

        self.metadata = dict(self.metadata, **plot_opts)

        self.plot_var = 'ObsValue'
        self.data_vars = ['ObsValue']

        if channel:
            self.metadata['title'] = (f"{self.obsname} {self.variable}" 
                                      f"\nChannel {channel} - Observations")

            self.metadata['savefile'] = (f"{self.obsname}_{self.variable}_"
                                         f"channel_{channel}_{self.eval_var}"
                                         f"_{self.plot_var}")
        else:
            self.metadata['title'] = f"{self.obsname} {self.variable} - Observations"

            self.metadata['savefile'] = (f"{self.obsname}_{self.variable}_"
                                         f"{self.eval_var}_{self.plot_var}")

        return


def _query_plot_type(df, diag):
    """
    Generates figure based on plot type.
    """
    plot_types = {
        'spatial': map2d(df['latitude'], df['longitude'],
                         df[f"{diag.plot_var}/{diag.variable}"],
                         domain = diag.metadata['domain'],
                         plotmap=True,
                         cmap=diag.metadata['cmap'],
                         vmin=diag.metadata['vmin'],
                         vmax=diag.metadata['vmax'],
                         title=diag.metadata['title'],
                         time_title=diag.metadata['cycle']),

        'scatter': scatter(df[f"{diag.data_vars[0]}/{diag.variable}"].to_numpy(),
                           df[f"{diag.data_vars[-1]}/{diag.variable}"].to_numpy(),
                           linear_regression=False,
                           density=False, grid=True,
                           title=diag.metadata['title'],
                           time_title=diag.metadata['cycle'],
                           xlabel=diag.metadata['xlabel'],
                           ylabel=diag.metadata['ylabel'])
    }

    fig = plot_types[diag.plot_type]

    return fig


def _query_eval_type(diag, channel=None):
    """
    Calls method based on evaluation type.
    """
    plot_types = {
        'hofxdiff': diag.hofxdiff,
        'gsiomf': diag.gsiomf,
        'ufoomf': diag.ufoomf,
        'gsi': diag.gsi,
        'ufo': diag.ufo,
        'obs': diag.obs
    }

    return plot_types[diag.eval_var](channel)


def gen_diagnostics(ob_dict, variable, plot_type, plot_dir='./'):
    """
    Driver function to grab metadata, create a dataframe, and generate
    diagnostics from a yaml input. 

    Args:
        ob_dict: dictionary containing info on obs file
        variable: variable from ob to create diagnostic
        plotType: str of the type of plot requested
        plot_dir: outdir where the plot should be saved to
    """

    diag = IODAdiagnostic(ob_dict, variable, plot_type, plot_dir)

    obsspace = ioda.ObsSpace(diag.obspath)

    if diag.str_channels:
        inputchans = diag.get_input_channels(diag.str_channels)

        for channel in inputchans:
            _query_eval_type(diag, channel)

            df = diag.gen_plot_df(obsspace, channel)

            diag.variable = f"{diag.variable}_{channel}"
            fig = _query_plot_type(df, diag)

            fig.savefig(f"{os.path.join(diag.outfig,diag.metadata['savefile'])}.png", bbox_inches='tight', pad_inches=0.1)

    else:
        _query_eval_type(diag)

        df = diag.gen_plot_df(obsspace)

        fig = _query_plot_type(df, diag)
        print(f"{diag.metadata['savefile']}.png")
        fig.savefig(f"{os.path.join(diag.outfig,diag.metadata['savefile'])}.png", bbox_inches='tight', pad_inches=0.1)


    return

