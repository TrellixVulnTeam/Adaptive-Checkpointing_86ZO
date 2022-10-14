import requests
import logging
import os
import argparse
import json
import sys

class Flink:
    '''
    Flink REST API connector.

    '''

    def __init__(self, endpoint="http://129.114.109.229:8081"):
        self._endpoint = endpoint

    def get_endpoint(self):
        return self._endpoint

    def set_endpoint(self, endpoint):
        self._endpoint = endpoint

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

def trancate_ip(taskmanager_id):
    return taskmanager_id.split(":")[0]


def main(job_id):
    # first get task id by job plan (description = Latency Sink)
    flink = Flink(endpoint="http://129.114.109.229:8081/")
    job_plan = flink.get_job_plan(job_id)
    job_all_nodes = job_plan['plan']['nodes']
    for node in job_all_nodes:
        if node['description'] == 'Latency Sink':
            sink_task_id = node['id']
            break

    # second get task status using task id
    sink_task_status = flink.get_task_status(job_id, sink_task_id)
    sink_subtasks = sink_task_status['subtasks']

    # third get taskmanager-id
    ip_list = []
    for subtask in sink_subtasks:
        taskmanager_id = subtask['taskmanager-id']
        # truncate taskmanager-id to get the ip-address
        ip = trancate_ip(taskmanager_id)
        if ip not in ip_list:
            ip_list.append(ip)
    # return ip-address to shell for scp log files
    return ip_list


if __name__ == "__main__":
    job_id = sys.argv[1]
    return_list = main(job_id)
    return_str = ''
    for item in return_list:
        return_str += str(item)+' '
    print(return_str)

