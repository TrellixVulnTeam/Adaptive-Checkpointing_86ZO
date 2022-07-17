/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package flink.queries;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.java.tuple.Tuple4;
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

import flink.sinks.DummyLatencyCountingSink;
import flink.utils.BidSchema;
import org.apache.beam.sdk.nexmark.model.Bid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Query1 {

    private static final Logger logger = LoggerFactory.getLogger(Query1.class);

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

        env.disableOperatorChaining();

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
                        .setStartingOffsets(OffsetsInitializer.earliest())
                        .build();

        DataStream<Bid> bids =
                env.fromSource(source, WatermarkStrategy.noWatermarks(), "Kafka source");

        DataStream<Tuple4<Long, Long, Long, Long>> mapped =
                bids.map(
                                new MapFunction<Bid, Tuple4<Long, Long, Long, Long>>() {
                                    @Override
                                    public Tuple4<Long, Long, Long, Long> map(Bid bid)
                                            throws Exception {
                                        return new Tuple4<>(
                                                bid.auction,
                                                dollarToEuro(bid.price, exchangeRate),
                                                bid.bidder,
                                                bid.dateTime);
                                    }
                                }) // .setParallelism(params.getInt("p-map", 1))
                        .name("Mapper")
                        .uid("Mapper"); // .slotSharingGroup("map");

        GenericTypeInfo<Object> objectTypeInfo = new GenericTypeInfo<>(Object.class);
        mapped.transform("DummyLatencySink", objectTypeInfo, new DummyLatencyCountingSink<>(logger))
                .setParallelism(params.getInt("p-sink", 1))
                .name("Latency Sink")
                .uid("Latency-Sink"); // .slotSharingGroup("sink");

        // execute program
        env.execute("Nexmark Query1");
    }

    private static long dollarToEuro(long dollarPrice, float rate) {
        return (long) (rate * dollarPrice);
    }
}
