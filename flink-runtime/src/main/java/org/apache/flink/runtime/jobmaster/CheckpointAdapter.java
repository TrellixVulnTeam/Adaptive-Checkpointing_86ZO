package org.apache.flink.runtime.jobmaster;

import org.apache.flink.runtime.checkpoint.CheckpointCoordinator;
import org.apache.flink.runtime.executiongraph.ExecutionAttemptID;
import org.apache.flink.runtime.jobgraph.tasks.CheckpointCoordinatorConfiguration;
import org.apache.flink.runtime.jobgraph.tasks.JobCheckpointAdapterConfiguration;
import org.apache.flink.runtime.taskmanager.TaskManagerRunningState;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.ConcurrentHashMap;

public class CheckpointAdapter {
    private JobCheckpointAdapterConfiguration checkpointAdapterConfiguration;
    private long baseInterval;
    private final CheckpointCoordinator coordinator;
    private boolean isAdapterEnable;
    private Timer timer = new Timer();
    private final ConcurrentHashMap<ExecutionAttemptID, Long> history;
    private final long recoveryTime;
    private final double allowRange;
    private final long checkInterval;
    protected final Logger log = LoggerFactory.getLogger(getClass());

    private class InnerTimerTask extends TimerTask {
        private final long interval;

        public InnerTimerTask(long internal) {
            this.interval = internal;
        }

        @Override
        public void run() {
            log.info(interval + "ms passed, calculate once");
            if (history.size() <= 0) {
                return;
            }
            // find bottleneck of all task. Map keeps the latest metrics
            List<Long> periods = new ArrayList<>(history.values());
            history.clear(); // clear the window after use the data in this window
            Collections.sort(periods, (x, y) -> (int) (x - y));
            // Find the smallest value in all current tasks(bottleneck) and compare it with the
            // threshold to decide whether to update
            long minPeriod = periods.get(0);
            log.info("current smallest value is " + minPeriod);
            if (isOverAllowRange(minPeriod)) {
                log.info( "over range, will change to " + minPeriod + " current time is :" + System.currentTimeMillis());
                updatePeriod(minPeriod);
            }
        }
    }

    public CheckpointAdapter(
            CheckpointCoordinatorConfiguration chkConfig,
            JobCheckpointAdapterConfiguration checkpointAdapterConfiguration,
            CheckpointCoordinator coordinator) {
        this.checkpointAdapterConfiguration = checkpointAdapterConfiguration;
        log.info(checkpointAdapterConfiguration.toString());
        this.coordinator = coordinator;
        this.baseInterval = chkConfig.getCheckpointInterval();
        this.isAdapterEnable = true;
        this.history = new ConcurrentHashMap<>();

        this.recoveryTime = checkpointAdapterConfiguration.getRecoveryTime();
        this.allowRange = checkpointAdapterConfiguration.getAllowRange();
        this.checkInterval = checkpointAdapterConfiguration.getCheckInterval();

        TimerTask task = new InnerTimerTask(checkInterval);
        timer.scheduleAtFixedRate(task, checkInterval, checkInterval);
    }

    public void setAdapterEnable(boolean adapterEnable) {
        isAdapterEnable = adapterEnable;
    }

    public void setCheckpointAdapterConfiguration(
            JobCheckpointAdapterConfiguration checkpointAdapterConfiguration) {
        this.checkpointAdapterConfiguration = checkpointAdapterConfiguration;
    }

    public boolean dealWithMessageFromOneTaskExecutor(
            TaskManagerRunningState taskManagerRunningState) {
        double ideal = taskManagerRunningState.getIdealProcessingRate();
        double inputRate = taskManagerRunningState.getNumRecordsInRate();

        // dealt with initial NaN
        if (Double.isNaN(ideal) || Double.isNaN(inputRate)) {
            return true;
        }

        double maxData = (double) (recoveryTime / 1000) * ideal; // ideal: records per second
        long newPeriod = (long) (maxData / inputRate); // result in milliseconds, input rate (records / million seconds)
        // log.info("New Period: " + newPeriod);

        // Get rid of extreme data
        if (newPeriod == 0 || newPeriod == Long.MAX_VALUE) {
            return true;
        }

        ExecutionAttemptID id = taskManagerRunningState.getExecutionId();
        history.put(id, newPeriod);
        return true;
    }

    private boolean isOverAllowRange(long period) {
        double variation = (double) Math.abs((period - baseInterval)) / (double) baseInterval;
        return variation > allowRange;
    }

    private void updatePeriod(long newPeriod) {
        // if  new Period exceed LONG.MAX_VALUE
        if (newPeriod >= Long.MAX_VALUE
                || newPeriod < coordinator.getMinPauseBetweenCheckpoints()) {
            return;
        }
        // update when a checkpoint is completed
        coordinator.restartCheckpointScheduler(newPeriod);
        baseInterval = newPeriod;
        final String message = "Current Checkpoint Interval was changed to: " + baseInterval;
        log.info(message);
    }

    public JobCheckpointAdapterConfiguration getCheckpointAdapterConfiguration() {
        return checkpointAdapterConfiguration;
    }

    public CheckpointCoordinator getCoordinator() {
        return coordinator;
    }
}
