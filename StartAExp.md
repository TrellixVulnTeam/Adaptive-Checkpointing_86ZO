# Depoly Custom Flink & Start A Experiment
1. `ssh ubuntu@128.31.26.144`
2. `rm -rf Adaptive-Checkpointing` and `git clone https://github.com/CASP-Systems-BU/Adaptive-Checkpointing.git` or `git stash` `git pull` and `git stash pop`
3. `cd Adaptive-Checkpointing/experiment-tools/`, `./build-all.sh` build flink and all jobs
4. 'cd Adaptive-Checkpointing/experiments-tools/', `./start-exp.sh 1/3/5/8` start exp (find more details in /experiments-tools/README.md)

