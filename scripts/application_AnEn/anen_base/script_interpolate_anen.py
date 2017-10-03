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
    parser.add_argument('--pixels_computed')
    parser.add_argument('--num_flts')
    parser.add_argument('--num_times_to_compute')
    parser.add_argument('--members_size')
    parser.add_argument('--num_neighbors')
    parser.add_argument('--xgrids_total')
    parser.add_argument('--ygrids_total')

    args = parser.parse_args()

    with open('func_interpolate_anen.R', 'r') as f:
        R_code = f.read()

    ncdf4 = importr("ncdf4")
    raster = importr("raster")
    raster = importr("RAnEnExtra")

    interpolate_anen = STAP(R_code, 'func_interpolate_anen')
    interpolate_anen.interpolate_anen(
            args.file_anen_accumulate_iteration,
            args.prefix_anen_raster, args.pixels_computed,
            args.num_fts, args.num_times_to_compute,
            args.members_size, args.num_neighbors,
            args.xgrids_total, args.ygrids_total)
