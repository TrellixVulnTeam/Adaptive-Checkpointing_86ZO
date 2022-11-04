# Build Problem
1. when you try to build, run 'mvn clean package -DskipTests -X', maven checkstyle is opened, so the build process fail may relate to style problem, find with -x and fix it! run 'mvn spotless:apply'
2. Never run 'mvn clean package'. It will cause some issue with test. 
3. For "Couldn't find/download xxxplugin" error, just rebuild it
4. If 'xxx module couldn't be found' appears when you are running an example. Try to rebuild the whole module / folder 
5. Build the whole Flink to ensure that you use the imported package of Custom Flink. Build example separately will use flink-1.14.0.

# Test Source Code
1. modify and run test files in every package, for small part of code modification, for example: flink-simplified-checkpoint/flink-runtime/**src/test**/java/org/apache/flink/runtime/jobmaster/JobMasterTest.java
2. Use flink-example/, run main() in the application which uses Flink API 

# Connect To Kafka
1. change listeners in server.properties to ensure port 9092 can be access by Flink application
2. use screen to run kafka and zookeeper

# Connect To Hadoop
1. add 2 env variables (HADOOP_CLASSPATH, HADOOP_CONF_DIR) to hadoop-env.sh. Accroding to https://nightlies.apache.org/flink/flink-docs-release-1.11/ops/deployment/hadoop.html#providing-hadoop-classes,
   Flink will use the environment variable HADOOP_CLASSPATH to augment the classpath that is used when starting Flink components . Most Hadoop distributions and cloud environments will not set this 
   variable by default so if the Hadoop classpath should be picked up by Flink the environment variable must be exported on all machines that are running Flink components explicitly.
   Another reason may be environment isolation cased by running the shell scripts.
2. add flink-shaded-hadoop-3-uber.jar to build-target/lib fro resolving dependencies conflicts. refer to
   https://nightlies.apache.org/flink/flink-docs-release-1.11/ops/deployment/hadoop.html#hadoop-integration.
3. change the IP in core-sites.xml to make the datanode connect to the namenode.
4. use http:<ip of the hadoop vm>:9870 to access the hadoop UI to debug and check status.
5. To add more vms as datanodes: add JAVA_HOME, HADOOP_HOME, HADOOP_CONF_DIR and HADOOP_CLASSPATH in "~/.bashrc" of all vms(master and workers).
Don't forget to use "source ~/.bashrc" to refresh the settings. Make new datanode folder and namenode folder in $HADOOP_HOME/hadoop_data/hdfs. Add these folders
as dfs.datanode.data.dir in hdfs-sites.xml. Change the replication factor to 3 (need 3 copies of the data). Add masters file in $HADOOP_CONF_DIR with masternode private IP. Add all the "workers" 
node private IP in "workers" file. When we need a new node use "scp /usr/local/hadoop flinknode-XX:/usr/local/" to install hadoop in that vm. Remove the datanode as well as namenode folders 
and recreate them. Also change some settings in yarn-site.xml and mapred-site.xml. 

1)namenode:
vi ~/.bashrc
add the following at the end of the files

export HADOOP_HOME=/usr/local/hadoop
export PATH=$PATH:$JAVA_HOME/bin
export PATH=$PATH:$HADOOP_HOME/bin
export PATH=$PATH:$HADOOP_HOME/sbin
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64
export HADOOP_CONF_DIR=${HADOOP_HOME}/etc/hadoop
export HADOOP_CLASSPATH=/usr/lib/jvm/java-1.8.0-openjdk-amd64/lib/tools.jar

source ~/.bashrc

vi $HADOOP_CONF_DIR/hadoop-env.sh
check if JAVA_HOME has been added, otherwise add 
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64

vi $HADOOP_CONF_DIR/core-site.xml
change the localhost to the internal ip of the namenode

<configuration>
        <property>
                <name>hadoop.tmp.dir</name>
                <value>/usr/local/hadoop/hdfs/tmp</value>
        </property>
        <property>
                <name>fs.defaultFS</name>
                <value>hdfs://flinknode-1:9000</value>
        </property>
</configuration>

 vi $HADOOP_CONF_DIR/yarn-site.xml
 add
<configuration>
<property>
<!-- Site specific YARN configuration properties -->
   <name>yarn.nodemanager.aux-services</name>
   <value>mapresuce_shuffle</value>
</property>
<property>
   <name>yarn.nodemanager.aux-service.mapresuce.shuffle.class</name>
   <value>org.apache.hadoop.mapred.ShuffleHandler</value>
</property>
<property>
   <name>yarn.resourcemanager.hostname</name>
   <value>flinknode-1</value>
</property>
<property>
   <name>yarn.resourcemanager.webapp.address</name>
   <value>${yarn.nodemanager.hostname}:5349</value>
</property>
<property>
   <name>yarn.nodemanager.webapp.address</name>
   <value>${yarn.nodemanager.hostname}:5249</value>
</property>
</configuration>

 vi $HADOOP_CONF_DIR/mapred-site.xml
 add
<configuration>
   <property>
      <name>mapreduce.jobtracker.address</name>
      <value>flinknode-1:54311</value>
</property>
<property>
      <name>mapreduce.framework.name</name>
      <value>yarn</value>
</property>
</configuration>

 vi $HADOOP_CONF_DIR/hdfs-site.xml
 add
<configuration>
        <property>
                <name>dfs.replication</name>
                <value>3</value>
        </property>
        <property>
                <name>dfs.namenode.name.dir</name>
                <value>file:///usr/local/hadoop/hadoop_data/hdfs/namenode</value>
        </property>
        <property>
                <name>dfs.datanode.data.dir</name>
                <value>file:///usr/local/hadoop/hadoop_data/hdfs/datanode</value>
        </property>
        <property>
                <name>dfs.webhdfs.enabled</name>
                <value>true</value>
        </property>
</configuration>

mkdir -p $HADOOP_HOME/hadoop_data/hdfs/datanode
mkdir -p $HADOOP_HOME/hadoop_data/hdfs/namenode

vi $HADOOP_CONF_DIR/masters
add 
flinknode-1

vi $HADOOP_CONF_DIR/slaves
add
flinknode-1
flinknode-3
flinknode-4

vi /etc/hosts
add all the nodes
127.0.1.1 flinknode-1.novalocal
127.0.0.1 localhost

# The following lines are desirable for IPv6 capable hosts
::1 localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

10.52.0.252 flinknode-1.novalocal flinknode-1                                       
10.52.2.212 flinknode-2.novalocal flinknode-2                                       
10.52.0.2 flinknode-3.novalocal flinknode-3                                         
10.52.2.250 flinknode-4.novalocal flinknode-4  

cd /usr/local/hadoop/sbin/stop-all.sh

hdfs namenode -format
$HADOOP_HOME/sbin/start-dfs.sh
$HADOOP_HOME/sbin/start-yarn.sh

jps

2. add more datanode to the namenode
vi /etc/hosts
add all the nodes

vi ~/.bashrc
add the following at the end of the files

export HADOOP_HOME=/usr/local/hadoop
export PATH=$PATH:$JAVA_HOME/bin
export PATH=$PATH:$HADOOP_HOME/bin
export PATH=$PATH:$HADOOP_HOME/sbin
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64
export HADOOP_CONF_DIR=${HADOOP_HOME}/etc/hadoop
export HADOOP_CLASSPATH=/usr/lib/jvm/java-1.8.0-openjdk-amd64/lib/tools.jar

source ~/.bashrc

back to namnode, copy the hadoop file to the datanode:
rsync -auvx /usr/local/hadoop flinknode-1:$HADOOP_HOME


vi $HADOOP_CONF_DIR/masters
add 
flinknode-1

vi $HADOOP_CONF_DIR/slaves(might be workers)
add
flinknode-1
flinknode-3
flinknode-4

mkdir -p $HADOOP_HOME/hadoop_data/hdfs/datanode
mkdir -p $HADOOP_HOME/hadoop_data/hdfs/namenode

hadoop-daemon.sh start datanode

back to namenode
$HADOOP_HOME/sbin/stop-dfs.sh
$HADOOP_HOME/sbin/start-dfs.sh
hdfs dfsadmin -report

