#!/bin/bash
export NODE_ROOT=$(cd ../..; pwd)
echo $NODE_ROOT
export FLINKROOT=$(cd ..; pwd)
echo $FLINKROOT

localip=$(hostname -I)
# localip=${$localip//\n/}

printf '%s\n' $localip

iplist=()

# use our yaml, workers, masters in conf/
cp "$FLINKROOT"/deploy-scripts/* "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/conf/
cd "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/bin
./stop-cluster.sh

# add hadoop pkg
cp $NODE_ROOT/commons-cli-1.5.0.jar  $FLINKROOT/build-target/lib/
cp $NODE_ROOT/flink-shaded-hadoop-3-uber-3.1.1.7.2.9.0-173-9.0.jar  $FLINKROOT/build-target/lib/

# clean jobmaster log files before copy files to taskmanagers
rm "$FLINKROOT"/build-target/log/*

# deploy workers
cd "$FLINKROOT"/deploy-scripts/
while IFS= read -r line; do
  ip="$line"
  printf '%s\n' $ip
  iplist+=("$line")
done < workers

#remove useless jars
rm -rf "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/examples

for ip in "${iplist[@]}"
do
  if [[ $ip != $localip ]]; then
    printf '%s\n' '-----------------------------------------------------'
    echo $ip
    ssh "$ip" "rm -rf "$FLINKROOT""
    ssh "$ip" "mkdir "$FLINKROOT""
    ssh "$ip" "mkdir "$FLINKROOT"/flinkstate/"
    ssh "$ip" "mkdir "$FLINKROOT"/flink-dist/"
    ssh "$ip" "mkdir "$FLINKROOT"/flink-dist/target"
    scp -r "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/ "$ip":"$FLINKROOT"/flink-dist/target/
  fi
done

# start cluster
cd "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/bin
./start-cluster.sh

