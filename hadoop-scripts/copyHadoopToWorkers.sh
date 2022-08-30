#!/bin/bash
localip=$(hostname -I)
iplist=()
while IFS= read -r line; do
  ip="$line"
  printf '%s\n' $ip
  if [ ! -z "$ip" ]; then
    iplist+=("$ip")
  fi
done < workers

for ip in "${iplist[@]}"
do
  if [[ $ip != $localip ]]; then
    echo "copy hadoop to $ip"
    scp -r $HADOOP_HOME $ip:/usr/local/
  fi
done
