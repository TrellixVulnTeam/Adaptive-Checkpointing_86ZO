#!/bin/bash
iplist=()
while IFS= read -r line; do
  ip="$line"
  if [[ (! -z "$ip") && ($ip != "flinknode-1") ]]; then
    printf '%s\n' $ip
    iplist+=("$ip")
  fi
done < workers

for ip in "${iplist[@]}"
do
  echo "copy hadoop to $ip"
  scp -r "$HADOOP_HOME" "$ip":/usr/local/
done
