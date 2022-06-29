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

    def __init__(self, endpoint="http://128.31.26.144:8081"):
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

def main(job_id):
    # first get task id by job plan (description = Latency Sink)

    # second get task status using task id

    # third get taskmanager-id

    # truncate taskmanager-id to get the ip-address

    # return ip-address to shell for scp log files


if __name__ = "__main__":
    job_id = sys.argv[1]
    main(job_id)

