import os
import sys

query_name={
    '1':'Query1',
    '3':'Query3Stateful',
    '5':'Query5',
    '8':'Query8',
    'a':'KafkaSourceAuction',
    'b':'KafkaSourceBid',
    'p':'KafkaSourcePerson'
}

folder_name={
    'q':'queries',
    's':'kafkaSource'
}

#specify which query to run
kwd=sys.argv[2]
folder=sys.argv[1]

print('Compiling '+folder_name[folder]+ ' '+query_name[kwd])

#FOLDER is the folder of mainEntry in .pom
_cmd_folder="sed 's/FOLDER/"+folder_name[folder]+"/g' ./pom_template.xml >> pom.xml"
os.popen(_cmd_folder).read()
#QUERYNO is the mainEntry in .pom
_cmd_name="sed -i '' 's/QUERYNO/"+query_name[kwd]+"/g' ./pom.xml"
os.popen(_cmd_name).read()

# build jar
os.popen('cp pom.xml ../flink-examples/flink-examples-streaming/').read()
os.popen('rm ./pom.xml').read()
print(os.popen('cd .. && mvn spotless:apply && mvn clean package -DskipTests').read())

# move and rename to current folder
dir='target'
if not os.path.exists(dir):
    os.makedirs(dir)
os.popen('cp ../flink-examples/flink-examples-streaming/target/flink-examples-streaming_2.11-1.14.0-jar-with-dependencies.jar ./'+dir+'/'+query_name[kwd]+'.jar').read()
