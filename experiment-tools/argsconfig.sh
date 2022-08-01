# experimental configurable parameters for a job
GROUP="adaptive"
EXCHANGE_RAGE="0.82F"
HDFS_DIR="hdfs://10.0.0.181:9000/checkpoint"
MEMORY_DIR="file:///home/ubuntu/Adaptive-Checkpointing-Storage/Checkpoint"
CHECKPOINT_DIR=$HDFS_DIR
INCREMENTAL_CHECKPOINTS="false"
LATENCY_MARKER_INTERVAL=60000

EXP_TYPE="exp1"

DURATION="1800000"
HALF_DURATION="9000"
Q3_AUC_HIGH="5000"
Q3_PER_HIGH="1000"
Q5_BID_HIGH="4000"
Q8_AUC_HIGH="2800"
Q8_PER_HIGH="800"
Q3_AUC_LOW="100"
Q3_PER_LOW="20"
Q5_BID_LOW="100"
Q8_AUC_LOW="100"
Q8_PER_LOW="30"
AUCTION_RATELIST="$Q3_AUC_HIGH"_"$DURATION"
PERSON_RATELIST="$Q3_PER_HIGH"_"$DURATION"
BID_RATELIST="$Q5_BID_HIGH"_"$DURATION"

CHECKPOINT_INTERVAL=5000
CKP_ADAPTER_RECOVERY=10000
CKP_ADAPTER_ALLOW_RANGE=0.4    #allow range
CKP_ADAPTER_CHECK_INTERVAL=1000   # checkInterval
CKP_ADAPTER_INC=0.25
CKP_ADAPTER_DEC=-0.1
CKP_ADAPTER_TASK_TIMER_INTERVAL=1000
CKP_ADAPTER_EMA=0.8
CKP_ADAPTER_COUNTER=3
CKP_ADAPTER_WINDOW=4

