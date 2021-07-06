from r2d2 import store
from solo.date import Hour, DateIncrement
import os
import glob

__all__ = ['diags']

def diags(config):
    """
    diags(config)
    archive JEDI IODA diagnostic files
    into a R2D2 database based on an
    input configuration 'config' dictionary
    """
    for ob in config['diags']['observations']:
        obname = ob['obs space']['name'].lower()
        # get output file, assumed to be already concatenated
        diagfile = ob['obs space']['obsdataout']['obsfile']
        store(
            type='diag',
            experiment=config['experiment'],
            date=config['window begin'],
            model='gfs',
            obs_type=obname.lower(),
            source_file=diagfile,
            database=config['diags']['archive_db'],
        )
