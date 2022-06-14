import requests
import os
import sys
import datetime

kafkaip="128.31.25.127"
root="128.31.26.144:8081"

# random topic name to file
timestamp=datetime.datetime.now().timestamp()
time_string=("".join(str(timestamp).split('.')))
topicname="adaptive-checkpoint-{}".format(time_string)
print("topicname: ", topicname)

# verify if the topic is added successfully?
os.popen('sh ./create_kafka_topic.sh'+' '+kafkaip+' '+topicname).read()

# run Query
async def submit_query_job(name, programArg):
    # upload jar
    upload_url = "{}/jars/upload".format(root)
    headers = {'Content-Type': "application/x-java-archive"}

    resp_upload =  await requests.post(upload_url, headers=headers, files={'file': open('report.xls', 'rb')})
    jarid = resp_upload.json().id
    # submit job
    submit_url = "{}/jars/{}/run".format(root, jarid)
    # programArg
    resp_submit = await requests.post(submit_url, )
    return resp_submit.json()

# run kafkaSource
async def submit_kafkasource_job(name):
    response = requests.get(url)
    return response.json()


# if __name__ == "__main__":
#    await submit_query_job()
#    await aubmit_kafkasource_job()


