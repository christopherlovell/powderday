import numpy as np
import config as cfg


def variable_set():
    try:
        cfg.par.FORCE_RANDOM_SEED
    except:
        cfg.par.FORCE_RANDOM_SEED  = None

    try:
        cfg.par.BH_SED
    except:
        cfg.par.BH_SED  = None

    try:
        cfg.par.IMAGING
    except:
        cfg.par.IMAGING  = None

    try:
        cfg.par.SED
    except:
        cfg.par.SED = True

    try:
        cfg.par.IMAGING_TRANSMISSION_FILTER
    except:
        cfg.par.IMAGING_TRANSMISSION_FILTER = False

    try:
        cfg.par.SED_MONOCHROMATIC
    except:
        cfg.par.SED_MONOCHROMATIC = False

    try:
        cfg.par.SKIP_RT
    except:
        cfg.par.SKIP_RT = False


    try:
        cfg.par.FIX_SED_MONOCHROMATIC_WAVELENGTHS 
    except:
        cfg.par.FIX_SED_MONOCHROMATIC_WAVELENGTHS = True


    try:
        cfg.par.n_MPI_processes
    except:
        cfg.par.n_MPI_processes = cfg.par.n_processes #default is to make the same as the number of pool processes

    return cfg.par.FORCE_RANDOM_SEED,cfg.par.BH_SED,cfg.par.IMAGING,cfg.par.SED,cfg.par.IMAGING_TRANSMISSION_FILTER,cfg.par.SED_MONOCHROMATIC,cfg.par.SKIP_RT,cfg.par.FIX_SED_MONOCHROMATIC_WAVELENGTHS,cfg.par.n_MPI_processes