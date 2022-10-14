#!/bin/bash
FLINKROOT=$(cd ..; pwd)
# $HADOOP_HOME and $HADOOP_CONF_DIR export by hadoop
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

#change hdfs-site.xml
sed -i 's/NUM_TO_BE_REPLACED/'"${#iplist[@]}"'/g' "$FLINKROOT"/hadoop-scripts/hdfs-site.xml

#configure workers
# delete and recreate the data folder for each vm
# change all the workers file in each vm
# change all the hdfs-site.xml files in each vm
for ip in "${iplist[@]}"
do
    printf '%s\n' '-----------------------------------------------------'
    echo "configuring on $ip"
    ssh "$ip" "rm -r "$HADOOP_HOME"/hadoop_data/hdfs/namenode"
    ssh "$ip" "rm -r "$HADOOP_HOME"/hadoop_data/hdfs/datanode"
    ssh "$ip" "mkdir "$HADOOP_HOME"/hadoop_data/hdfs/namenode"
    ssh "$ip" "mkdir "$HADOOP_HOME"/hadoop_data/hdfs/datanode"
    scp -r "$FLINKROOT"/hadoop-scripts/workers "$ip":"$HADOOP_CONF_DIR"/slaves
    scp -r "$FLINKROOT"/hadoop-scripts/masters "$ip":"$HADOOP_CONF_DIR"/masters
    scp -r "$FLINKROOT"/hadoop-scripts/hdfs-site.xml "$ip":"$HADOOP_HOME"/etc/hadoop/hdfs-site.xml
done

hdfs namenode -format
# start-all
.  "$HADOOP_HOME"/sbin/start-all.sh

