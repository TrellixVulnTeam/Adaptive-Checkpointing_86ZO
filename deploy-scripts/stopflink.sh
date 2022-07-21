#!/bin/bash
FLINKROOT=$(cd ..; pwd)
echo "FLINKROOT: $FLINKROOT"

cd $FLINKROOT/flink-dist/target/flink-1.14.0-bin/flink-1.14.0/bin
./stop-cluster.sh

rm "$FLINKROOT"/build-target/log/*

cd $FLINKROOT/deploy-scripts/
