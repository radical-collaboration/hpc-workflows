
from rpy2.robjects.packages import STAP
import rpy2
import rpy2.robjects as robjects
import argparse

if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--file_observation')
    parser.add_argument('--file_AnEn')
    parser.add_argument('--stations_ID')
    parser.add_argument('--test_ID_start')
    parser.add_argument('--test_ID_end')
    parser.add_argument('--nflts')
    parser.add_argument('--nrows')
    parser.add_argument('--ncols')

    args = parser.parse_args()

    raw_station_id = args.stations_ID.split(',')
    proc_station_id = list()

    for val in raw_station_id:
         proc_station_id.append(int((val.strip().replace("[","").replace("u","").replace("]","").replace("'","")).strip()))

    # Read evaluation functions from R function
    with open('evaluation.R', 'r') as f:
        R_code = f.read()
    evaluation = STAP(R_code, 'evaluation')
    stations_ID = evaluation.evaluate(    args.file_observation,
                                            args.file_AnEn,
                                            robjects.IntVector(proc_station_id),
                                            float(args.test_ID_start), float(args.test_ID_end),
                                            int(args.nflts),
                                            int(args.nrows), int(args.ncols))

    if len(stations_ID) is not 0:
        print stations_ID