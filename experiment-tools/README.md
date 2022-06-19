# Build Job
```shell
cd expeirment-tools/
```

- Each experiment contains a Query and at least one Source.
- The jar package will be placed in the target/ folder of the current directory. 
- If there is a jar in the folder and you didn't modify the code, you can skip the build step and submit the job directly.

- For Query1 and 5 you need to run commands to package the corresponding Query, as well as the BidSource.
- For Query3 and 8 you need to run commands to package the corresponding Query, as well as the PersonSource and AuctionSource.

## Build KafkaSourceJob
```shell
sh build-all.sh # build all source and query jobs at oncw
```
```shell
sh build.sh b # build BidSource
sh build.sh a # build AuctionSource
sh build.sh p # build PersonSource
```
## Build Query
```shell
sh build.sh 1 # Build Query1
sh build.sh 3 # Build Query3
sh build.sh 5 # Build Query5
sh build.sh 8 # Build Query8
```
# Start Experiment
```shell
vim argsconfig.sh # change configs such as ratelist in this file
```
The script will automatically submit the jars of Query and its Source, just specify the Query to run.
```shell
sh start-exp.sh 1 # start Query1
sh start-exp.sh 3 # start Query3
sh start-exp.sh 5 # start Query5
sh start-exp.sh 8 # start Query8
```
# stop Experiment
