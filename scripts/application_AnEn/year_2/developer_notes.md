## Necessary Environment Variables

export RADICAL_ENTK_VERBOSE=INFO

Install Radical EnTK on Cheyenne

```
# prepare VE
module purge && module load python/2.7.15
virtualenv venv
source venv/bin/activate

# Install entk and dependencies
pip install radical.entk pyyaml netcdf4

# replace RP version
git clone https://github.com/radical-cybertools/radical.pilot.git
cd radical.pilot
git checkout fix/cheyenne
pip uninstall -y radical.pilot
pip install .

# verify installation
python -V
radical-stack
```

## Documentation

- [Resources for NCAR](https://github.com/radical-cybertools/radical.pilot/blob/devel/src/radical/pilot/configs/resource_ncar.json)
- [EnTK doc](https://radicalentk.readthedocs.io/en/latest/)


# Common Issues and Debugging

### Spot whether tasks are running on the same node

You can check the `mpirun` command and the ID associated with it. The ID indicates the node ID where the task runs.
