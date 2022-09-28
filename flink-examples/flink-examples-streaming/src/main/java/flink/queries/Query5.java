package flink.queries;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.typeutils.GenericTypeInfo;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.KafkaSourceOptions;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.connector.kafka.source.reader.deserializer.KafkaRecordDeserializationSchema;
import org.apache.flink.contrib.streaming.state.EmbeddedRocksDBStateBackend;
import org.apache.flink.streaming.api.CheckpointingMode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.AssignerWithPeriodicWatermarks;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;

import flink.sinks.DummyLatencyCountingSink;
import flink.utils.BidSchema;
import org.apache.beam.sdk.nexmark.model.Bid;
import org.apache.kafka.clients.consumer.OffsetResetStrategy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.annotation.Nullable;

public class Query5 {

    private static final Logger logger = LoggerFactory.getLogger(Query5.class);

    public static void main(String[] args) throws Exception {
        System.out.println("Options for both the above setups: ");
        System.out.println("\t[--kafka-topic <topic>]");
        System.out.println("\t[--kafka-group <group>]");
        System.out.println("\t[--broker <broker>]");
        System.out.println("\t[--exchange-rate <exchange-rate>]");
        System.out.println("\t[--checkpoint-dir <filepath>]");
        System.out.println("\t[--incremental-checkpoints <true|false>]");

        System.out.println("\t[--ckp-interval <long ckp interval>]");
        System.out.println("\t[--ckp-adapter <long recovery time>]");
        System.out.println("\t[--ckp-adapter-allow-range <double allow range>]");
        System.out.println("\t[--ckp-adapter-check-interval <long check interval>]");
        System.out.println("\t[--ckp-adapter-inc-threshold <double inc threshold>]");
        System.out.println("\t[--ckp-adapter-dec-threshold <double dec threshold>]");
        System.out.println("\t[--ckp-adapter-task-timer-interval <long timer interval>]");
        System.out.println("\t[--ckp-adapter-ema <double ema>]");
        System.out.println("\t[--ckp-adapter-counter-threshold <int counter>]");
        System.out.println("\t[--ckp-adapter-window <int window>]");
        System.out.println("\t[--latency-marker <long interval>]");
        System.out.println();

        // Checking input parameters
        //  --kafka-topic <topic>
        //  --broker <broker>
        // --broker localhost:9092 --kafka-topic query1 --kafka-group test1
        final ParameterTool params = ParameterTool.fromArgs(args);
        final float exchangeRate = params.getFloat("exchange-rate", 0.82F);
        final String broker = params.getRequired("broker");
        final String kafkaTopic = params.getRequired("kafka-topic");
        final String kafkaGroup = params.getRequired("kafka-group");
        System.out.printf(
                "Reading from kafka topic %s @ %s group: %s\n", kafkaTopic, broker, kafkaGroup);
        System.out.println();
        final String checkpointDir =
                params.get(
                        "checkpoint-dir", "hdfs://10.0.0.181:9000/checkpoint");
        boolean incrementalCheckpoints = params.getBoolean("incremental-checkpoints", false);
        long ckpInterval = params.getLong("ckp-interval", -1);
        long ckpAdapterRecoveryTime = params.getLong("ckp-adapter", -1);
        double ckpAdapterAllowRange = params.getDouble("ckp-adapter-allow-range", 0.3);
        long ckpAdapterCheckInterval = params.getLong("ckp-adapter-check-interval", 1000);
        double ckpAdapterIncThreshold = params.getDouble("ckp-adapter-inc-threshold", 0.3);
        double ckpAdapterDecThreshold = params.getDouble("ckp-adapter-dec-threshold", -0.1);
        long ckpAdapterTaskTimerInterval = params.getLong("ckp-adapter-task-timer-interval", 1000);
        double ckpAdapterEMA = params.getDouble("ckp-adapter-ema", -0.1);
        int ckpAdapterCounter = params.getInt("ckp-adapter-counter-threshold", 3);
        int ckpAdapterWindow = params.getInt("ckp-adapter-window", 4);
        long latencyInterval = params.getLong("latency-marker", 60000);


        // set up the execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setStateBackend(new EmbeddedRocksDBStateBackend(incrementalCheckpoints));
        env.getCheckpointConfig().setCheckpointStorage(checkpointDir);

        if (ckpInterval > 0) {
            env.enableCheckpointing(ckpInterval, CheckpointingMode.EXACTLY_ONCE);
        }

        if (ckpInterval > 0 && ckpAdapterRecoveryTime > 0) {
            env.enableCheckpointAdapter(ckpAdapterRecoveryTime);
            env.setCheckpointAdapterAllowRange(ckpAdapterAllowRange);
            env.setCheckpointAdapterCheckInterval(ckpAdapterCheckInterval);
            env.setCheckpointAdapterIncThreshold(ckpAdapterIncThreshold);
            env.setCheckpointAdapterDecThreshold(ckpAdapterDecThreshold);
            env.setCheckpointAdapterTaskTimerInterval(ckpAdapterTaskTimerInterval);
            env.setCheckpointAdapterEMA(ckpAdapterEMA);
            env.setCheckpointAdapterCounterThreshold(ckpAdapterCounter);
            env.setCheckpointAdapterTaskWindowSize(ckpAdapterWindow);
        }

        env.getCheckpointConfig().setCheckpointTimeout(100000);
        env.disableOperatorChaining();
        env.getConfig().setAutoWatermarkInterval(5000);

        // enable latency tracking
        env.getConfig().setLatencyTrackingInterval(latencyInterval);

        KafkaSource<Bid> source =
                KafkaSource.<Bid>builder()
                        .setBootstrapServers(broker)
                        .setGroupId(kafkaGroup)
                        .setTopics(kafkaTopic)
                        .setDeserializer(
                                KafkaRecordDeserializationSchema.valueOnly(new BidSchema()))
                        .setProperty(
                                KafkaSourceOptions.REGISTER_KAFKA_CONSUMER_METRICS.key(), "true")
                        // If each partition has a committed offset, the offset will be consumed
                        // from the committed offset.
                        // Start consuming from scratch when there is no submitted offset
                        .setStartingOffsets(OffsetsInitializer.committedOffsets(OffsetResetStrategy.EARLIEST))
                        .build();

        DataStream<Bid> bids =
                env.fromSource(source, WatermarkStrategy.noWatermarks(), "Kafka source")
                    .slotSharingGroup("src");

        DataStream<Bid> bidsWithWaterMark =
                bids.assignTimestampsAndWatermarks(
                        new TimestampAssigner())
                    .slotSharingGroup("timestamp");

        // SELECT B1.auction, count(*) AS num
        // FROM Bid [RANGE 60 MINUTE SLIDE 1 MINUTE] B1
        // GROUP BY B1.auction
        DataStream<Tuple2<Long, Long>> windowed =
                bidsWithWaterMark
                        .keyBy((KeySelector<Bid, Long>) bid -> bid.auction)
                        .window(SlidingEventTimeWindows.of(Time.seconds(5), Time.seconds(1)))
                        .aggregate(new CountBids())
                        .slotSharingGroup("window")
                        .name("Sliding Window");

        GenericTypeInfo<Object> objectTypeInfo = new GenericTypeInfo<>(Object.class);
        windowed.transform(
                        "DummyLatencySink", objectTypeInfo, new DummyLatencyCountingSink<>(logger))
                .slotSharingGroup("sink")
                .name("Latency Sink")
                .uid("Latency-Sink");

        // execute program
        env.execute("Nexmark Query5");
    }

    private static final class TimestampAssigner implements AssignerWithPeriodicWatermarks<Bid> {
        private long maxTimestamp = Long.MIN_VALUE;

        @Nullable
        @Override
        public Watermark getCurrentWatermark() {
            return new Watermark(maxTimestamp);
        }

        @Override
        public long extractTimestamp(Bid element, long previousElementTimestamp) {
            maxTimestamp = Math.max(maxTimestamp, element.dateTime);
            return element.dateTime;
        }
    }

    private static final class CountBids
            implements AggregateFunction<Bid, Long, Tuple2<Long, Long>> {

        private long auction = 0L;

        @Override
        public Long createAccumulator() {
            return 0L;
        }

        @Override
        public Long add(Bid value, Long accumulator) {
            auction = value.auction;
            return accumulator + 1;
        }

        @Override
        public Tuple2<Long, Long> getResult(Long accumulator) {
            return new Tuple2<>(auction, accumulator);
        }

        @Override
        public Long merge(Long a, Long b) {
            return a + b;
        }
    }
}
