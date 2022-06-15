import requests
import os
import sys
import pathlib
from nameconfig import query_name, folder_name

kafkaip="128.31.25.127"
root="http://128.31.26.144:8081"

kwd=sys.argv[1]

# # random topic name to file
# timestamp=datetime.datetime.now().timestamp()
# time_string=("".join(str(timestamp).split('.')))
# topicname="adaptive-checkpoint-{}".format(time_string)
# print("topicname: ", topicname)

# # verify if the topic is added successfully?
# os.popen('sh ./create_kafka_topic.sh'+' '+kafkaip+' '+topicname).read()

# run Query
def submit_query_job(name, programArg):
    # upload jar
    upload_url = "{}/jars/upload".format(root)
    headers = {'Content-Type': "application/x-java-archive"}
    
    if name not in query_name: 
        print("invalid query name!")
        return
    
    jar = './target/'+query_name[name]+'.jar'
    if name == '1' or name == '5':
        source = pathlib.Path('./target/'+query_name['b']+'.jar')
        print(source)
        if (not source.exists()):
            print("BidSource doesn't exist!")
            return
        if (not os.path.exists(jar)):
            print("Query doesn't exist!")
            return
        resp_upload =  requests.post(upload_url, headers=headers, files={'file': open(source, 'rb')})
        resp_upload.raise_for_status()
        print(resp_upload.json())
        jarid = resp_upload.json().id
    else:
        source1 = './target/'+query_name['p']+'.jar'
        source2 = './target/'+query_name['a']+'.jar'
        if (not os.path.exists(source1)):
            print("PersonSource doesn't exist!")
            return
        if (not os.path.exists(source2)):
            print("AuctionSource doesn't exist!")
            return
        if (not os.path.exists(jar)):
            print("Query doesn't exist!")
            return
        resp_upload =  requests.post(upload_url, headers=headers, files={'file': open(jar, 'rb')})
        print(resp_upload.json())
        jarid = resp_upload.json().id
        
#     # submit job
#     submit_url = "{}/jars/{}/run".format(root, jarid)
#     # programArg
#     resp_submit = await requests.post(submit_url, )
#     return resp_submit.json()

# run kafkaSource
async def submit_kafkasource_job(kwd):
    response = requests.get(url)
    return response.json()


if __name__ == "__main__":
   submit_query_job(kwd, "")
#    await submit_kafkasource_job()


