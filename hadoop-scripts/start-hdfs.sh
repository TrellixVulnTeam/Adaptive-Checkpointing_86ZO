#!/bin/bash
FLINKROOT=$(cd ..; pwd)
HADOOP_HOME=/usr/local/hadoop
HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop

# stop all the nodes
. $HADOOP_HOME/sbin/stop-all.sh

iplist=()
# get workers
cd "$FLINKROOT"/hadoop-scripts/ || (echo "cd fail" && exit 1)
while IFS= read -r line; do
  ip="$line"
  printf '%s\n' $ip
  iplist+=("$line")
done < workers

#configure workers
# delete and recreate the data folder for each vm
# change all the workers file in each vm
for ip in "${iplist[@]}"
do
  if [[ $ip != $localip ]]; then
    printf '%s\n' '-----------------------------------------------------'
    echo "configuring on $ip"
    ssh "$ip" "rm -r "$HADOOP_HOME"/hadoop_data/hdfs/namenode"
    ssh "$ip" "rm -r "$HADOOP_HOME"/hadoop_data/hdfs/datanode"
    ssh "$ip" "mkdir "$HADOOP_HOME"/hadoop_data/hdfs/namenode"
    ssh "$ip" "mkdir "$HADOOP_HOME"/hadoop_data/hdfs/datanode"
    scp -r "$HADOOP_CONF_DIR"/workers "$ip":"$HADOOP_CONF_DIR"/workers
  fi
done

hdfs namenode -format
# start-all
.  $HADOOP_HOME/sbin/start-all.sh

