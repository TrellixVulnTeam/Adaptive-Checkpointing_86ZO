


import requests
import logging
import os
import argparse
import json
import sys
import time

class FlinkException(Exception):
    pass


class Flink:
    '''
    Flink REST API connector.
    '''
    def __init__(self, endpoint="http://128.31.26.144:8081"):
        self._endpoint = endpoint

    def get_endpoint(self):
        return self._endpoint

    def set_endpoint(self, endpoint):
        self._endpoint = endpoint

    def get_all_checkpoints(self, jobid):
        url = "{}/jobs/{}/checkpoints".format(
            self._endpoint, jobid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_checkpoint_detail(self, jobid, checkpointid):
        url = "{}/jobs/{}/checkpoints/details/{}".format(
            self._endpoint, jobid, checkpointid)
        response = requests.get(url)
        try:
            response.raise_for_status()
        except Exception as e:
            print(repr(e))
        return response.json()


def main(job_id, interval, total_time):
    flink = Flink(endpoint="http://128.31.26.144:8081/")
    checkpoints_info = {}
    repeat = int(total_time/interval)
    last_record_checkpoint_id = 1
    checkpoint_fetch_keys = ["end_to_end_duration", "state_size"]
    for i in range(0, repeat):
        time.sleep(interval)
        current_all_checkpoints = flink.get_all_checkpoints(job_id)
        latest_checkpoint_id = current_all_checkpoints['latest']['completed']['id']

        for i in range(last_record_checkpoint_id, latest_checkpoint_id):
            checkpoint_id = str(i)
            checkpoint_all_details = flink.get_checkpoint_detail(job_id, checkpoint_id)
            checkpoint_store_info = {}
            if "error" in checkpoint_all_details:
                continue
            for fetch_key in checkpoint_fetch_keys:
                checkpoint_store_info[fetch_key] = checkpoint_all_details[fetch_key]
            checkpoints_info[i] = checkpoint_store_info
        last_record_checkpoint_id = latest_checkpoint_id

    current_all_checkpoints = flink.get_all_checkpoints(job_id)
    checkpoints_summary_info = {}
    for fetch_key in checkpoint_fetch_keys:
        checkpoints_summary_info[fetch_key] = current_all_checkpoints['summary'][fetch_key]['avg']
    checkpoints_info['summary'] = checkpoints_summary_info

    target_dir = "./" + job_id
    write_to_file(target_dir, checkpoints_info)


def write_to_file(target_dir, checkpoints_info):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    target_path = target_dir + "/checkpoints_info.json"
    if os.path.exists(target_path):
        os.remove(target_path)

    with open(target_path, 'w') as w:
        json.dump(checkpoints_info, w, indent=4, separators=(',', ':'))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--job_id', type=str)
    parser.add_argument('--interval', type=int, default=5)
    parser.add_argument('--total_time', type=int, default=60)
    args = parser.parse_args()

    main(args.job_id, args.interval, args.total_time)
