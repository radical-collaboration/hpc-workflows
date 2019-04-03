import os
import sys
import yaml
import argparse
from helpers.utils import get_files_dims, expand_tilde, write_config_files


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='This program generates spatially decomposed configuration files \
            (.cfg) for analog generation.\nThe configuration file generated contains file names and start/count indices. \
            An input configuration file is required. Please refer to the configuration template file.')

    parser.add_argument('--cfg', help='Path to the configuration file', required=True)

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)

    if not os.path.isfile(args.cfg):
        print '%s does not exist' % args.cfg
        sys.exit(1)

    with open(args.cfg, 'r') as fp:
        cfg = yaml.load(fp, Loader=yaml.FullLoader)

    cfg = expand_tilde(cfg)

    files_dims = list()
    write_config_files('day-analog-similarity', cfg['global'], files_dims)
    sys.exit(0)

    files_dims = get_files_dims(cfg['global'])

    if write_config_files('search-forecasts', cfg['global'], files_dims):
        print "Successfully generated search forecast configuration!"
    else:
        sys.exit(1)

    if write_config_files('test-forecasts', cfg['global'], files_dims):
        print "Successfully generated test forecast configuration!"
    else:
        sys.exit(1)

    if write_config_files('observations', cfg['global'], files_dims):
        print "Successfully generated observation configuration!"
    else:
        sys.exit(1)

    print "Configurations are generated!"
    sys.exit(0)

