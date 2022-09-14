#!/bin/bash
iplist=()
while IFS= read -r line; do
  ip="$line"
  if [[ (! -z "$ip") && ($ip != "flinknode-1") ]]; then
    iplist+=("$ip")
  fi
done < workers

for ip in "${iplist[@]}"
do
  echo "copy hadoop to $ip"
  scp -r ~/.bashrc "$ip":~/
  ssh "$ip" "source  ~/.bashrc"
  scp -r "$HADOOP_HOME" "$ip":/usr/local
done
