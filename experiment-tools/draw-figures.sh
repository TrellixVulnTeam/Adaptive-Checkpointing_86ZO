#!/bin/bash
DATA_DIR=$1
PIC_DIR=$2

if [ ! -d "$PIC_DIR" ]; then
  echo "===== making pic dir ====="
  mkdir "$PIC_DIR"
fi

python3 draw_latency_result.py "$DATA_DIR" "$PIC_DIR"
python3 draw_ckp_result.py "$DATA_DIR" "$PIC_DIR"
python3 draw_thr_result.py "$DATA_DIR" "$PIC_DIR"
python3 draw_cpu_result.py "$DATA_DIR" "$PIC_DIR"
