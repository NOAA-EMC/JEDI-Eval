import numpy as np
import pandas as pd
import xarray as xr
import os
import ioda

from hofx.diag import diagnostics


def append_dict(dic, data, variable, inputchans=None, chanCoords=None):
    """
    Create dictionary from existing dictionary.
    Input:
        dic: existing dictionary
        data: data to be added to dictionary
        variable: string of variable
        inputchans: lsit of inputted channels of radiance data requested by user
        chanCoords: list of all channels from sensor/satellite
    Output
        dic: outputted dictionary
    """
    
    if len(data.shape) == 2:
        if inputchans:
            for channel in inputchans:
                chanIndex=chanCoords.index(channel)
                dic[f'{variable}_{channel}'] = data[:,chanIndex]
        else:
            raise TypeError("Please enter channel data.")
        
    else:
        dic[f'{variable}'] = data
        
    return dic

def get_data(obsspace, variable):
    
    var = obsspace.Variable(variable)
    data = var.read_data()
    
    return data

def get_lat_lon(obsspace):
    
    lats = get_data(obsspace, variable='MetaData/latitude')
    lons = get_data(obsspace, variable='MetaData/longitude')
    
    return lats, lons

def get_indexed_channels(obsspace):
    """
    Grab list of all channels from obs space.
    """
    
    chansCoords = get_data(obsspace, variable='nchans')
    chansCoords = [int(i) for i in chansCoords]

    return chansCoords

def get_input_channels(channels):
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
    
def gen_plot_df(obsspace, variable, plotType, inputchans=None):
    
    d = {'hofxdiff': ['hofx', 'GsiHofXBc'],
         'hofx': ['hofx', 'GsiHofXBc'],
         'gsiomf': ['ObsValue', 'GsiHofXBc'],
         'ufoomf': ['ObsValue', 'hofx'],
         'ufocounts': ['hofx'],
         'gsicounts': ['GsiHofxBc'],
         'obscounts': ['ObsValue'],
         'ufo': ['hofx'],
         'gsi': ['GsiHofX'],
         'obs': ['ObsValue']
        }

    plotType_components = plotType.split('_')
    plotvar = plotType_components[-1]
    
    # Gets appropriate variables based on plot type
    plotgroups = d[plotvar]
    
    plot_dict = {}
    
    # loop through variable(s) to get all data needed
    for group in plotgroups:
        data = get_data(obsspace, variable=f'{group}/{variable}')
        
        ### Figure this out once finished with logic of function ###
        if variable == 'brightness_temperature':
            chanCoords = get_indexed_channels(obsspace)
            plot_dict = append_dict(plot_dict, data, variable=f'{group}/{variable}', inputchans=inputchans, chanCoords=chanCoords)
            
        
    # Grab lat lons
    lats, lons = get_lat_lon(obsspace)
    
    plot_dict = append_dict(plot_dict, lats, variable='latitude')
    plot_dict = append_dict(plot_dict, lons, variable='longitude')
    
    # Create dataframe
    df = pd.DataFrame(plot_dict)

    return df 

def plot_metadata(var):
    """
    Grabs metadata dictionary based on the plot variable given.
    """
    
    d = {'hofxdiff': {'cmap': 'coolwarm',
                      'vmin': -15,
                      'vmax': 15,
                      'label': 'GSI-UFO'
                      'xlabel': 'GSI',
                      'ylabel': 'UFO'
                     },
         'gsiomf':   {'cmap': 'coolwarm',
                      'vmin': -15,
                      'vmax': 15,
                      'label': 'Obs-GSI'
                      'xlabel': 'Obs',
                      'ylabel': 'GSI'
                     },
         'ufoomf':   {'cmap': 'coolwarm',
                      'vmin': -15,
                      'vmax': 15,
                      'label': 'Obs-UFO'
                      'xlabel': 'Obs',
                      'ylabel': 'UFO'
                     },
         'gsi':      {'cmap': 'viridis',
                      'vmin': None,
                      'vmax': None,
                      'label': 'GSI'
                      'xlabel': 'GSI',
                      'ylabel': None
                     },
         'ufo':      {'cmap': 'viridis',
                      'vmin': None,
                      'vmax': None,
                      'label': 'UFO'
                      'xlabel': 'UFO',
                      'ylabel': None
                     },
         'obs':      {'cmap': 'viridis',
                      'vmin': None,
                      'vmax': None,
                      'label': 'Observations'
                      'xlabel': 'Observations',
                      'ylabel': None
                     },
         'hofx':     {'cmap': 'coolwarm',
                      'vmin': None,
                      'vmax': None,
                      'label': 'GSI-UFO'
                      'xlabel': 'GSI',
                      'ylabel': 'UFO'
                     }
                    }
    
    return d[var]


def query_plot_type(df, variable, plotType, metadata, channel=None):    
    
    if plotType.endswith('hofxdiff'):
        plotvar = 'hofxdiff'
        if channel:
            df[f'hofxdiff/{variable}_{channel}'] = df[f'GsiHofXBc/{variable}_{channel}'] - df[f'hofx/{variable}_{channel}']
        else:
            df[f'hofxdiff/{variable}'] = df[f'GsiHofXBc/{variable}'] - df[f'hofx/{variable}']

        plot_dict = plot_metadata['hofxdiff']
        metadata = dict(metadata, **plot_dict)
        
        metadata['title'] = f"{metadata['obs name']} {variable} channel {channel} - GSI-UFO"


    elif plotType.endswith('gsiomf'):
        plotvar = 'omf'
        if channel:
            df[f'omf/{variable}_{channel}'] = df[f'ObsValue/{variable}_{channel}'] - df[f'GsiHofXBc/{variable}_{channel}']
        else:
            df[f'omf/{variable}'] = df[f'ObsValue/{variable}'] - df[f'GsiHofXBc/{variable}']
        
        plot_dict = plot_metadata['gsiomf']
        metadata = dict(metadata, **plot_dict)
        
        metadata['title'] = f"{metadata['obs name']} {variable} channel {channel} - Obs-GSI"

    elif plotType.endswith('ufoomf'):
        plotvar = 'omf'
        if channel:
            df[f'omf/{variable}_{channel}'] = df[f'ObsValue/{variable}_{channel}'] - df[f'hofx/{variable}_{channel}']
        else:
            df[f'omf/{variable}'] = df[f'ObsValue/{variable}'] - df[f'hofx/{variable}']
        
        plot_dict = plot_metadata['ufoomf']
        metadata = dict(metadata, **plot_dict)
        
        metadata['title'] = f"{metadata['obs name']} {variable} channel {channel} - Obs-UFO"

    elif plotType.endswith('gsi'):
        plotvar = 'GsiHofXBc'
        
        plot_dict = plot_metadata['gsi']
        metadata = dict(metadata, **plot_dict)
        
        metadata['title'] = f"{metadata['obs name']} {variable} channel {channel} - GSI"

    elif plotType.endswith('ufo'):
        plotvar = 'hofx'
        
        plot_dict = plot_metadata['ufo']
        metadata = dict(metadata, **plot_dict)
        
        metadata['title'] = f"{metadata['obs name']} {variable} channel {channel} - UFO"

    elif plotType.endswith('obs'):
        plotvar = 'ObsValue'
        
        plot_dict = plot_metadata['obs']
        metadata = dict(metadata, **plot_dict)
        
        metadata['title'] = f"{metadata['obs name']} {variable} channel {channel} - Observations"
        
    elif plotType.endswith('hofx'):
        plotvar = ['GsiHofXBc', 'hofx']
        
        plot_dict = plot_metadata['hofx']
        metadata = dict(metadata, **plot_dict)
        
        metadata['title'] = f"{metadata['obs name']} {variable} channel {channel} - GSI-UFO"
        
    else:
        raise TypeError(f'Plot variable {plotType} is not recognized. Please enter valid plot variable.')
        
    return df, plotvar, metadata

def parse_ob_dict(ob_dict):
    
    obsspace = ob_dict['obs space']
    obsname = obsspace['name']
    obsfile = obsspace['obsdataout']['obsfile']
    cycle = obsfile.split('/')[-1].split('.')[-2]
    
    if 'channels' in obsspace:
        channels = obsspace['channels']
    else:
        channels = None
    
    metadata = {'obs file': obsfile,
                'obs name': obsname,
                'channels': channels,
                'cycle': cycle}
    
    return metadata


def genDiagnostics(ob_dict, variable, plotType, plot_dir='./'):
    """
    Input:
        ob_dict: dictionary containing info on obs file
        variable: variable from ob to create diagnostic
        plotType: str of the type of plot requested
        plot_dir: outdir where the plot should be saved to
    """
    
    metadata = parse_ob_dict(ob_dict)
    channels = metadata['channels']
    metadata['outfig'] = plot_dir
    
    obsspace = ioda.ObsSpace(metadata['obs file'])
    
    if channels:
        inputchans = get_input_channels(channels)
    else:
        inputchans = None
    
    
    df = gen_plot_df(obsspace, variable, plotType, inputchans)
    

    if plotType.startswith('spatial'):
        if channels:
            for channel in inputchans:
                
                df, plotvar, metadata = query_plot_type(df, variable, plotType, metadata, channel=channel)
                
                fig = diagnostics.spatial(df, metadata, variable=f'{plotvar}/{variable}_{channel}')
                # Save figure    
                fig.savefig(f"{metadata['outfig']}/spatial_{metadata['obs name']}_{variable}_{metadata['cycle']}_{channel}.png",
                            bbox_inches='tight', pad_inches=0.1)
                
        else:                
            df, plotvar, metadata = query_plot_type(df, variable, plotType, metadata)

            fig = diagnostics.spatial(df, metadata, variable=f'{plotvar}/{variable}')
        
            # Save figure    
            fig.savefig(f"{metadata['outfig']}/spatial_{metadata['obs name']}_{variable}_{metadata['cycle']}.png",
                        bbox_inches='tight', pad_inches=0.1)
            
    
    if plotType.startswith('binned_spatial'):
        if channels:
            for channel in inputchans:
                
                df, plotvar, metadata = query_plot_type(df, variable, plotType, metadata, channel=channel)
                
                binned_df = diagnostics.bin_df(df, variable=f'{plotvar}/{variable}_{channel}', dlat=5, dlon=5)
                fig = diagnostics.spatial_binned(binned_df, metadata)
                
                # Save figure    
                fig.savefig(f"{metadata['outfig']}/binned_spatial_{metadata['obs name']}_{variable}_{metadata['cycle']}_{channel}.png",
                            bbox_inches='tight', pad_inches=0.1)
                
        else:
            df, plotvar, metadata = query_plot_type(df, variable, plotType, metadata)

            binned_df = diagnostics.bin_df(df, variable=f'{plotvar}/{variable}', dlat=5, dlon=5)
            fig = diagnostics.spatial_binned(binned_df, metadata)
        
            # Save figure    
            fig.savefig(f"{metadata['outfig']}/binned_spatial_{metadata['obs name']}_{variable}_{metadata['cycle']}.png",
                        bbox_inches='tight', pad_inches=0.1)
        
    
    if plotType.startswith('scatter_hofx'):
        if channels:
            for channel in inputchans:   
                df, plotvar, metadata = query_plot_type(df, variable, plotType, metadata, channel=channel)
                fig = diagnostics.scatter(df[f"{plotvar[0]}/{variable}_{channel}"], df[f"{plotvar[1]}/{variable}_{channel}"], metadata)
                # Save figure    
                fig.savefig(f"{metadata['outfig']}/scatter_{metadata['obs name']}_{variable}_{metadata['cycle']}_{channel}.png",
                            bbox_inches='tight', pad_inches=0.1)
        else:
            df, plotvar, metadata = query_plot_type(df, variable, plotType, metadata)
            fig = diagnostics.scatter(df[f"{plotvar[0]}/{variable}"], df[f"{plotvar[1]}/{variable}"], metadata)
            
            # Save figure    
            fig.savefig(f"{metadata['outfig']}/scatter_{metadata['obs name']}_{variable}_{metadata['cycle']}.png",
                        bbox_inches='tight', pad_inches=0.1)
            
    if plotType.startswith('lineplot'):
        
        metadata['linestlye'] = '-'
        metadata['linewidth'] = '1'
        metadata['color'] = 'red'
        
        if channels:
            for channel in inputchans:
                df, plotvar, metadata = query_plot_type(df, variable, plotType, metadata, channel=channel)
                fig = diagnostics.scatter(df[f"{plotvar[1]}/{variable}_{channel}"].index,
                                          df[f"{plotvar[0]}/{variable}_{channel}"]-df[f"{plotvar[1]}/{variable}_{channel}"],
                                          metadata)
                # Save figure    
                fig.savefig(f"{metadata['outfig']}/lineplot_{metadata['obs name']}_{variable}_{metadata['cycle']}_{channel}.png",
                            bbox_inches='tight', pad_inches=0.1)
        else:
            df, plotvar, metadata = query_plot_type(df, variable, plotType, metadata)
            fig = diagnostics.scatter(df[f"{plotvar[1]}/{variable}"].index,
                                      df[f"{plotvar[0]}/{variable}"]-df[f"{plotvar[1]}/{variable}"],
                                      metadata)
        
            # Save figure    
            fig.savefig(f"{metadata['outfig']}/lineplot_{metadata['obs name']}_{variable}_{metadata['cycle']}.png",
                        bbox_inches='tight', pad_inches=0.1)
    
    
    return