#!/bin/bash
bin=`dirname "$0"`
bin=`cd "$bin"; pwd`
echo "bin: $bin"

. "$bin"/config.sh
. "$bin"/argsconfig.sh

# Query 3 change allow range
CKP_ADAPTER_CHECK_INTERVAL=1000
CKP_ADAPTER_ALLOW_RANGE=0.2
./start-exp.sh 1 ~/data/exp1_query3_ar
CKP_ADAPTER_ALLOW_RANGE=0.4
./start-exp.sh 1 ~/data/exp1_query3_ar
CKP_ADAPTER_ALLOW_RANGE=0.6
./start-exp.sh 1 ~/data/exp1_query3_ar
CKP_ADAPTER_RECOVERY=-1
./start-exp.sh 1 ~/data/exp1_query3_ar

# Query 3 change interval
CKP_ADAPTER_RECOVERY=10000
CKP_ADAPTER_ALLOW_RANGE=0.4
CKP_ADAPTER_CHECK_INTERVAL=0
./start-exp.sh 1 ~/data/exp1_query3_interval
CKP_ADAPTER_CHECK_INTERVAL=500
./start-exp.sh 1 ~/data/exp1_query3_interval
CKP_ADAPTER_CHECK_INTERVAL=2000
./start-exp.sh 1 ~/data/exp1_query3_interval
CKP_ADAPTER_RECOVERY=-1
./start-exp.sh 1 ~/data/exp1_query3_interval

# Query 5


