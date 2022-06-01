package org.apache.flink.streaming.api.environment;

import org.apache.flink.annotation.Public;

import static org.apache.flink.util.Preconditions.checkNotNull;

/** Configuration that captures all adapter related settings. */
@Public
public class CheckpointAdapterConfig {
    /** the same as user tolerant time. */
    private long recoveryTime = -1;
    /**
     * The interval between data submissions of taskExecutor, The default timing is -1 , which means
     * commit once after completing a checkpoint.
     */
    @Deprecated private long metricsInterval = -1;
    /**
     * A new period calculated from the metrics outside this range triggers a period change
     * operation default value is 30%.
     */
    private double allowRange = 0.3;
    /** How often the checkpoint adapter checks for updates, operation default value is 1000ms. */
    private long checkInterval = 1000;
    /**
     * If this value is true. You must both set allowRange and changePeriod Changes are triggered
     * only if the data stays at a level (allowRange) for a period of time (changePeriod).
     */
    @Deprecated private boolean isDebounceMode = false;

    public void setAllowRange(double allowRange) {
        this.allowRange = allowRange;
    }

    public void setCheckInterval(long checkInterval) {
        this.checkInterval = checkInterval;
    }

    @Deprecated
    public void setDebounceMode(boolean debounceMode) {
        isDebounceMode = debounceMode;
    }

    public double getAllowRange() {
        return allowRange;
    }

    public long getCheckInterval() {
        return checkInterval;
    }

    public boolean isDebounceMode() {
        return isDebounceMode;
    }

    @Deprecated
    public void setMetricsInterval(long metricsInterval) {
        this.metricsInterval = metricsInterval;
    }

    public long getMetricsInterval() {
        return metricsInterval;
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
        this.metricsInterval = config.metricsInterval;
        this.isDebounceMode = config.isDebounceMode;
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
