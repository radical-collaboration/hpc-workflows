Prepare docker for ENTK

```
docker ps
docker rm [name]
docker run -d --name rabbitmq1 -P rabbitmq:3
```

If you have already installed docker but it is not running, for Linux, try

```
service docker stop
```

You might need root permission to run this command.

Prepare env variable for ENTK

```
export RADICAL_PILOT_DBURL="mongodb://138.201.86.166:27017/ee_exp_4c"
export GLOBUS_LOCATION="/Library/Globus/"
export RP_ENABLE_OLD_DEFINES=True
```

Don't run jobs on loggin node; run it on computing nodes:
```
qsub -I -l walltime=00:30:00,nodes=1:ppn=20 -A TG-MCB090174
```

To start a rabbit mq
```
docker run -d --name rabbit-1 -p 32773:5672 rabbitmq:3
```
