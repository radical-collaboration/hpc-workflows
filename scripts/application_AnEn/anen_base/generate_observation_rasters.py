import argparse
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import STAP
from rpy2.robjects.packages import importr

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--folder_prefix'),
    parser.add_argument('--folder_accumulate'), 
    parser.add_argument('--folder_output'), 
    parser.add_argument('--folder_raster_anen'),
    parser.add_argument('--folder_tmp')
    parser.add_argument('--folder_raster_obs')
    parser.add_argument('--num_times_to_compute')
    parser.add_argument('--num_flts')    
    parser.add_argument('--file_observations')
    parser.add_argument('--test_ID_start')
    parser.add_argument('--xgrids_total')
    parser.add_argument('--ygrids_total')

    args = parser.parse_args()

    # Read evaluation functions from R function
    with open('generate_observation_rasters.R', 'r') as f:
        R_code = f.read()
    generate_observation_rasters = STAP(R_code, 'generate_observation_rasters')
    ncdf4 = importr("ncdf4")
    raster = importr("raster")
    generate_observation_rasters.generate_observation_rasters(  
                                                                args.folder_prefix, 
                                                                args.folder_accumulate, 
                                                                args.folder_output, 
                                                                args.folder_raster_anen,
                                                                args.folder_tmp,
                                                                args.folder_raster_obs,
                                                                args.num_times_to_compute,
                                                                args.num_flts,
                                                                args.file_observations,
                                                                args.test_ID_start,
                                                                args.xgrids_total,
                                                                args.ygrids_total)
