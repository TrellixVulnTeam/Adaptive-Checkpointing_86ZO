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

    def get_cluster(self):
        '''
        Show cluster information.

        `/cluster`

        https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/ops/rest_api/#cluster

        '''        
        url = "{}/taskmanagers/10.0.0.235:33307-153094/logs".format(self._endpoint)
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
        response.raise_for_status()
        return response.json()



def main(job_id, target_path, interval, repeat):
    from pprint import pprint
    metrics_info = {}
    flink = Flink(endpoint="http://128.31.26.144:8081/")
#     print("Endpoint is:", flink.get_endpoint())
#     job_id = sys.argv[1]
#     print("Job ID:", job_id)
#     print("Job details:")
    job_details = flink.get_job_details(job_id)
#     pprint(job_details)
#     print("Job metrics:")
#     pprint(flink.get_job_metrics(job_id))
#     print("Job plan:")
    job_plan = flink.get_job_plan(job_id)
    nodes_info = job_plan['plan']['nodes']

    # pprint(job_plan)
#     num_bytes_in_per_second_record = []
#     num_records_in_per_second_record = []
    number_bytes_in_per_second_query = ""
    all_queries_keys = ["0.numBytesInPerSecond", "0.numRecordsInPerSecond"]

    for node in nodes_info:
        node_key = node['id']
        node_value = {}
        node_value['name'] = node['description']
        for query_key in all_queries_keys:
            node_value[query_key] = []
        metrics_info[node_key]  = node_value

    for i in range(0, 1):
        time.sleep(interval)
        for task in job_details['vertices']:
            task_id = task['id']
            task_info = metrics_info[task_id]
#             for query_key in all_queries_keys:
#                  query_result = flink.get_task_metrics_details(job_id, task_id, query_key)
#                  instant_value = query_result[0]["value"]
#                  task_info[query_key].append(instant_value)
#
#     write_to_file(target_path, metrics_info)
    pprint(flink.get_all_checkpoints(job_id))

def write_to_file(target_path, metrics_info):
    if os.path.exists(target_path):
        os.remove(target_path)

    with open(target_path, 'w') as w:
        json.dump(metrics_info, w, indent=4, separators=(',', ':'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--job_id', type=str)
    parser.add_argument('--target_path', type=str, default="./metrics_record.json")
    parser.add_argument('--interval', type=int, default=5)
    parser.add_argument('--repeat', type=int, default=5)
    args = parser.parse_args()

    main(args.job_id, args.target_path, args.interval, args.repeat)
