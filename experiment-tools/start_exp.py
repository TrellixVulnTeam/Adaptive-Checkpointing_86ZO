import os
import sys
from nameconfig import query_name, folder_name

kafkaip="128.31.25.127"
root="http://128.31.26.144:8081"

kwd=sys.argv[1]
argstr=sys.argv[2]

# random topic name to file
timestamp=datetime.datetime.now().timestamp()
time_string=("".join(str(timestamp).split('.')))
topicname="adaptive-checkpoint-{}".format(time_string)
print("topicname: ", topicname)

# verify if the topic is added successfully?
os.popen('sh ./create_kafka_topic.sh'+' '+kafkaip+' '+topicname).read()

# run Query
def submit_query_job(name, programArg):
    os.popen('sh ' + )

# run kafkaSource
def submit_kafkasource_job(kwd):


if __name__ == "__main__":
   submit_query_job(kwd, argstr)
#    await submit_kafkasource_job()


