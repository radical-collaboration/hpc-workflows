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
    parser.add_argument('--num_flts')
    parser.add_argument('--num_pixels_increase')
    parser.add_argument('--num_times_to_compute')
    parser.add_argument('--members_size')
    parser.add_argument('--threshold_triangle')
    parser.add_argument('--pixels_computed_file')

    args = parser.parse_args()


    with open(args.pixels_computed_file,'r') as fh:
        pixels_computed = fh.readlines()[0].strip()

    pixels_computed = [k for k in pixels_computed.split(' ')]

    with open('func_define_pixels.R', 'r') as f:
        R_code = f.read()

    ncdf4 = importr("ncdf4")
    raster = importr("raster")
    deldir = importr("deldir")
    stringr = importr("stringr")
    spatstat = importr("spatstat") 
    maptools = importr("maptools")
    RAnEnExtra = importr("RAnEnExtra")

    define_pixels = STAP(R_code, 'define_pixels')
    define_pixels.define_pixels(
            args.iteration, args.folder_raster_obs, args.folder_accumulate,
            args.folder_triangles, pixels_computed, args.xgrids_total,
            args.ygrids_total, args.num_flts, args.num_pixels_increase,
            args.num_times_to_compute, args.members_size, args.threshold_triangle)
