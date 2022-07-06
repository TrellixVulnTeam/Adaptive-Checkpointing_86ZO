# Usage of Checkpoint Adapter
## API Usage
6 APIs are added to `StreamExecutionEnvironment` to set up an adaptive checkpoint.
```java
// if you enable a checkpoint adapter without recovery time,
// default recovery time is 10000L
enableCheckpointAdapter()
enableCheckpointAdapter(long recoveryTime)
// before setting params, you must enable a checkpoint adapter
setCheckpointAdapterAllowRange(double allowRange)
setCheckpointAdapterCheckInterval(long changeInterval)
```
Each checkpoint adapter mainly includes 2 parts, so make sure
you set up **_these 2 parts and periodic checkpoint_** properly, 
otherwise the adapter will not work properly: 
1. get metrics from each task
2. calculate and update checkpoint interval referring to metrics
### Set up periodic checkpoint and set up adapter
```java
env.enableCheckpointing(3000L);
env.enableCheckpointAdapter(10000L); 
/** set up recoveryTime without set up metrics submission and update strategy,
 the metrics will be submitted after completing each checkpoint and checkpoint
 interval will not be updated
*/
```
### Set up reset checkpoint strategy

## Docs Description
1. Main Flink application for experiment:
   - "flink-examples/flink-examples-streaming/src/main/java/org/apache/flink/streaming/examples/clusterdata/kafkajob/MaxTaskCompletionTimeFromKafka.java"
2. Flink application for injecting data to Kafka: 
   - "flink-examples/flink-examples-streaming/src/main/java/org/apache/flink/streaming/examples/clusterdata/kafkajob/FilterTaskEventsToKafka.java"
3. Important files related to Checkpoint Adapter Implementation.
![impl](http://blog.minghuiyang1998.com/20220505141506.png)
   - "flink-runtime/src/main/java/org/apache/flink/runtime/jobmaster/CheckpointAdapter.java"
   - "flink-runtime/src/main/java/org/apache/flink/runtime/jobmaster/JobMaster.java"
   - "flink-runtime/src/main/java/org/apache/flink/runtime/jobmaster/JobMasterGateway.java"
   - "flink-runtime/src/main/java/org/apache/flink/runtime/taskmanager/TaskExecutor.java"
   - "flink-runtime/src/main/java/org/apache/flink/runtime/jobmaster/TaskExecutorGateway.java"
   - "flink-runtime/src/main/java/org/apache/flink/runtime/taskmanager/Task.java"
4. Exp-1: master branch, Exp-2: exp-2 branch: exp-2 includes the speed adjustment part in org.apache.flink.streaming.examples.clusterdata.sources.TaskEventSource
