import numpy as np
import pandas as pd
import os
import ioda
import yaml
import matplotlib.pyplot as plt
from emcpy.plots.plots import Scatter
from emcpy.plots.map_plots import MapScatter
from emcpy.plots import CreateMap, CreatePlot, VariableSpecs
from emcpy.plots.map_tools import Domain, MapProjection


__all__ = ['gen_diagnostics']


class IODAdiagnostic:

    def __init__(self, ob_dict, variable, cycle, plot_type, plot_dir):
        # body of the constructor

        obsspace = ob_dict['obs space']
        self.obsname = obsspace['name']
        self.obsfile = os.path.basename(obsspace['obsdataout']['obsfile'])
        self.obspath = os.path.join(ob_dict['diag_dir'], self.obsfile)
        self.cycle = cycle
        self.str_channels = obsspace['channels'] if 'channels' in \
            obsspace else None

        self.variable = variable
        self.outfig = plot_dir

        # separate plotType variables
        self.plot_type = plot_type.split('_')[0]
        self.eval_var = plot_type.split('_')[-1]

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

    def gen_plot_df(self, obsspace, channel=None):
        """
        Generates the dataframe to produce the diagnostic requested.

        Args:
            obsspace : ioda obsspace object
            metadata : dictionary of metadata
            channel : (default=None) If data contains channel data
                      needed to grab appropriate index of from data

        Returns:
            df : pandas dataframe with variable data, latitude and
                 longitude data
        """

        df_dict = {}

        for dvar in self.data_vars:
            data = self._get_data(obsspace, variable=f"{dvar}/{self.variable}")

            if self.variable == 'brightness_temperature':
                chanCoords = self._get_indexed_channels(obsspace)
                chanIndex = chanCoords.index(channel)
                df_dict[f"{dvar}/{self.variable}_{channel}"] = \
                    data[:, chanIndex]
            else:
                df_dict[f"{dvar}/{self.variable}"] = data

        # Grab lat lons; add to df_dict
        lats, lons = self._get_lat_lon(obsspace)

        df_dict['latitude'] = lats
        df_dict['longitude'] = lons

        # Create dataframe
        df = pd.DataFrame(df_dict)

        # drop rows in df with nans and reset index
        df = df.dropna().reset_index()

        # add 'diff' column when data vars has 2 variables
        if len(self.data_vars) >= 2:
            if channel:
                df[f"diff/{self.variable}_{channel}"] = \
                    df[f"{self.data_vars[0]}/{self.variable}_{channel}"] - \
                    df[f"{self.data_vars[1]}/{self.variable}_{channel}"]
            else:
                df[f"diff/{self.variable}"] = \
                    df[f"{self.data_vars[0]}/{self.variable}"] - \
                    df[f"{self.data_vars[1]}/{self.variable}"]

        return df

    def _varspecs_name(self):
        """
        Grabs the specific variable name to utlitize emcpy's VariableSpecs.
        """
        vardict = {
                'temperature': ['air temperature', 'tmp', 'temp'],
                'specific humidity': ['q', 'spfh'],
                'u': ['eastward wind', 'ugrd'],
                'v': ['northward wind', 'vgrd'],
                'wind speed': ['windspeed'],
                'brightness temperature': ['bt']
            }

        # makes lower case and replaces underscore with space
        spec_variable = self.variable.lower().replace('_', ' ')

        for key in vardict.keys():
            spec_variable = key if spec_variable in vardict[key] \
                else spec_variable

        return spec_variable

    def query_eval_type(self, channel=None):
        """
        Stores metadata, plot_var, and data_vars in self.
        """
        eval_types = {
            'hofxdiff': {
                'plot opts': {
                    'domain': 'global',
                    'projection': 'plcarr',
                    'xlabel': 'GSI',
                    'ylabel': 'UFO',
                    'title tag': 'GSI-UFO'
                },
                'plot var': 'diff',
                'data vars': ['GsiHofXBc', 'hofx']
            },
            'hofxbias': {
                'plot opts': {
                    'domain': 'global',
                    'projection': 'plcarr',
                    'xlabel': 'GSI',
                    'ylabel': 'GSI-UFO',
                    'title tag': 'HofX Bias'
                },
                'plot var': 'diff',
                'data vars': ['GsiHofXBc', 'hofx']
            },
            'omfdiff': {
                'plot opts': {
                    'domain': 'global',
                    'projection': 'plcarr',
                    'xlabel': 'O-F GSI',
                    'ylabel': 'O-F UFO',
                    'title tag': 'O-F Comparison'
                },
                'plot var': 'diff',
                'data vars': ['GsiHofXBc', 'hofx', 'ObsValue']
            },
            'gsiomf': {
                'plot opts': {
                    'domain': 'global',
                    'projection': 'plcarr',
                    'xlabel': 'Obs',
                    'ylabel': 'GSI',
                    'title tag': 'Obs-GSI'
                },
                'plot var': 'diff',
                'data vars': ['ObsValue', 'GsiHofXBc']
            },
            'ufoomf': {
                'plot opts': {
                    'domain': 'global',
                    'projection': 'plcarr',
                    'xlabel': 'Obs',
                    'ylabel': 'UFO',
                    'title tag': 'Obs-UFO'
                },
                'plot var': 'diff',
                'data vars': ['ObsValue', 'hofx']
            },
            'gsi': {
                'plot opts': {
                    'domain': 'global',
                    'projection': 'plcarr',
                    'xlabel': 'GSI',
                    'ylabel': None,
                    'title tag': 'GSI'
                },
                'plot var': 'GsiHofXBc',
                'data vars': ['GsiHofXBc']
            },
            'ufo': {
                'plot opts': {
                    'domain': 'global',
                    'projection': 'plcarr',
                    'xlabel': 'UFO',
                    'ylabel': None,
                    'title tag': 'UFO'
                },
                'plot var': 'hofx',
                'data vars': ['hofx']
            },
            'obs': {
                'plot opts': {
                    'domain': 'global',
                    'projection': 'plcarr',
                    'xlabel': 'Observations',
                    'ylabel': None,
                    'title tag': 'Observations'
                },
                'plot var': 'ObsValue',
                'data vars': ['ObsValue']
            }
        }

        # Grab plot options and add to metadata
        plot_opts = eval_types[self.eval_var]['plot opts']
        self.metadata = dict(self.metadata, **plot_opts)

        self.plot_var = eval_types[self.eval_var]['plot var']
        self.data_vars = eval_types[self.eval_var]['data vars']

        # Get variable specs
        spec_variable = self._varspecs_name()

        etype = 'magnitude' if self.plot_var != 'diff' else self.plot_var
        varspecs = VariableSpecs(variable=spec_variable,
                                 eval_type=etype)

        self.metadata['vmin'] = varspecs.vmin
        self.metadata['vmax'] = varspecs.vmax
        self.metadata['cmap'] = varspecs.cmap

        if self.eval_var in ['omfdiff', 'hofxdiff']:
             self.metadata['vmin'] = varspecs.vmin / 100.
             self.metadata['vmax'] = varspecs.vmax / 100.

        self.metadata['label'] = f"{varspecs.name} ({varspecs.units})"

        if channel:
            self.metadata['title'] = (f"{self.obsname} {self.variable}"
                                      f"\nChannel {channel} - "
                                      f"{self.metadata['title tag']}")

            self.metadata['savefile'] = (f"{self.obsname}.{self.variable}_"
                                         f"channel_{channel}.{self.eval_var}"
                                         f".{self.plot_type}")
        else:
            self.metadata['title'] = (f"{self.obsname} {self.variable} - "
                                      f"{self.metadata['title tag']}")

            self.metadata['savefile'] = (f"{self.obsname}.{self.variable}."
                                         f"{self.eval_var}.{self.plot_type}")


def _mapping(df, diag):
    """
    Generate a map using emcpy.
    """
    # Generate domain and map projection
    domain = Domain(diag.metadata['domain'])
    proj = MapProjection(diag.metadata['projection'])

    # Generate map and add map features
    mymap = CreateMap(figsize=(12, 8), domain=domain, proj_obj=proj)
    mymap.add_features(['coastlines'])

    # Generate data to plot and set attributes
    plotobj = MapScatter(df['latitude'], df['longitude'],
                         df[f"{diag.plot_var}/{diag.variable}"])

    plotobj.cmap = diag.metadata['cmap']
    plotobj.vmin = diag.metadata['vmin']
    plotobj.vmax = diag.metadata['vmax']

    # Draw data on existing map
    mymap.draw_data([plotobj])

    # Add features to the plot
    mymap.add_colorbar(label=diag.metadata['label'],
                       label_fontsize=12, extend='neither')
    mymap.add_title(label=diag.metadata['title'],
                    loc='left', fontsize=12)
    mymap.add_title(label=diag.metadata['cycle'],
                    loc='right', fontsize=12,
                    fontweight='semibold')
    mymap.add_xlabel(xlabel='Longitude')
    mymap.add_ylabel(ylabel='Latitude')
    mymap.add_grid()

    # Return figure
    fig = mymap.return_figure()

    return fig


def _scatter(df, diag):
    """
    Generate scatter plot using emcpy.
    """
    # Generate scatter object and add linear regression
    if diag.eval_var in ['hofxbias']:
        # hofxbias is very particular eval type. It requires
        # GSI on x axis and GSI-UFO on y axis
        plotobj = Scatter(
            df[f"{diag.data_vars[0]}/{diag.variable}"].to_numpy(),
            df[f"{diag.plot_var}/{diag.variable}"].to_numpy())
    elif diag.eval_var in ['omfdiff']:
        # need to get O-F from both for scatter
        omf_gsi = df[f"{diag.data_vars[-1]}/{diag.variable}"].to_numpy() - \
                  df[f"{diag.data_vars[0]}/{diag.variable}"].to_numpy()
        omf_ufo = df[f"{diag.data_vars[-1]}/{diag.variable}"].to_numpy() - \
                  df[f"{diag.data_vars[1]}/{diag.variable}"].to_numpy()
        plotobj = Scatter(omf_gsi, omf_ufo)
    else:
        plotobj = Scatter(
            df[f"{diag.data_vars[0]}/{diag.variable}"].to_numpy(),
            df[f"{diag.data_vars[-1]}/{diag.variable}"].to_numpy())
    plotobj.add_linear_regression()
    plotobj.density_scatter()

    # Generate plot and draw data
    myplot = CreatePlot(figsize=(10, 8))
    myplot.draw_data([plotobj])

    if diag.eval_var in ['omfdiff']:
        max1 = max(abs(max(plotobj.x)), abs(max(plotobj.y)))
        min1 = max1 * -1.
        myplot.set_xlim(min1,max1)
        myplot.set_ylim(min1,max1)

    # Add features to plot
    myplot.add_title(label=diag.metadata['title'],
                     fontsize=12, loc='left')
    myplot.add_title(label=diag.metadata['cycle'],
                     loc='right', fontsize=12,
                     fontweight='semibold')
    myplot.add_xlabel(xlabel=diag.metadata['xlabel'])
    myplot.add_ylabel(ylabel=diag.metadata['ylabel'])
    myplot.add_grid(color='lightgray')
    myplot.add_legend()

    # Return figure
    fig = myplot.return_figure()

    return fig


def _query_plot_type(df, diag):
    """
    Generates figure based on plot type.
    """
    plot_types = {
        'spatial': _mapping,
        'scatter': _scatter
    }

    fig = plot_types[diag.plot_type](df, diag)

    return fig


def gen_diagnostics(ob_dict, variable, cycle, plot_type, plot_dir='./'):
    """
    Driver function to grab metadata, create a dataframe, and generate
    diagnostics from a yaml input.

    Args:
        ob_dict: dictionary containing info on obs file
        variable: variable from ob to create diagnostic
        plotType: str of the type of plot requested
        plot_dir: outdir where the plot should be saved to
    """

    # Creates object
    diag = IODAdiagnostic(ob_dict, variable, cycle, plot_type, plot_dir)

    # Gets obspace
    obsspace = ioda.ObsSpace(diag.obspath)

    # If yaml includes channels, will do radiance things
    if diag.str_channels:
        # Grabs channels
        inputchans = diag.get_input_channels(diag.str_channels)

        # loops through each channel input to create diag
        for channel in inputchans:
            # determines the eval type
            diag.query_eval_type(channel)

            # generates dataframe
            df = diag.gen_plot_df(obsspace, channel)

            # changes variable to 'variable_channel'
            diag.variable = f"{diag.variable}_{channel}"
            # create figure
            fig = _query_plot_type(df, diag)

            fig.savefig(
                f"{os.path.join(diag.outfig, diag.metadata['savefile'])}.png",
                bbox_inches='tight', pad_inches=0.1)
            plt.close(fig)
            diag.variable = variable

    else:
        diag.query_eval_type()

        df = diag.gen_plot_df(obsspace)

        fig = _query_plot_type(df, diag)
        print(f"{diag.metadata['savefile']}.png")
        fig.savefig(
            f"{os.path.join(diag.outfig,diag.metadata['savefile'])}.png",
            bbox_inches='tight', pad_inches=0.1)
        plt.close(fig)

    return
