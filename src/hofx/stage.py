from r2d2 import fetch
from solo.basic_files import mkdir
from solo.date import Hour, DateIncrement
from solo.logger import Logger
from solo.stage import Stage
import os

__all__ = ['background', 'fv3jedi', 'obs', 'diags']

def background(config):
    """
    background(config)
    stage model backgrounds based on
    input configuration 'config' dictionary
    """
    # get background time
    # NOTE: will below be handled in config already?
    bkg_time = Hour(config['cycle']) - DateIncrement(config['step_cycle'])
    # create directory
    mkdir(config['bkg']['bkg_dir'])
    # fetch the coupler file first
    fetch(
        type='fc',
        model='gfs_metadata',
        experiment=config['bkg']['bkg_exp'],
        date=bkg_time,
        step=config['bkg']['background_steps'],
        resolution=config['model_resolution'],
        user_date_format='%Y%m%d.%H%M%S',
        fc_date_rendering='analysis',
        database=config['bkg']['bkg_db'],
        target_file=f"{config['bkg']['bkg_dir']}/$(valid_date).coupler.res",
        #full_report  = 'yes',
        #report = f"fetch_gfs_metadata_{config['cycle']}.yaml",
    )
    # fetch the tile files
    fetch(
        type='fc',
        model='gfs',
        experiment=config['bkg']['bkg_exp'],
        date=bkg_time,
        step=config['bkg']['background_steps'],
        resolution=config['model_resolution'],
        user_date_format='%Y%m%d.%H%M%S',
        fc_date_rendering='analysis',
        database=config['bkg']['bkg_db'],
        target_file=f"{config['bkg']['bkg_dir']}/$(valid_date).$(file_type).tile$(tile).nc",
        tile=config['bkg']['bkg_tiles'],
        file_type=['fv_core.res', 'fv_srf_wnd.res', 'fv_tracer.res', 'phy_data', 'sfc_data'],
        #full_report  = 'yes',
        #report = f"fetch_gfs_{config['cycle']}.yaml",
    )

def diags(config):
    """
    diags(config)
    stage diags based on
    input configuration 'config' dictionary
    """
    # create directory
    directory = config['diags']['diag_dir']
    mkdir(directory)
    # loop through designated observations
    for ob in config['diags']['observations']:
        obname = ob['obs space']['name'].lower()
        outfile = os.path.basename(ob['obs space']['obsdataout']['obsfile'])
        outpath = os.path.join(directory, outfile)
        fetch(
            type='diag',
            experiment=config['experiment'],
            date=config['window begin'],
            model='gfs',
            obs_type=obname.lower(),
            target_file=outpath,
            database=config['diags']['archive_db'],
        )

def obs(config):
    """
    obs(config)
    stage observations based on
    input configuration 'config' dictionary
    """
    # create directory
    mkdir(config['obs']['obs_dir'])
    # loop through designated observations
    for ob in config['obs']['observations']:
        obname = ob['obs space']['name'].lower()
        outfile = ob['obs space']['obsdatain']['obsfile']
        # try to grab obs
        fetch(
            type='ob',
            provider=config['obs']['obs_src'],
            experiment=config['obs']['obs_dump'],
            date=config['window begin'],
            obs_type=obname,
            time_window=config['window_length'],
            target_file=outfile,
            ignore_missing=True,
            database=config['obs']['obs_db'],
            #full_report  = 'yes',
            #report = f"fetch_{obname}_{config['window begin']}.yaml",
        )
        # try to grab bias correction files too
        if 'obs bias' in ob:
            satbias = ob['obs bias']['input file']
            fetch(
                type='bc',
                provider=config['obs']['bc_src'],
                experiment=config['obs']['bc_dump'],
                date=config['cycle'],
                obs_type=obname,
                target_file=satbias,
                file_type='satbias',
                ignore_missing=True,
                database=config['obs']['obs_db'],
                #full_report  = 'yes',
                #report = f"fetch_satbias_{obname}_{config['window begin']}.yaml",
            )
            # below is lazy but good for now...
            tlapse = satbias.replace('satbias.nc4', 'tlapse.txt')
            fetch(
                type='bc',
                provider=config['obs']['bc_src'],
                experiment=config['obs']['bc_dump'],
                date=config['cycle'],
                obs_type=obname,
                target_file=tlapse,
                file_type='tlapse',
                ignore_missing=True,
                database=config['obs']['obs_db'],
                #full_report  = 'yes',
                #report = f"fetch_tlapse_{obname}_{config['window begin']}.yaml",
            )

def fv3jedi(config):
    """
    fv3jedi(config)
    stage fix files needed for FV3-JEDI
    such as akbk, fieldsets, fms namelist, etc.
    uses input config dictionary for paths
    """
    # create output directory
    mkdir(config['fv3jedi']['stage_dir'])
    # call solo.Stage
    path = os.path.dirname(config['fv3jedi']['fv3jedi_stage'])
    stage = Stage(path, config['fv3jedi']['stage_dir'], config['fv3jedi']['fv3jedi_stage_files'])
