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

RabbitMQ has been installed using docker.

```
# Print the local available containers
docker ps

# Run the RabbitMQ container
docker run -d --name rabbitmq -P rabbitmq:3
```

Because setting up RabbitMQ on Cheyenne can be hussle. I directly used Vivek's service.

```
AppManager(hostname='two.radical-project.org', port=33239)
```

I also need MongoDB, which I set up on Mlab.

```
export RADICAL_PILOT_DBURL='mongo url'
```


To use EnTK on Cheyenne, I need to checkout the specific branch with Cheyenne features.

```
git clone https://github.com/radical-cybertools/radical.pilot
cd radical.pilot/
git checkout feature/cheyenne
pip install . --upgrade
cd ..

git clone https://github.com/radical-cybertools/saga-python
cd saga-python/
git checkout feature/cheyenne
pip install . --upgrade
```

MongoDB needs to be set up. The following setting should be in environment variables.

```
export RADICAL_PILOT_DBURL="mongodb://<dbuser>:<dbpassword>@ds058579.mlab.com:58579/wuh20"
```

## Setting up Open-SSh on Ubuntu Bionic

To have Open-SSh set up, we need the following dependency:

- Globus Toolkit
- myproxy
- gloxbus-proxy-utils
- globux-simple-ca
- gsi-openssh-clients

First, install the latests Globus Toolkit from [Globus Toolkit website](http://toolkit.globus.org/toolkit/downloads/latest-stable/). By doing this, you should see the additional repostiory file from `Globus` added into the folder `/etc/apt/sources.list.d`.

Then install the other dependencies.

```
sudo apt-get update
sudo apt-get install myproxy myproxy-server myproxy-admin
sudo apt-get install globus-proxy-utils globus-simple-ca
sudo apt-get install gsi-openssh-clients
```

[reference](https://github.com/vivek-bala/docs/blob/master/misc/gsissh_setup_stampede_ubuntu_xenial.sh)

By now, you should have `gsissh` ready.

To set up `gsissh` access to XSEDE supercomputers, we need to prepare certificates locally.

```
# Create a folder to store the certificates.
mkdir ~/.globus
cd ~/.globus
wget https://software.xsede.org/security/xsede-certs.tar.gz
tar xvf xsede-certs.tar.gz
rm xsede-certs.tar.gz

# Generate certificate locally
myproxy-logon -s myproxy.xsede.org -l <username>
```

By now you should have passwordless access to supercomputers. Try the following command to test it:

```
# gsissh should be connected using the port 2222.
# Let's try to connect to stampede2. You should not be asked for password.
#
gsissh -p 2222 stampede2.tacc.xsede.org
```

**gsissh to Comet and SuperMIC is not working.**


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