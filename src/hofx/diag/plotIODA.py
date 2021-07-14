import numpy as np
import pandas as pd
import xarray as xr
import os
import ioda

import sys
sys.path.append('/scratch1/NCEPDEV/da/Kevin.Dougherty/hofxcs/src/hofx')

from diag import diagnostics

def create_df(dic):
    """
    Create a dataframe from dictionary of data.
    """
    df = pd.DataFrame(dic)

    return df

def create_dict(dic, data, variable, inputchans=None, chanCoords=None):
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
         'gsiomf': ['ObsValues', 'GsiHofXBc'],
         'ufoomf': ['ObsValues', 'hofx'],
         'ufocounts': ['hofx'],
         'gsicounts': ['GsiHofxBc'],
         'obscounts': ['ObsValues'],
         'ufo': ['hofx'],
         'gsi': ['GsiHofX'],
         'obs': ['ObsValues']
        }

    plotType_components = plotType.split('_')
    plotvar = plotType_components[-1]
    
    # Gets appropriate variables based on plot type
    plotgroups = d[plotvar]
    
    plot_dict = {}
    
    # loop through variable(s) to get all data needed
    for group in plotgroups:
        inVar = group + '/' + variable
        data = get_data(obsspace, inVar)
        
        ### Figure this out once finished with logic of function ###
        if variable == 'brightness_temperature':
            chanCoords = get_indexed_channels(obsspace)
            plot_dict = create_dict(plot_dict, data, variable=inVar, inputchans=inputchans, chanCoords=chanCoords)
            
        
    # Grab lat lons
    lats, lons = get_lat_lon(obsspace)
    
    plot_dict = create_dict(plot_dict, lats, variable='latitude')
    plot_dict = create_dict(plot_dict, lons, variable='longitude')
    
    df = create_df(plot_dict)

    return df 

def query_plot_type(df, variable, plotType, channel=None):
    
    
    if plotType.endswith('hofxdiff'):
        plotvar = 'hofxdiff'
        if channel:
            df[f'hofxdiff/{variable}_{channel}'] = df[f'GsiHofXBc/{variable}_{channel}'] - df[f'hofx/{variable}_{channel}']
        else:
            df[f'hofxdiff/{variable}'] = df[f'GsiHofXBc/{variable}_{channel}'] - df[f'hofx/{variable}']

    elif plotType.endswith('gsiomf'):
        plotvar = 'omf'
        if channel:
            df[f'omf/{variable}_{channel}'] = df[f'ObsValues/{variable}_{channel}'] - df[f'GsiHofXBc/{variable}_{channel}']
        else:
            df[f'omf/{variable}'] = df[f'ObsValues/{variable}'] - df[f'GsiHofXBc/{variable}']

    elif plotType.endswith('ufoomf'):
        plotvar = 'omf'
        if channel:
            df[f'omf/{variable}_{channel}'] = df[f'ObsValues/{variable}_{channel}'] - df[f'hofx/{variable}_{channel}']
        else:
            df[f'omf/{variable}'] = df[f'ObsValues/{variable}'] - df[f'hofx/{variable}']

    elif plotType.endswith('gsi'):
        plotvar = 'GsiHofXBc'
        
    elif plotType.endswith('ufo'):
        plotvar = 'hofx'
    
    elif plotType.endswith('obs'):
        plotvar = "ObsValues"
        
    else:
        raise TypeError('Plot variable is not recognized. Please enter valid plot variable.')
        
    return df, plotvar

def gen_spatial(df, variable, metadata, channels=None):
    
    if channels:        
        for channel in channels:

            # Spatial of specific variable
            fig = diagnostics.spatial(df, metadata, variable=f'{variable}_{channel}')

def genDiagnostics(file, variable, plotType, channels=None):
    
    obsspace = ioda.ObsSpace(file)
    
    if channels:
        inputchans = get_input_channels(channels)
    else:
        inputchans = None
    
    
    df = gen_plot_df(obsspace, variable, plotType, inputchans)
    

    if plotType.startswith('spatial'):
        if channels:
            for channel in inputchans:
                
                df, plotvar = query_plot_type(df, variable, plotType, channel=channel)
                
                metadata = {'title': 'title',
                            'cycle': 'cycle',
                            'cmap': 'viridis',
                            'vmax': None,
                            'vmin': None,
                            'label': 'label',
                            'outfig': f'sample_figure.png'}
                
                fig = diagnostics.spatial(df, metadata, variable=f'{plotvar}/{variable}_{channel}')
                fig.savefig(metadata['outfig'], bbox_inches='tight', pad_inches=0.1)
                
        else:                
            df, plotvar = query_plot_type(df, variable, plotType)

            metadata = {'title': 'title',
                        'cycle': 'cycle',
                        'cmap': 'viridis',
                        'vmax': None,
                        'vmin': None,
                        'label': 'label',
                        'outfig': f'sample_figure.png'}

            fig = diagnostics.spatial(df, metadata, variable=f'{plotvar}/{variable}')
            fig.savefig(metadata['outfig'], bbox_inches='tight', pad_inches=0.1)
            
    
    if plotType.startswith('binned_spatial'):
        if channels:
            for channel in inputchans:
                
                df, plotvar = query_plot_type(df, variable, plotType, channel=channel)
                
                metadata = {'title': 'title',
                            'cycle': 'cycle',
                            'cmap': 'viridis',
                            'vmax': None,
                            'vmin': None,
                            'label': 'label',
                            'outfig': f'sample_figure.png'}
                
                binned_df = diagnostics.bin_df(df, variable=f'{plotvar}/{variable}_{channel}', dlat=5, dlon=5)
                fig = diagnostics.spatial_binned(binned_df, metadata, variable=f'{plotvar}/{variable}_{channel}')
                fig.savefig(metadata['outfig'], bbox_inches='tight', pad_inches=0.1)
                
        else:
            df, plotvar = query_plot_type(df, variable, plotType)
                
            metadata = {'title': 'title',
                        'cycle': 'cycle',
                        'cmap': 'viridis',
                        'vmax': None,
                        'vmin': None,
                        'label': 'label',
                        'outfig': f'sample_figure.png'}

            binned_df = diagnostics.bin_df(df, variable=f'{plotvar}/{variable}', dlat=5, dlon=5)
            fig = diagnostics.spatial_binned(binned_df, metadata, variable=f'{plotvar}/{variable}')
            fig.savefig(metadata['outfig'], bbox_inches='tight', pad_inches=0.1)       
    
    
    return
