import numpy as np
import pandas as pd
import os
import ioda
import yaml
import emcpy
from emcpy.plots import map2d, scatter

__all__ = ['gen_diagnostics']


def _spatial(df, metadata):
    """
    Plots and saves a spatial plot on a map.
    """
    
    if metadata['channel']:
        data = df[f"{metadata['plot var']}/{metadata['variable']}_{metadata['channel']}"]
    else:
        data = df[f"{metadata['plot var']}/{metadata['variable']}"]

    fig = map2d(df['latitude'], df['longitude'],
                data, domain = metadata['domain'],
                plotmap=True, cmap=metadata['cmap'],
                vmin=metadata['vmin'],
                vmax=metadata['vmax'],
                title=metadata['title'],
                time_title=metadata['time title'])

    fig.savefig(f"{metadata['savefile']}_spatial.png", bbox_inches='tight', pad_inches=0.1)

    return

def _scatter(df, metadata):
    """
    Plots and saves a scatter plot.
    """

    if metadata['channel']:
        x = df[f"{metadata['data var'][0]}/{metadata['variable']}_{metadata['channel']}"]
        y = df[f"{metadata['data var'][-1]}/{metadata['variable']}_{metadata['channel']}"]
    else:
        x = df[f"{metadata['data var'][0]}/{metadata['variable']}"]
        y = df[f"{metadata['data var'][-1]}/{metadata['variable']}"]

    fig = scatter(x, y,
                  linear_regression=True,
                  density=False, grid=True,
                  title=metadata['title'],
                  time_title=metadata['cycle'],
                  xlabel=metadata['xlabel'],
                  ylabel=metadata['ylabel']
                 )

    fig.savefig(f"{metadata['savefile']}_scatter.png", bbox_inches='tight', pad_inches=0.1)

    return


def _query_plot_type(df, metadata):
    """
    Calls function based on 'plot type' from metadata.
    """
    plot_types = {
        'spatial': _spatial,
        'scatter': _scatter
    }

    return plot_types[metadata['plot type']](df, metadata)


def _hofxdiff(metadata):
    """
    Grabs metadata for hofxdiff evaluation type input.
    """
    plot_opts = {
        'plot var' : 'diff',
        'data vars': ['GsiHofXBc', 'hofx'],
        'cmap': 'coolwarm',
        'vmin': 2,
        'vmax': 2,
        'label': 'GSI-UFO',
        'xlabel': 'GSI',
        'ylabel': 'UFO'
        }
    
    metadata = dict(metadata, **plot_opts)
    
    if metadata['channel']:
        metadata['title'] = (f"{metadata['obs name']} {metadata['variable']}" 
                            f"\nChannel {metadata['channel']} - GSI-UFO")
        
        metadata['savefile'] = (f"{metadata['obs name']}_{metadata['variable']}_"
                                f"channel_{metadata['channel']}_{metadata['eval type']}")
    else:
        metadata['title'] = f"{metadata['obs name']} {metadata['variable']} - GSI-UFO"
        
        metadata['savefile'] = (f"{metadata['obs name']}_{metadata['variable']}_"
                                f"{metadata['eval type']}")
    
    return metadata

def _gsiomf(metadata):
    """
    Grabs metadata for gsiomf evaluation type input.
    """
    plot_opts = {
        'plot var': 'diff',
        'data vars': ['ObsValue', 'GsiHofXBc'],
        'cmap': 'coolwarm',
        'vmin': -15,
        'vmax': 15,
        'label': 'Obs-GSI',
        'xlabel': 'Obs',
        'ylabel': 'GSI'
        }
    
    metadata = dict(metadata, **plot_opts)
    
    if metadata['channel']:
        metadata['title'] = f"{metadata['obs name']} {metadata['variable']}"\
                            f"\nChannel {metadata['channel']} - Obs-GSI"
    else:
        metadata['title'] = f"{metadata['obs name']} {metadata['variable']} - Obs-GSI"
    
    return metadata

def _ufoomf(metadata):
    """
    Grabs metadata for ufoomf evaluation type input.
    """
    plot_opts = {
        'plot var': 'diff',
        'data vars': ['ObsValue', 'hofx'],
        'cmap': 'coolwarm',
        'vmin': -15,
        'vmax': 15,
        'label': 'Obs-UFO',
        'xlabel': 'Obs',
        'ylabel': 'UFO'
        }
    
    metadata = dict(metadata, **plot_opts)
    
    if metadata['channel']:
        metadata['title'] = f"{metadata['obs name']} {metadata['variable']}"\
                            f"\nChannel {metadata['channel']} - Obs-UFO"
    else:
        metadata['title'] = f"{metadata['obs name']} {metadata['variable']} - Obs-UFO"
    
    return metadata

def _gsi(metadata):
    """
    Grabs metadata for gsi evaluation type input.
    """
    plot_opts = {
        'plot var': 'GsiHofXBc',
        'data vars': ['GsiHofXBc'],
        'cmap': 'viridis',
        'vmin': None,
        'vmax': None,
        'label': 'GSI',
        'xlabel': 'GSI',
        'ylabel': None
        }
    
    metadata = dict(metadata, **plot_opts)
    
    if metadata['channel']:
        metadata['title'] = f"{metadata['obs name']} {metadata['variable']}"\
                            f"\nChannel {metadata['channel']} - GSI"
    else:
        metadata['title'] = f"{metadata['obs name']} {metadata['variable']} - GSI"
    
    return metadata

def _ufo(metadata):
    """
    Grabs metadata for ufo evaluation type input.
    """
    plot_opts = {
        'plot var': 'hofx',
        'data vars': ['hofx'],
        'cmap': 'viridis',
        'vmin': None,
        'vmax': None,
        'label': 'UFO',
        'xlabel': 'UFO',
        'ylabel': None
        }
    
    metadata = dict(metadata, **plot_opts)
    
    if metadata['channel']:
        metadata['title'] = f"{metadata['obs name']} {metadata['variable']}"\
                            f"\nChannel {metadata['channel']} - GSI-UFO"
    else:
        metadata['title'] = f"{metadata['obs name']} {metadata['variable']} - GSI-UFO"
        
    return metadata

def _obs(metadata):
    """
    Grabs metadata for obs evaluation type input.
    """
    plot_opts = {
        'plot var': 'ObsValue',
        'data vars': ['ObsValue'],
        'cmap': 'viridis',
        'vmin': None,
        'vmax': None,
        'label': 'Observations',
        'xlabel': 'Observations',
        'ylabel': None
        }
    
    metadata = dict(metadata, **plot_opts)
    
    if metadata['channel']:
        metadata['title'] = f"{metadata['obs name']} {metadata['variable']}"\
                            f"\nChannel {metadata['channel']} - Observations"
    else:
        metadata['title'] = f"{metadata['obs name']} {metadata['variable']} - Observations"
        
    return metadata     


def _query_eval_type(metadata):
    """
    Calls function based on 'eval type' from metadata.
    """
    plot_types = {
        'hofxdiff': _hofxdiff,
        'gsiomf': _gsiomf,
        'ufoomf': _ufoomf,
        'gsi': _gsi,
        'ufo': _ufo,
        'obs': _obs
    }
    
    return plot_types[metadata['eval type']](metadata)


def _get_data(obsspace, variable):
    """
    Grabs data specific to variable from IODA
    obsspace.
    """
    var = obsspace.Variable(variable)
    data = var.read_data()
    
    return data


def _get_lat_lon(obsspace):
    """
    Grabs lat and lon data from IODAv2 file.
    """
    lats = _get_data(obsspace, variable='MetaData/latitude')
    lons = _get_data(obsspace, variable='MetaData/longitude')
    
    return lats, lons


def _get_indexed_channels(obsspace):
    """
    Grab list of all channels from obs space.
    """
    
    chansCoords = _get_data(obsspace, variable='nchans')
    chansCoords = [int(i) for i in chansCoords]

    return chansCoords


def _gen_plot_df(obsspace, metadata, channel=None):
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
    
    for dvar in metadata['data vars']:
        data = _get_data(obsspace, variable=f"{dvar}/{metadata['variable']}")
        
        if metadata['variable'] == 'brightness_temperature':
            chanCoords = _get_indexed_channels(obsspace)
            chanIndex = chanCoords.index(channel)
            df_dict[f"{dvar}/{metadata['variable']}_{channel}"] = data[:,chanIndex]
        else:
            df_dict[f"{dvar}/{metadata['variable']}"] = data       
        
    # Grab lat lons; add to df_dict
    lats, lons = _get_lat_lon(obsspace)
    
    df_dict['latitude'] = lats
    df_dict['longitude'] = lons
    
    # Create dataframe
    df = pd.DataFrame(df_dict)
    
    # add 'diff' column when data vars has 2 variables
    if len(metadata['data vars']) == 2:
        if channel:
            df[f"diff/{metadata['variable']}_{channel}"] = df[f"{metadata['data vars'][0]}/{metadata['variable']}_{channel}"] - \
                                                           df[f"{metadata['data vars'][-1]}/{metadata['variable']}_{channel}"]
        else:
            df[f"diff/{metadata['variable']}"] = df[f"{metadata['data vars'][0]}/{metadata['variable']}"] - \
                                                 df[f"{metadata['data vars'][-1]}/{metadata['variable']}"]
        
    return df


# Generate metadata

def _get_input_channels(channels):
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


def _gen_metadata(ob_dict, variable, plotType, plot_dir):
    """
    Uses initial inputs from yaml input to create a 
    metadata dictionary that is used to create diagnostics.
    """
    
    obsspace = ob_dict['obs space']
    obsname = obsspace['name']
    obsfile = os.path.join(ob_dict['diag_dir'], os.path.basename(obsspace['obsdataout']['obsfile']))
    cycle = obsfile.split('/')[-1].split('.')[-2]
    
    str_channels = obsspace['channels'] if 'channels' in obsspace else None
        
    # separate plotType variables; add to metadata
    plotvar = plotType.split('_')[0]
    evalvar = plotType.split('_')[-1]
    
    metadata = {'obs file': obsfile,
                'obs name': obsname,
                'str channels': str_channels,
                'cycle': cycle,
                'variable': variable,
                'outfig': plot_dir,
                'plot type': plotvar,
                'eval type': evalvar
               }
    
    return metadata


def gen_diagnostics(ob_dict, variable, plotType, plot_dir='./'):
    """
    Driver function to grab metadata, create a dataframe, and generate
    diagnostics from a yaml input. 
    
    Args:
        ob_dict: dictionary containing info on obs file
        variable: variable from ob to create diagnostic
        plotType: str of the type of plot requested
        plot_dir: outdir where the plot should be saved to
    """
    
    metadata = _gen_metadata(ob_dict, variable, plotType, plot_dir)
    
    obsspace = ioda.ObsSpace(metadata['obs file'])
    
    if 'str channels' in metadata.keys():
        inputchans = _get_input_channels(metadata['str channels'])
        inputchans = [1]
        
        for channel in inputchans:
            metadata['channel'] = channel
            metadata = _query_eval_type(metadata)
            
            df = _gen_plot_df(obsspace, metadata, channel)
            
            _query_plot_type(df, metadata)
    
    else:
        metadata = _query_eval_type(metadata)
        
        df = _gen_plot_df(obsspace, metadata, channel)
        
        _query_plot_type(df, metadata)
        
            
    return

