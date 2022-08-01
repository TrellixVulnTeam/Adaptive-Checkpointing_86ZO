import os
import sys
import json
import shutil

class FileParser:

    def __init__(self, src_dir, target_dir, exp_name):
        self._src_dir = src_dir
        self._target_dir = target_dir
        self._exp_name = exp_name

    def parse_latency(self):
        '''
        latency file format
        {
            "exp_name": [30, 123, 234, ...]  // latency_value
            "exp_name": [...]
            ...
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

        exp_info[self._exp_name] = latency_record
        target_path = self._target_dir+"/latency.json"
        with open(target_path, 'w') as w:
            json.dump(exp_info, w, indent=4, separators=(',', ':'))

    def parse_cpu(self):
        '''
        cpu file format
        {
            "exp_name": [10.2, 3.1, ...]
            "exp_name": [...]
            ...
        }
        '''
        node_list = os.listdir(self._src_dir+"/sys-metrics")
        for node in node_list:
            exp_info = {}
            if not os.path.exists(self._target_dir+"/"+node):
                os.mkdir(self._target_dir+"/"+node)
            if os.path.exists(self._target_dir+"/"+node+"/cpu.json"):
                with open(self._target_dir+"/"+node+"/cpu.json", 'r') as r:
                    try:
                        exp_info = json.load(r)
                    except Exception as e:
                        print("Exception", e)
                        sys.exit(1)
            cpu_record = []
            for line in open(self._src_dir+"/sys-metrics/"+node+"/cpu_record.txt", 'r'):
                value = float(line)
                cpu_record.append(value)
            exp_info[self._exp_name] = cpu_record
            target_path = self._target_dir+"/"+node+"/cpu.json"
            with open(target_path, 'w') as w:
                json.dump(exp_info, w, indent=4, separators=(',', ':'))


    def parse_thr(self):
        '''
        throughput file format
        {
            "task_name": {
                "exp_name": [187, 177, ]
                "exp_name": [...]
                ...
            },
            ...
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
                if key != 'checkpoints':
                    task_data = {}
                    task = metrics_info[key]
                    task_name = task['name']
                    throughput_record = task['0.numBytesInPerSecond']
#                     task_num_thr = task['0.numRecordsInPerSecond']
                    if os.path.exists(self._target_dir + "/throughput.json"):
                        with open(self._target_dir + "/throughput.json", 'r') as r1:
                            try:
                                task_data = json.load(r1)[task_name]
                            except Exception as e:
                                print("Exception", e)
                                sys.exit(1)

                    task_data[self._exp_name] = throughput_record
                    tasks_data[task_name] = task_data

        with open(self._target_dir + "/throughput.json", "w") as w:
            json.dump(tasks_data, w, indent=4, separators=(',', ':'))

    def parse_ckp(self):
        '''
        checkpoint file format:
        {
            "end_to_end_duration": {
                "exp_name":[],
                ...
            },
            "state_size": {
                "exp_name":[],
                ...
            },
            "average_duration": {
                "exp_name": 100,
                ...
            },
            "average_size": {
                "exp_name": 1000,
                ...
            }
        }
        '''

        checkpoint_data = {}
        checkpoints_info = {}
        with open(self._src_dir+"/metrics_record.json", 'r') as r:
            try:
                metrics_info = json.load(r)
            except Exception as e:
                print("Exception", e)
                sys.exit(1)
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

        checkpoints_duration = {}
        checkpoints_size = {}
        checkpoint_avg_dur = {}
        checkpoint_avg_size = {}
        if os.path.exists(self._target_dir + "/checkpoints.json"):
            with open(self._target_dir + "/checkpoints.json", 'r') as r:
                try:
                    checkpoint_data = json.load(r)
                except Exception as e:
                    print("Exception", e)
                    sys.exit(1)
            checkpoints_duration = checkpoint_data['end_to_end_duration']
            checkpoints_size = checkpoint_data['state_size']
            checkpoint_avg_dur = checkpoint_data['average_duration']
            checkpoint_avg_size = checkpoint_data['average_size']

        checkpoints_duration[self._exp_name] = checkpoints_duration_list
        checkpoint_data['end_to_end_duration'] = checkpoints_duration
        checkpoints_size[self._exp_name] = checkpoints_size_list
        checkpoint_data['state_size'] = checkpoints_size
        checkpoint_avg_dur[self._exp_name] = average_duration
        checkpoint_data['average_duration'] = checkpoint_avg_dur
        checkpoint_avg_size[self._exp_name] = average_size
        checkpoint_data['average_size'] = checkpoint_avg_size

        with open(self._target_dir + "/checkpoints.json", "w") as w:
            json.dump(checkpoint_data, w, indent=4, separators=(',', ':'))



    def process_data(self):
        self.parse_latency()
        self.parse_cpu()
        self.parse_thr()
        self.parse_ckp()


def main(target_path, src_path, exp_name):
    file_parser = FileParser(src_path, target_path, exp_name)
    file_parser.process_data()
    shutil.rmtree(src_path)


if __name__ == "__main__":
    query_id = sys.argv[1]
    exp_name = sys.argv[2]
    target_path = sys.argv[3]
    src_path = "./" + query_id
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    main(target_path, src_path, exp_name)
