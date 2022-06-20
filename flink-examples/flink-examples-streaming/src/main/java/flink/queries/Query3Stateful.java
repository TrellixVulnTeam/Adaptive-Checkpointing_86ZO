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
import org.apache.flink.api.common.functions.FilterFunction;
import org.apache.flink.api.common.state.MapState;
import org.apache.flink.api.common.state.MapStateDescriptor;
import org.apache.flink.api.common.typeinfo.BasicTypeInfo;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.api.java.tuple.Tuple4;
import org.apache.flink.api.java.typeutils.GenericTypeInfo;
import org.apache.flink.api.java.typeutils.TupleTypeInfo;
import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.KafkaSourceOptions;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.connector.kafka.source.reader.deserializer.KafkaRecordDeserializationSchema;
import org.apache.flink.contrib.streaming.state.EmbeddedRocksDBStateBackend;
import org.apache.flink.streaming.api.CheckpointingMode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.KeyedStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.co.RichCoFlatMapFunction;
import org.apache.flink.util.Collector;

import flink.sinks.DummyLatencyCountingSink;
import flink.utils.AuctionSchema;
import flink.utils.PersonSchema;
import org.apache.beam.sdk.nexmark.model.Auction;
import org.apache.beam.sdk.nexmark.model.Person;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;

public class Query3Stateful {

    private static final Logger logger = LoggerFactory.getLogger(Query3Stateful.class);

    public static void main(String[] args) throws Exception {
        // set up the execution environment
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
                        "checkpoint-dir", "file:///home/Adaptive-Checkpointing-Storage/Checkpoint");
        final String hdfsDir =
                params.get(
                        "checkpoint-dir", "hdfs://10.0.0.181:9000/checkpoint");
        boolean incrementalCheckpoints = params.getBoolean("incremental-checkpoints", false);

        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setStateBackend(new EmbeddedRocksDBStateBackend(incrementalCheckpoints));
        env.getCheckpointConfig().setCheckpointStorage(hdfsDir);
        env.enableCheckpointing(5000, CheckpointingMode.EXACTLY_ONCE);
        env.enableCheckpointAdapter(100000);
        env.disableOperatorChaining();
        // enable latency tracking
        env.getConfig().setLatencyTrackingInterval(60000);

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

        DataStream<Person> filteredPersons =
                persons.filter(
                        new FilterFunction<Person>() {
                            @Override
                            public boolean filter(Person person) throws Exception {
                                return (person.state.equals("OR")
                                        || person.state.equals("ID")
                                        || person.state.equals("CA"));
                            }
                        });
        // .setParallelism(params.getInt("p-person-source", 1))
        // .slotSharingGroup("filt");

        // SELECT Istream(P.name, P.city, P.state, A.id)
        // FROM Auction A [ROWS UNBOUNDED], Person P [ROWS UNBOUNDED]
        // WHERE A.seller = P.id AND (P.state = `OR' OR P.state = `ID' OR P.state = `CA')

        KeyedStream<Auction, Long> keyedAuctions =
                auctions.keyBy(
                        new KeySelector<Auction, Long>() {
                            @Override
                            public Long getKey(Auction auction) throws Exception {
                                return auction.seller;
                            }
                        });

        KeyedStream<Person, Long> keyedPersons =
                filteredPersons.keyBy(
                        new KeySelector<Person, Long>() {
                            @Override
                            public Long getKey(Person person) throws Exception {
                                return person.id;
                            }
                        });

        DataStream<Tuple4<String, String, String, Long>> joined =
                keyedAuctions
                        .connect(keyedPersons)
                        .flatMap(new JoinPersonsWithAuctions())
                        .name("Incremental join");
        // .setParallelism(params.getInt("p-join", 1))
        // .slotSharingGroup("join");

        GenericTypeInfo<Object> objectTypeInfo = new GenericTypeInfo<>(Object.class);
        joined.transform("Sink", objectTypeInfo, new DummyLatencyCountingSink<>(logger))
                .setParallelism(params.getInt("p-join", 1));
        // .slotSharingGroup("sink");

        // execute program
        env.execute("Nexmark Query3 stateful");
    }

    private static final class JoinPersonsWithAuctions
            extends RichCoFlatMapFunction<Auction, Person, Tuple4<String, String, String, Long>> {

        // person state: id, <name, city, state>
        private MapState<Long, Tuple3<String, String, String>> personMap;

        // auction state: seller, List<id>
        private final HashMap<Long, HashSet<Long>> auctionMap = new HashMap<>();

        @Override
        public void open(Configuration parameters) throws Exception {
            MapStateDescriptor<Long, Tuple3<String, String, String>> personDescriptor =
                    new MapStateDescriptor<Long, Tuple3<String, String, String>>(
                            "person-map",
                            BasicTypeInfo.LONG_TYPE_INFO,
                            new TupleTypeInfo<>(
                                    BasicTypeInfo.STRING_TYPE_INFO,
                                    BasicTypeInfo.STRING_TYPE_INFO,
                                    BasicTypeInfo.STRING_TYPE_INFO));

            personMap = getRuntimeContext().getMapState(personDescriptor);
        }

        @Override
        public void flatMap1(Auction auction, Collector<Tuple4<String, String, String, Long>> out)
                throws Exception {
            // check if auction has a match in the person state
            if (personMap.contains(auction.seller)) {
                // emit and don't store
                Tuple3<String, String, String> match = personMap.get(auction.seller);
                out.collect(new Tuple4<>(match.f0, match.f1, match.f2, auction.id));
            } else {
                // we need to store this auction for future matches
                if (auctionMap.containsKey(auction.seller)) {
                    HashSet<Long> ids = auctionMap.get(auction.seller);
                    ids.add(auction.id);
                    auctionMap.put(auction.seller, ids);
                } else {
                    HashSet<Long> ids = new HashSet<>();
                    ids.add(auction.id);
                    auctionMap.put(auction.seller, ids);
                }
            }
        }

        @Override
        public void flatMap2(Person person, Collector<Tuple4<String, String, String, Long>> out)
                throws Exception {
            // store person in state
            personMap.put(person.id, new Tuple3<>(person.name, person.city, person.state));

            // check if person has a match in the auction state
            if (auctionMap.containsKey(person.id)) {
                // output all matches and remove
                HashSet<Long> auctionIds = auctionMap.remove(person.id);
                for (Long auctionId : auctionIds) {
                    out.collect(new Tuple4<>(person.name, person.city, person.state, auctionId));
                }
            }
        }
    }
}
