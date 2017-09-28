import argparse
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import STAP
from rpy2.robjects.packages import importr

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers')
    parser.add_argument('--iteration')
    parser.add_argument('--folder_raster_obs')
    parser.add_argument('--folder_accumulate')
    parser.add_argument('--folder_triangles')
    parser.add_argument('--pixels_computed')
    parser.add_argument('--xgrids_total')
    parser.add_argument('--ygrids_total')
    parser.add_argument('--test_ID_start')
    parser.add_argument('--num_flts')
    parser.add_argument('--num_pixels_increase')
    parser.add_argument('--num_times_to_compute')
    parser.add_argument('--members_size')
    parser.add_argument('--threshold_triangle')

    args = parser.parse_args()

    with open('func_define_pixels.R', 'r') as f:
        R_code = f.read()
    define_pixels = STAP(R_code, 'define_pixels')

    raster = importr("raster")
    deldir = importr("deldir")
    spatstat = importr("spatstat") 
    maptools = importr("maptools")
    RAnEnExtra = importr("RAnEnExtra")

    define_pixels.define_pixels(
            args.iteration, args.folder_raster_obs, args.folder_accumulate,
            args.triangles, args.pixels_computed, args.xgrids_total,
            args.ygrids_total, args.test_ID_start, args.num_flts,
            args.num_pixels_increase, args.num_times_to_compute,
            args.members_size, args.threshold_triangle)