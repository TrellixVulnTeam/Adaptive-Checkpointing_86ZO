#!/bin/bash
export FLINKROOT=$(builtin cd ..; pwd)
echo $FLINKROOT

localip=$(hostname -I)
# localip=${$localip//\n/}

printf '%s\n' $localip

iplist=()

# use our yaml, workers, masters in conf/
cp "$FLINKROOT"/deploy-scripts/* "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/conf/
cd "$FLINKROOT"/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/bin
./stop-cluster.sh

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

