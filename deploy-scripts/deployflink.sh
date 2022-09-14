#!/bin/bash
FLINKROOT=$(cd ..; pwd)
echo "FLINKROOT: $FLINKROOT"

#localip=$(hostname -I)
# localip=${$localip//\n/}

#printf '%s\n' $localip

iplist=()

# use our yaml, workers, masters in conf/
cp "$FLINKROOT"/deploy-scripts/* "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/conf/
cd "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/bin
./stop-cluster.sh

# clean jobmaster log files before copy files to taskmanagers
rm "$FLINKROOT"/build-target/log/*

# deploy workers
cd "$FLINKROOT"/deploy-scripts/
prev="" # filter same ip
while IFS= read -r line; do
  ip="$line"
  printf '%s\n' $ip
  if [ ! -z "$ip" ]; then
    if [ "$ip" != prev ]; then
      iplist+=("$ip")
    fi
    prev=ip;
  fi
done < workers

#remove useless jars
rm -rf "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/examples

for ip in "${iplist[@]}"
do
  if [[ $ip != "flinknode-1" ]]; then
    printf '%s\n' '-----------------------------------------------------'
    echo "deploying on $ip"
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

