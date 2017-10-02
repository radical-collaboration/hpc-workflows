import os, sys, traceback, rpy2

'''
functions for parsing and checking the arguments from func_setup.R
'''

def test_initial_config(d):

    possible_keys = [
            'command.exe', 'command.verbose', 'file.forecasts',
            'file.observations', 'file.pixels.computed', 'folder.prefix',
            'folder.accumulate', 'folder.output', 'folder.raster.anen',
            'folder.raster.obs', 'folder.local', 'folder.triangles',
            'num.flts', 'num.times', 'num.times.to.compute',
            'num.parameters', 'ygrids.total', 'xgrids.total',
            'grids.total', 'init.num.pixels.compute',
            'yinterval', 'ycuts', 'quick', 'cores', 'rolling',
            'observation.ID', 'train.ID.start', 'train.ID.end',
            'test.ID.start', 'test.ID.end', 'weights', 'members.size',
            'num.neighbors', 'init.iteration', 'threshold.triangle',
            'num.pixels.increase', 'debug', 'pixels.compute']

    all_ok = True

    for keys in possible_keys:

        if keys not in d:

            print 'Expected key %s not in initial_config dictionary'%keys
            all_ok = False

    return all_ok


def process_initial_config(initial_config):

    # arguments treated as lists with integer elements
    keys_list_int = ['pixels.compute', 'ycuts']

    # arguments treated as lists with float elements
    keys_list_float = ['weights']

    # arguments treated as double
    keys_float = ['threshold.triangle']

    # arguments treated as string
    keys_str = [
            'command.exe', 'command.verbose',
            'folder.raster.obs', 'folder.local',
            'folder.prefix', 'folder.accumulate',
            'folder.output', 'folder.raster.anen',
            'file.forecasts', 'file.observations',
            'file.pixels.computed', 'folder.triangles']

    # arguments treated as integer
    keys_int = [
            'grids.total', 'init.num.pixels.compute', 'yinterval',
            'members.size', 'num.neighbors', 'init.iteration',
            'num.parameters', 'ygrids.total', 'xgrids.total',
            'num.flts', 'num.times', 'num.times.to.compute',
            'quick', 'cores', 'rolling', 'observation.ID',
            'train.ID.start', 'train.ID.end',
            'test.ID.start', 'test.ID.end',
            'num.pixels.increase', 'debug']

    for key in keys_list_int:
        initial_config[key] = [int(k) for k in list(initial_config[key])]

    for key in keys_list_float:
        initial_config[key] = [float(k) for k in list(initial_config[key])]

    for key in keys_str:
        initial_config[key] = initial_config[key][0]

    for key in keys_int:
        initial_config[key] = int(initial_config[key][0])

    for key in keys_float:
        initial_config[key] = float(initial_config[key][0])

    # wrap up check for types
    for key, val in initial_config.iteritems():
        if type(val) not in [str, int, float, list]:
            sys.exit(1)

    return initial_config



