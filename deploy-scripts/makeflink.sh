cd ..
mvn spotless:apply
mvn clean package -DskipTests 
cd deploy-scripts
