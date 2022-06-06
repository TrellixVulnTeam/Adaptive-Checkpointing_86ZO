package flink.kafkaSources;

import flink.sources.BidSourceFunction;
import flink.utils.BidSchema;
import org.apache.beam.sdk.nexmark.model.Bid;

import org.apache.flink.api.java.utils.ParameterTool;
import org.apache.flink.connector.base.DeliveryGuarantee;
import org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;

public class Query1Source {
    private static final String LOCAL_KAFKA_BROKER = "localhost:9092";
    private static final String REMOTE_KAFKA_BROKER = "20.127.226.8:9092";
    public static final String FILTERED_TASKS_TOPIC = "wiki-edits";

    public static void main(String[] args) throws Exception {
        // Checking input parameters
        final ParameterTool params = ParameterTool.fromArgs(args);
        final float exchangeRate = params.getFloat("exchange-rate", 0.82F);
        String ratelist = params.getRequired("ratelist");

        //  --ratelist 250_300000_11000_300000
        int[] numbers = Arrays.stream(ratelist.split("_")).mapToInt(Integer::parseInt).toArray();
        System.out.println(Arrays.toString(numbers));
        List<List<Integer>> rates = new ArrayList<>();
        /* The internal list will be [rate, time in ms]
        //        rates.add(Arrays.asList(25000, 3000000));
                int runningperiod=1*60*60*1000;    //1h
                rates.add(Arrays.asList(150000, runningperiod));
                rates.add(Arrays.asList(1000, runningperiod));
                rates.add(Arrays.asList(1000, runningperiod));
                rates.add(Arrays.asList(1000, runningperiod));
                rates.add(Arrays.asList(1000, runningperiod));
                rates.add(Arrays.asList(1000, runningperiod));
                rates.add(Arrays.asList(1000, runningperiod));
                rates.add(Arrays.asList(1000, runningperiod));
                rates.add(Arrays.asList(1000, runningperiod));
                */
        for (int i = 0; i < numbers.length - 1; i += 2) {
            rates.add(Arrays.asList(numbers[i], numbers[i + 1]));
        }

        // set up streaming execution environment
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        DataStream<Bid> bids =
                env.addSource(new BidSourceFunction(rates))
                        .setParallelism(params.getInt("p-source", 1))
                        .name("Bids Source")
                        .uid("Bids-Source");

        // write the filtered data to a Kafka sink
        KafkaSink<Bid> sink =
                KafkaSink.<Bid>builder()
                        .setBootstrapServers(REMOTE_KAFKA_BROKER)
                        .setDeliverGuarantee(DeliveryGuarantee.EXACTLY_ONCE)
                        .setRecordSerializer(
                                KafkaRecordSerializationSchema.builder()
                                        .setTopic(FILTERED_TASKS_TOPIC)
                                        .setValueSerializationSchema(new BidSchema())
                                        .build())
                        .build();

        bids.sinkTo(sink);
        // run the cleansing pipeline
        env.execute("Task Events to Kafka");
    }

}
