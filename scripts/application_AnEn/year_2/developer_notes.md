# Developer's Notes

The latest document can be found at [here](https://radicalentk.readthedocs.io/en/latest/)

```
cd ~/storage/virtual-envs/env-entk-test

# Activate environment
source bin/activate

# Install the EnTk package
pip install radical.ensemblemd radical.entk

# Deactivate environment
deactivate
```

RabitMQ has been installed using docker.

```
# Print the local available containers
docker ps

# Run the RabitMQ container
docker run -d --name rabitmq -P rabbitmq:3
```


## Old Notes

### After creating a .ssh/config file, when run `ssh mach1`, get error `Bad owner or permission`

The config file requires rw for user only permission. Use the following command to fix it


`chmod 600 ~/.ssh/config`


### mongo db instances are restricted and I am the admin

To connect to the database, use the following username and password

`mongo -u weiming -p 54Eka?vN`


### Deal with multiple python versions

Because I have three versions of python (2.6, 2.7, 3.5), the version of python used when creating virtual environment should be specified. Use the following command line.

`python27 -m virtualenv [path to folder]`

But it seems like executable python26 will by default be created in the environment, so if we want to use python27, pay attention to the command used for this. Check the name. Is it `python27` or `python2.7` in directory `bin/`. Use the following command lines.

```
python2.7 -m pip list
RADICAL_VERBOSE=REPORT python2.7 [file]
```