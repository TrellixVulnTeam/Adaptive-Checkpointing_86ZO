import os
import sys
import json
import shutil

class FileParser:

    def __init__(self, src_dir, target_dir, exp_type):
        self._src_dir = src_dir
        self._target_dir = target_dir
        self._exp_type = exp_type

    def parse_log(self):
        '''
        file format
        {
            "base":{
                "30": 2  // latency value: count
                ...
            },
            "new":{
                ...
            }
        }
        '''

        # todo: append data if already exists
        log_list = os.listdir(self._src_dir+"/log")
        exp_info = {}
        latency_info = {}
        for log in log_list:
            for line in open(self._src_dir+"/log/"+log, "r"):
                if "%latency%" not in line:
                    continue
                first_pos = line.find("%", 0)
                second_pos = line.find("%", first_pos+1)
                third_pos = line.find("%", second_pos+1)
                latency = line[second_pos+1:third_pos]
                if latency in latency_info:
                    latency_info[latency] += 1
                else:
                    latency_info[latency] = 0
        exp_info[self._exp_type] = latency_info
        with open(self._target_dir + "/latency.json", "w") as w:
            json.dump(exp_info, w, indent=4, separators=(',', ':'))

    def copy_files(self):
        node_list = os.listdir(self._src_dir+"/sys_metrics")
        for node in node_list:
            os.mkdir(self._target_dir+node)
            shutil.copyfile(self._src_dir+"/sys_metrics/"+node+"/cpu_record.txt", self._target_dir+"/"+node+"/"+self._exp_type)
            shutil.copyfile(self._src_dir+"/sys_metrics/"+node+"/disk_record.txt", self._target_dir+"/"+node+"/"+self._exp_type)
            shutil.copyfile(self._src_dir+"/sys_metrics/"+node+"/thread_num_record.txt", self._target_dir+"/"+node+"/"+self._exp_type)

    def parse_metrics(self):
        '''
        file format
        {
            task_name: {
                exp_type: {
                    "bytes_thr":[],
                    "num_thr":[]
                },
                ...
            },
            ...
        }
        '''
        tasks_data = {}
        checkpoints_data = {}
        with open(self._src_dir+"/metrics_record.json", 'r') as r:
            try:
                metrics_info = json.load(r)
            except Exception as e:
                print("Exception", e)
                sys.exit(1)
            for key in metrics_info:
                # todo: append data if already exists
                if key != 'Checkpoints':
                    task_data = {}
                    exp_data = {}
                    task = metrics_info[key]
                    task_name = task['name']
                    task_bytes_thr = task['0.numBytesInPerSecond']
                    task_num_thr = task['0.numRecordsInPerSecond']
                    exp_data['bytes_thr'] = task_bytes_thr
                    exp_data['num_thr'] = task_num_thr
                    task_data[this._exp_type] = exp_data
                    tasks_data[task_name] = task_data
                else:
                    # todo: parse checkpoints info here





