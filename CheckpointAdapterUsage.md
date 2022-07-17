# Usage of Checkpoint Adapter
## API Usage
APIs are added to `StreamExecutionEnvironment` to set up an adaptive checkpoint.
```java
// if you enable a checkpoint adapter without recovery time,
// default recovery time is 10000L
enableCheckpointAdapter()
enableCheckpointAdapter(long recoveryTime)
// before setting params, you must enable a checkpoint adapter
// configurable params for checkpoint interval update in jobmaster
setCheckpointAdapterAllowRange(double allowRange)
setCheckpointAdapterCheckInterval(long changeInterval)
// configurable params for metrics submission in Task
setCheckpointAdapterIncThreshold(double incThreshold)
setCheckpointAdapterDecThreshold(double decThreshold)
setCheckpointAdapterTaskTimerInterval(long taskTimerInterval)
setCheckpointAdapterEMA(double ema)
setCheckpointAdapterCounterThreshold(int counterThreshold)
setCheckpointAdapterTaskWindowSize(int taskWindowSize)
```
## Docs Description
1. Main Flink application for experiment:
   - "flink-examples/flink-examples-streaming/src/main/java/org/apache/flink/streaming/examples/clusterdata/kafkajob/MaxTaskCompletionTimeFromKafka.java"
2. Flink application for injecting data to Kafka: 
   - "flink-examples/flink-examples-streaming/src/main/java/org/apache/flink/streaming/examples/clusterdata/kafkajob/FilterTaskEventsToKafka.java"
3. Important files related to Checkpoint Adapter Implementation.
   - "flink-runtime/src/main/java/org/apache/flink/runtime/jobmaster/CheckpointAdapter.java"
   - "flink-runtime/src/main/java/org/apache/flink/runtime/jobmaster/JobMaster.java"
   - "flink-runtime/src/main/java/org/apache/flink/runtime/jobmaster/JobMasterGateway.java"
   - "flink-runtime/src/main/java/org/apache/flink/runtime/taskmanager/TaskExecutor.java"
   - "flink-runtime/src/main/java/org/apache/flink/runtime/jobmaster/TaskExecutorGateway.java"
   - "flink-runtime/src/main/java/org/apache/flink/runtime/taskmanager/Task.java"
