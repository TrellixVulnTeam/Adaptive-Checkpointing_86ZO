package flink.utils;

import org.apache.beam.sdk.nexmark.NexmarkUtils;
import org.apache.beam.sdk.nexmark.model.Bid;

import org.apache.flink.api.common.serialization.DeserializationSchema;
import org.apache.flink.api.common.serialization.SerializationSchema;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.TypeExtractor;

public class BidSchema implements DeserializationSchema<Bid>, SerializationSchema<Bid> {

    @Override
    public Bid deserialize(byte[] message) {
        Bid bid  = null;
        try {
            bid = NexmarkUtils.MAPPER.readValue(message, Bid.class);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return bid;
    }

    @Override
    public boolean isEndOfStream(Bid nextElement) {
        return false;
    }

    @Override
    public byte[] serialize(Bid element) {
        return element.toString().getBytes();
    }

    @Override
    public TypeInformation<Bid> getProducedType() {
        return TypeExtractor.getForClass(Bid.class);
    }
}
