package flink.queries;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.FlatJoinFunction;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.api.java.tuple.Tuple3;
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
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.util.Collector;

import flink.sinks.DummyLatencyCountingSink;
import flink.utils.AuctionSchema;
import flink.utils.PersonSchema;
import org.apache.beam.sdk.nexmark.model.Auction;
import org.apache.beam.sdk.nexmark.model.Person;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.annotation.Nullable;

public class Query8 {

    private static final Logger logger = LoggerFactory.getLogger(Query8.class);

    public static void main(String[] args) throws Exception {
        // Checking input parameters
        System.out.println("Options for both the above setups: ");
        System.out.println("\t[--auction-kafka-topic <topic>]");
        System.out.println("\t[--auction-kafka-group <group>]");
        System.out.println("\t[--auction-broker <broker>]");
        System.out.println("\t[--person-kafka-topic <topic>]");
        System.out.println("\t[--person-kafka-group <group>]");
        System.out.println("\t[--person-broker <broker>]");
        System.out.println("\t[--exchange-rate <exchange-rate>]");
        System.out.println("\t[--checkpoint-dir <filepath>]");
        System.out.println("\t[--incremental-checkpoints <true|false>]");
        System.out.println();

        // Checking input parameters
        // --auction-broker <broker> --auction-kafka-topic <topic> --auction-kafka-group <group>
        // --auction-broker localhost:9092 --auction-kafka-topic query3 --auction-kafka-group test1
        // --person-broker <broker> --person-kafka-topic <topic> --person-kafka-group <group>
        // --person-broker localhost:9092 --person-kafka-topic query3 --person-kafka-group test1
        final ParameterTool params = ParameterTool.fromArgs(args);
        final float exchangeRate = params.getFloat("exchange-rate", 0.82F);
        final String auctionBroker = params.getRequired("auction-broker");
        final String auctionKafkaTopic = params.getRequired("auction-kafka-topic");
        final String auctionKafkaGroup = params.getRequired("auction-kafka-group");
        final String personBroker = params.getRequired("person-broker");
        final String personKafkaTopic = params.getRequired("person-kafka-topic");
        final String personKafkaGroup = params.getRequired("person-kafka-group");
        System.out.printf(
                "Reading Auction data from kafka topic %s @ %s group: %s\n",
                auctionKafkaTopic, auctionBroker, auctionKafkaGroup);
        System.out.printf(
                "Reading Person data from kafka topic %s @ %s group: %s\n",
                personKafkaTopic, personBroker, personKafkaGroup);
        System.out.println();
        final String checkpointDir =
                params.get(
                        "checkpoint-dir", "hdfs://10.0.0.181:9000/checkpoint");
        boolean incrementalCheckpoints = params.getBoolean("incremental-checkpoints", false);

        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setStateBackend(new EmbeddedRocksDBStateBackend(incrementalCheckpoints));
        env.getCheckpointConfig().setCheckpointStorage(checkpointDir);
        env.enableCheckpointing(100000, CheckpointingMode.EXACTLY_ONCE);
        env.getCheckpointConfig().setCheckpointTimeout(100000);
        env.disableOperatorChaining();
        env.getConfig().setAutoWatermarkInterval(5000);

        // enable latency tracking
        env.getConfig().setLatencyTrackingInterval(100000);

        KafkaSource<Person> personKafkaSource =
                KafkaSource.<Person>builder()
                        .setBootstrapServers(personBroker)
                        .setGroupId(personKafkaGroup)
                        .setTopics(personKafkaTopic)
                        .setDeserializer(
                                KafkaRecordDeserializationSchema.valueOnly(new PersonSchema()))
                        .setProperty(
                                KafkaSourceOptions.REGISTER_KAFKA_CONSUMER_METRICS.key(), "true")
                        // If each partition has a committed offset, the offset will be consumed
                        // from the committed offset.
                        // Start consuming from scratch when there is no submitted offset
                        .setStartingOffsets(OffsetsInitializer.earliest())
                        .build();
        DataStream<Person> persons =
                env.fromSource(
                        personKafkaSource, WatermarkStrategy.noWatermarks(), "Person Kafka source");
        DataStream<Person> personsWithWaterMark =
                persons.assignTimestampsAndWatermarks(
                        new PersonTimestampAssigner()); // .slotSharingGroup("src");

        KafkaSource<Auction> auctionKafkaSource =
                KafkaSource.<Auction>builder()
                        .setBootstrapServers(auctionBroker)
                        .setGroupId(auctionKafkaGroup)
                        .setTopics(auctionKafkaTopic)
                        .setDeserializer(
                                KafkaRecordDeserializationSchema.valueOnly(new AuctionSchema()))
                        .setProperty(
                                KafkaSourceOptions.REGISTER_KAFKA_CONSUMER_METRICS.key(), "true")
                        // If each partition has a committed offset, the offset will be consumed
                        // from the committed offset.
                        // Start consuming from scratch when there is no submitted offset
                        .setStartingOffsets(OffsetsInitializer.earliest())
                        .build();
        DataStream<Auction> auctions =
                env.fromSource(
                        auctionKafkaSource,
                        WatermarkStrategy.noWatermarks(),
                        "Auction Kafka source");
        DataStream<Auction> auctionsWithWaterMark =
                auctions.assignTimestampsAndWatermarks(
                        new AuctionTimestampAssigner()); // .slotSharingGroup("src");

        // SELECT Rstream(P.id, P.name, A.reserve)
        // FROM Person [RANGE 1 HOUR] P, Auction [RANGE 1 HOUR] A
        // WHERE P.id = A.seller;
        DataStream<Tuple3<Long, String, Long>> joined =
                personsWithWaterMark
                        .join(auctionsWithWaterMark)
                        .where(
                                new KeySelector<Person, Long>() {
                                    @Override
                                    public Long getKey(Person p) {
                                        return p.id;
                                    }
                                })
                        .equalTo(
                                new KeySelector<Auction, Long>() {
                                    @Override
                                    public Long getKey(Auction a) {
                                        return a.seller;
                                    }
                                })
                        .window(TumblingEventTimeWindows.of(Time.seconds(10)))
                        .apply(
                                new FlatJoinFunction<
                                        Person, Auction, Tuple3<Long, String, Long>>() {
                                    @Override
                                    public void join(
                                            Person p,
                                            Auction a,
                                            Collector<Tuple3<Long, String, Long>> out) {
                                        out.collect(new Tuple3<>(p.id, p.name, a.reserve));
                                    }
                                });

        GenericTypeInfo<Object> objectTypeInfo = new GenericTypeInfo<>(Object.class);
        joined.transform("DummyLatencySink", objectTypeInfo, new DummyLatencyCountingSink<>(logger))
                .setParallelism(params.getInt("p-window", 1))
                .name("Latency Sink")
                .uid("Latency-Sink");; // .slotSharingGroup("sink");

        // execute program
        env.execute("Nexmark Query8");
    }

    private static final class PersonTimestampAssigner
            implements AssignerWithPeriodicWatermarks<Person> {
        private long maxTimestamp = Long.MIN_VALUE;

        @Nullable
        @Override
        public Watermark getCurrentWatermark() {
            return new Watermark(maxTimestamp);
        }

        @Override
        public long extractTimestamp(Person element, long previousElementTimestamp) {
            maxTimestamp = Math.max(maxTimestamp, element.dateTime);
            return element.dateTime;
        }
    }

    private static final class AuctionTimestampAssigner
            implements AssignerWithPeriodicWatermarks<Auction> {
        private long maxTimestamp = Long.MIN_VALUE;

        @Nullable
        @Override
        public Watermark getCurrentWatermark() {
            return new Watermark(maxTimestamp);
        }

        @Override
        public long extractTimestamp(Auction element, long previousElementTimestamp) {
            maxTimestamp = Math.max(maxTimestamp, element.dateTime);
            return element.dateTime;
        }
    }
}
