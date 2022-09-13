package org.apache.flink.streaming.api.environment;

import org.apache.flink.annotation.Public;

import static org.apache.flink.util.Preconditions.checkNotNull;

/** Configuration that captures all adapter related settings. */
@Public
public class CheckpointAdapterConfig {
    /** the same as user tolerant time. */
    private long recoveryTime = -1;

    /**
     * A new period calculated from the metrics outside this range triggers a period change
     * operation default value is 30%.
     */
    private double allowRange = 0.3;

    /** How often the checkpoint adapter checks for updates, operation default value is 1000ms. */
    private long checkInterval = 1000;

    /** for metrics submission **/
    private double incThreshold = 0.25;

    private double decThreshold = -0.1;

    private long taskTimerInterval = 1000;

    private double EMA = 0.8;

    private int counterThreshold = 3;

    private int taskWindowSize = 4;

    public void setCounterThreshold(int counterThreshold) {
        this.counterThreshold = counterThreshold;
    }

    public void setTaskWindowSize(int taskWindowSize) {
        this.taskWindowSize = taskWindowSize;
    }

    public int getCounterThreshold() {
        return counterThreshold;
    }

    public int getTaskWindowSize() {
        return taskWindowSize;
    }

    public void setEMA(double EMA) {
        this.EMA = EMA;
    }

    public double getEMA() {
        return EMA;
    }

    public void setAllowRange(double allowRange) {
        this.allowRange = allowRange;
    }

    public void setCheckInterval(long checkInterval) {
        if (checkInterval <= 0) checkInterval = 1; // reset illegal argument
        this.checkInterval = checkInterval;
    }

    public void setIncThreshold(double incThreshold) {
        this.incThreshold = incThreshold;
    }

    public void setDecThreshold(double decThreshold) {
        this.decThreshold = decThreshold;
    }

    public double getAllowRange() {
        return allowRange;
    }

    public long getCheckInterval() {
        return checkInterval;
    }

    public double getIncThreshold() {
        return incThreshold;
    }

    public double getDecThreshold() {
        return decThreshold;
    }

    public void setTaskTimerInterval(long taskTimerInterval) {
        this.taskTimerInterval = taskTimerInterval;
    }

    public long getTaskTimerInterval() {
        return taskTimerInterval;
    }

    public boolean isCheckpointAdapterEnabled() {
        return recoveryTime > 0;
    }

    /**
     * Creates a deep copy of the provided {@link CheckpointAdapterConfig}.
     *
     * @param config the config to copy.
     */
    public CheckpointAdapterConfig(final CheckpointAdapterConfig config) {
        checkNotNull(config);
        this.recoveryTime = config.recoveryTime;
        this.allowRange = config.allowRange;
        this.checkInterval = config.checkInterval;
        this.taskTimerInterval = config.taskTimerInterval;
        this.incThreshold = config.incThreshold;
        this.decThreshold = config.decThreshold;
        this.EMA = config.EMA;
        this.counterThreshold = config.counterThreshold;
        this.taskWindowSize = config.taskWindowSize;
    }

    public CheckpointAdapterConfig() {}

    /**
     * Sets the recovery time in which adapter used for new period calculation.
     *
     * @param recoveryTime The recovery time, in milliseconds.
     */
    public void setRecoveryTime(long recoveryTime) {
        this.recoveryTime = recoveryTime;
    }

    public long getRecoveryTime() {
        return recoveryTime;
    }
}
