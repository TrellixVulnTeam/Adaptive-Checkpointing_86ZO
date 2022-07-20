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
            "base": [30, 123, 234, ...]  // latency_value
            "new": [...]
        }
        '''

        log_list = os.listdir(self._src_dir+"/log")
        exp_info = {}
        if os.path.exists(self._target_dir + "/latency.json"):
            with open(self._target_dir + "/latency.json", 'r') as r:
                try:
                    exp_info = json.load(r)
                except Exception as e:
                    print("Exception", e)
                    sys.exit(1)
        latency_record = []
        for log in log_list:
            for line in open(self._src_dir+"/log/"+log, "r"):
                if "%latency%" not in line:
                    continue
                first_pos = line.find("%", 0)
                second_pos = line.find("%", first_pos+1)
                third_pos = line.find("%", second_pos+1)
                latency = int(line[second_pos+1:third_pos])
                latency_record.append(latency)

        exp_info[self._exp_type] = latency_record
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
            "task_name": {
                "exp_type": {
                    "bytes_thr":[],
                    "num_thr":[]
                },
                ...
            },
            "checkpoints": {
                "exp_type": {
                    "end_to_end_duration": [],
                    "state_size": [],
                    "average_duration": 30,
                    "average_size": 3000
                },
                ...
            }
        }
        '''
        tasks_data = {}
        with open(self._src_dir+"/metrics_record.json", 'r') as r:
            try:
                metrics_info = json.load(r)
            except Exception as e:
                print("Exception", e)
                sys.exit(1)
            for key in metrics_info:
                if key != 'Checkpoints':
                    task_data = {}
                    exp_data = {}
                    task = metrics_info[key]
                    task_name = task['name']
                    task_bytes_thr = task['0.numBytesInPerSecond']
                    task_num_thr = task['0.numRecordsInPerSecond']
                    if os.path.exists(self._target_dir + "/metrics.json"):
                        with open(self._target_dir + "/metrics.json", 'r') as r1:
                            try:
                                task_data = json.load(r1)[task_name]
                            except Exception as e:
                                print("Exception", e)
                                sys.exit(1)

                    exp_data['bytes_thr'] = task_bytes_thr
                    exp_data['num_thr'] = task_num_thr
                    task_data[self._exp_type] = exp_data
                    tasks_data[task_name] = task_data
                else:
                    # todo: parse checkpoints info here
                    checkpoint_data = {}
                    exp_data = {}
                    checkpoints_info = metrics_info['checkpoints']
                    checkpoints_duration_list = []
                    checkpoints_size_list = []
                    for checkpoint_id in checkpoints_info:
                        if checkpoint_id != 'summary':
                            checkpoints_duration_list.append(checkpoints_info[checkpoint_id]['end_to_end_duration'])
                            checkpoints_size_list.append(checkpoints_info[checkpoint_id]['state_size'])
                        else:
                            average_duration = checkpoints_info[checkpoint_id]['end_to_end_duration']
                            average_size = checkpoints_info[checkpoint_id]['state_size']

                    if os.path.exists(self._target_dir + "/metrics.json"):
                        with open(self._target_dir + "/metrics.json", 'r') as r1:
                            try:
                                checkpoint_data = json.load(r1)['checkpoints']
                            except Exception as e:
                                print("Exception", e)
                                sys.exit(1)
                    exp_data['end_to_end_duration'] = checkpoints_duration_list
                    exp_data['state_size'] = checkpoints_size_list
                    exp_data['average_duration'] = average_duration
                    exp_data['average_size'] average_size
                    checkpoint_data[self._exp_type] = exp_data
                    tasks_data['checkpoints'] = checkpoint_data

        with open(self._target_dir + "/metrics.json", "w") as w:
            json.dump(tasks_data, w, indent=4, separators=(',', ':'))



    def process_data(self):
        parse_log()
        copy_files()
        parse_metrics()


def main(target_path, src_path, exp_type):
    file_parser = FileParser(src_path, target_path, exp_type)
    file_parser.process_data()


if __name__ = "__main__":
    target_path = "~/data"
    query_id = sys.argv[1]
    exp_type = sys.argv[2]
    src_path = "~/Adaptive-Checkpointing/experiment-tools/" + query_id
    main(target_path, src_path, exp_type)






