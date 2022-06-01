package org.apache.flink.runtime.jobmaster;

import org.apache.flink.runtime.checkpoint.CheckpointCoordinator;
import org.apache.flink.runtime.jobgraph.tasks.CheckpointCoordinatorConfiguration;
import org.apache.flink.runtime.jobgraph.tasks.JobCheckpointAdapterConfiguration;
import org.apache.flink.runtime.taskmanager.TaskManagerRunningState;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

public class CheckpointAdapter {
    final class Consumer implements Runnable {
        @Override
        public void run() {

        }
    }

    private JobCheckpointAdapterConfiguration checkpointAdapterConfiguration;
    private long baseInterval;
    private final CheckpointCoordinator coordinator;
    private boolean isAdapterEnable;
    private final BlockingQueue<Long> queue;

    private final long recoveryTime;
    private final double allowRange;
    private final long checkInterval;

    protected final Logger log = LoggerFactory.getLogger(getClass());

    public CheckpointAdapter(
            CheckpointCoordinatorConfiguration chkConfig,
            JobCheckpointAdapterConfiguration checkpointAdapterConfiguration,
            CheckpointCoordinator coordinator) {
        this.checkpointAdapterConfiguration = checkpointAdapterConfiguration;
        this.coordinator = coordinator;
        this.baseInterval = chkConfig.getCheckpointInterval();
        this.isAdapterEnable = true;
        this.queue = new LinkedBlockingQueue<>();

        this.recoveryTime = checkpointAdapterConfiguration.getRecoveryTime();
        this.allowRange = checkpointAdapterConfiguration.getAllowRange();
        this.checkInterval = checkpointAdapterConfiguration.getCheckInterval();

        boolean withPeriod = checkInterval > 0;
        boolean withRange = allowRange > 0;
        log.info("checkInterval:" + checkInterval);
        log.info("allowRange:" + allowRange);
        if (withPeriod || withRange) {
            ThreadPoolExecutor executor =
                    new ThreadPoolExecutor(
                            3, 10, 60, TimeUnit.SECONDS, new ArrayBlockingQueue<>(20));
            Runnable consumer = new Consumer();
            CompletableFuture.runAsync(consumer, executor).thenRunAsync(executor::shutdown);
        }
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
        long checkpointID = taskManagerRunningState.getCheckpointID();
        final String message =
                "ideal: " + ideal + " inputRate: " + inputRate + " checkpointID: " + checkpointID;
        log.info(message);

        // dealt with initial NaN
        if (Double.isNaN(ideal) || Double.isNaN(inputRate)) {
            return true;
        }

        double maxData = (double) (recoveryTime / 1000) * ideal; // ideal: records per second
        long newPeriod = (long) (maxData / inputRate); // (records / million seconds)
        log.info("New Period: " + newPeriod);

        // Get rid of extreme data
        if (newPeriod == 0 || newPeriod == Long.MAX_VALUE) {
            return true;
        }

        try {
            queue.put(newPeriod);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return true;
    }

    private boolean isOverAllowRange(long period) {
        long variation = (period - baseInterval) / baseInterval;
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
