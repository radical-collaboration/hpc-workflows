Prepare docker for ENTK

```
docker run -d --name rabbitmq1 -P rabbitmq:3
```

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