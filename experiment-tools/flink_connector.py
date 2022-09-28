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

    def __init__(self, endpoint="http://129.114.109.240:8081"):
        self._endpoint = endpoint

    def get_endpoint(self):
        return self._endpoint
    
    def set_endpoint(self, endpoint):
        self._endpoint = endpoint

    def get_cluster(self):
        '''
        Show cluster information.

        `/cluster`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#cluster

        '''        
        url = "{}/taskmanagers/128.31.26.144:41985-a1561f/logs".format(self._endpoint)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def list_jobs(self):
        '''
        List all jobs.

        `/jobs`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs

        '''
        url = "{}/jobs".format(self._endpoint)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_job_agg_metrics(self):
        '''
        Get job aggregated metrics.

        `/jobs/metrics`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#job-metrics

        '''
        url = "{}/jobs/metrics".format(self._endpoint)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_job_details(self, jobid):
        '''
        Get job details by ID

        `/jobs/{jobid}`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#job-details

        '''
        url = "{}/jobs/{}".format(self._endpoint, jobid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_job_metrics(self, jobid):
        '''
        Get job metrics by ID

        `/jobs/{jobid}/metrics`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-metrics

        '''
        url = "{}/jobs/{}/metrics".format(self._endpoint, jobid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_job_plan(self, jobid):
        '''
        Get job plan by ID

        `/jobs/{jobid}/plan`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-plan

        '''
        url = "{}/jobs/{}/plan".format(self._endpoint, jobid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_task_status(self, jobid, taskid):
        '''
        Get task status by ID

        `/jobs/:jobid/vertices/:vertexid`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-tasks-taskid

        '''
        url = "{}/jobs/{}/vertices/{}".format(self._endpoint, jobid, taskid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_task_backpressure(self, jobid, taskid):
        '''
        Get task backpressure by ID

        `/jobs/:jobid/vertices/:vertexid/backpressure`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-tasks-taskid-backpressure

        '''
        url = "{}/jobs/{}/vertices/{}/backpressure".format(self._endpoint, jobid, taskid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_task_metrics(self, jobid, taskid):
        '''
        Get task metrics by ID

        `/jobs/:jobid/vertices/:vertexid/metrics`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-tasks-taskid-metrics

        '''
        url = "{}/jobs/{}/vertices/{}/metrics".format(self._endpoint, jobid, taskid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_task_metrics_details(self, jobid, taskid, fieldid):
        '''
        Get task metrics by ID

        `/jobs/:jobid/vertices/:vertexid/metrics`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-tasks-taskid-metrics

        '''
        url = "{}/jobs/{}/vertices/{}/metrics?get={}".format(self._endpoint, jobid, taskid, fieldid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_subtask_metrics(self, jobid, taskid):
        '''
        Get subtask metrics by ID

        `/jobs/:jobid/vertices/:vertexid/subtasks/metrics`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-tasks-taskid-metrics-subtaskid

        '''
        url = "{}/jobs/{}/vertices/{}/subtasks/metrics".format(
            self._endpoint, jobid, taskid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_subtask_metrics_details(self, jobid, taskid, fieldid):
        '''
        Get subtask metrics by ID

        `/jobs/:jobid/vertices/:vertexid/subtasks/metrics`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#jobs-jobid-tasks-taskid-metrics-subtaskid

        '''
        url = "{}/jobs/{}/vertices/{}/subtasks/metrics?get={}".format(
            self._endpoint, jobid, taskid, fieldid)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

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
    repeat = int(total_time/interval)
    metrics_info = {}
    checkpoints_info = {}
    flink = Flink(endpoint="http://129.114.109.240:8081/")
    last_record_checkpoint_id = 1
    job_details = flink.get_job_details(job_id)
    job_plan = flink.get_job_plan(job_id)
    nodes_info = job_plan['plan']['nodes']

    number_bytes_in_per_second_query = ""
    all_queries_keys = ["0.numBytesInPerSecond", "0.numRecordsInPerSecond"]
    checkpoint_fetch_keys = ["end_to_end_duration", "state_size"]
    backpressure_key = "backpressure"

    for node in nodes_info:
        node_key = node['id']
        node_value = {}
        node_value['name'] = node['description']
        for query_key in all_queries_keys:
            node_value[query_key] = []
        node_value[backpressure_key] = []
        metrics_info[node_key]  = node_value

    fail_count = 0
    for i in range(0, repeat):
        print("fetch flink data: " + str(i))
        jobs_details = flink.list_jobs()
        jobs_lists_status = jobs_details['jobs']
        for job_status in jobs_lists_status:
            if job_status['id'] == job_id:
                status = job_status['status']
                break

        for task in job_details['vertices']:
            task_id = task['id']
            task_info = metrics_info[task_id]
            task_backpressure = flink.get_task_backpressure(job_id, task_id)
            backpressure_value = get_backpressure_value(task_backpressure)
            task_info[backpressure_key].append(backpressure_value)
            for query_key in all_queries_keys:
                 query_result = flink.get_task_metrics_details(job_id, task_id, query_key)
                 instant_value = query_result[0]["value"]
                 task_info[query_key].append(instant_value)

        current_all_checkpoints = flink.get_all_checkpoints(job_id)
        latest_checkpoint_id = current_all_checkpoints['latest']['completed']['id']
        for i in range(last_record_checkpoint_id, latest_checkpoint_id):
            checkpoint_id = str(i)
            checkpoint_all_details = flink.get_checkpoint_detail(job_id, checkpoint_id)
            checkpoint_store_info = {}
            if "errors" in checkpoint_all_details:
                continue
            for fetch_key in checkpoint_fetch_keys:
                checkpoint_store_info[fetch_key] = checkpoint_all_details[fetch_key]
            checkpoints_info[i] = checkpoint_store_info
        last_record_checkpoint_id = latest_checkpoint_id
        time.sleep(interval)

    current_all_checkpoints = flink.get_all_checkpoints(job_id)
    checkpoints_summary_info = {}
    for fetch_key in checkpoint_fetch_keys:
        checkpoints_summary_info[fetch_key] = current_all_checkpoints['summary'][fetch_key]['avg']
    checkpoints_info['summary'] = checkpoints_summary_info
    metrics_info['checkpoints'] = checkpoints_info

    target_dir = "./" + job_id
    write_to_file(target_dir, metrics_info)

def get_backpressure_value(task_backpressure):
    subtasks_backpressure = task_backpressure['subtasks']
    total_value = 0
    count = 0
    for subtask in subtasks_backpressure:
        total_value += subtask['ratio']
        count += 1
    return total_value/count

def write_to_file(target_dir, metrics_info):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    target_path = target_dir + "/metrics_record.json"
    if os.path.exists(target_path):
        os.remove(target_path)

    with open(target_path, 'w') as w:
        json.dump(metrics_info, w, indent=4, separators=(',', ':'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--job_id', type=str)
    parser.add_argument('--interval', type=int, default=3)
    parser.add_argument('--total_time', type=int, default=30)
    args = parser.parse_args()

    main(args.job_id, args.interval, args.total_time)
