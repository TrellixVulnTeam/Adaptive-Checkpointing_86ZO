GROUP="adaptive"
EXCHANGE_RAGE="0.82F"
RATELIST="50000_300000_1000_600000"
HDFS_DIR="hdfs://10.0.0.181:9000/checkpoint"
MEMORY_DIR="file:///home/ubuntu/Adaptive-Checkpointing-Storage/Checkpoint"
CHECKPOINT_DIR=$HDFS_DIR
INCREMENTAL_CHECKPOINTS="false"
LATENCY_MARKER_INTERVAL=60000

CHECKPOINT_INTERVAL=5000
CKP_ADAPTER_RECOVERY=10000
CKP_ADAPTER_ALLOW_RANGE=0.4
CKP_ADAPTER_CHECK_INTERVAL=1000
CKP_ADAPTER_INC=0.25
CKP_ADAPTER_DEC=-0.1
CKP_ADAPTER_TASK_TIMER_INTERVAL=1000
CKP_ADAPTER_EMA=0.8
CKP_ADAPTER_COUNTER=3
CKP_ADAPTER_WINDOW=4
