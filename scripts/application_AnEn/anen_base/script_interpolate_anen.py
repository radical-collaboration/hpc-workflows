import argparse
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import STAP
from rpy2.robjects.packages import importr

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            description='Parse arguments for AnEn interpolation')
    parser.add_argument('--file_anen_accumulate_iteration')
    parser.add_argument('--prefix_anen_raster')
    parser.add_argument('--file_pixels_accumulated')
    parser.add_argument('--num_flts')
    parser.add_argument('--num_times_to_compute')
    parser.add_argument('--members_size')
    parser.add_argument('--num_neighbors')
    parser.add_argument('--xgrids_total')
    parser.add_argument('--ygrids_total')

    args = parser.parse_args()
    
    with open(args.file_pixels_accumulated, 'r') as fh:
        pixels_computed = fh.readlines()[0].strip()

    pixels_computed = [k for k in pixels_computed.split(' ')]

    with open('func_interpolate_anen.R', 'r') as f:
        R_code = f.read()

    ncdf4 = importr("ncdf4")
    raster = importr("raster")
    raster = importr("RAnEnExtra")

    interpolate_anen = STAP(R_code, 'interpolate_anen')
    interpolate_anen.interpolate_anen(
            args.file_anen_accumulate_iteration,
            args.prefix_anen_raster, pixels_computed,
            args.num_times_to_compute, args.num_flts,
            args.members_size, args.num_neighbors,
            args.xgrids_total, args.ygrids_total)
