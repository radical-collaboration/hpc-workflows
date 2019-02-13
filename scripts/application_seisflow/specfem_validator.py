import math
import sys

if __name__ == '__main__':

    output_solver_txt = sys.argv[1]

    if not os.path.exists(output_solver_txt):
        return 1

    # check no NAN values in output_solver.txt. If there are,
    # then the simulation failed.
    unstable_flag = False
    with open(output_solver_txt) as fh:
        content = [line.rstrip() for line in fh]

    for line in content:
        if "Max of strain, eps_trace_over_3_crust_mantle" in line:
            v = float(line.split()[-1])
            if math.isnan(v) or math.isinf(v):
                unstable_flag = True
        if "Max of strain, epsilondev_crust_mantle" in line:
            v = float(line.split()[-1])
            if math.isnan(v) or math.isinf(v):
                unstable_flag = True

    if unstable_flag:
        return 1

    if "End of the simulation" not in content[-2]:
        return 1

    return 0