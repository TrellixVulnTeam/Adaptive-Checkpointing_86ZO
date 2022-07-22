#!/bin/bash
DATA_DIR=$1
PIC_DIR=$2

python3 draw_latency_result.py "$DATA_DIR" "$PIC_DIR"
python3 draw_metrics_result.py "$DATA_DIR" "$PIC_DIR"
python3 draw_thr_result.py "$DATA_DIR" "$PIC_DIR"
