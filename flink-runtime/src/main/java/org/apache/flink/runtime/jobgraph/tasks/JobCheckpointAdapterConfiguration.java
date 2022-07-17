/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.apache.flink.runtime.jobgraph.tasks;

import java.io.Serializable;

/**
 * The JobCheckpointingAdapterSettings are attached to a JobGraph and describe the settings for the
 * asynchronous checkpoints of the JobGraph, such as recovery time.
 */
public class JobCheckpointAdapterConfiguration implements Serializable {
    public static final long DEFAULT_RECOVERY = 10000;
    /** the same as user tolerant time. */
    private final long recoveryTime;
    /**
     * A new period calculated from the metrics outside this range triggers a period change
     * operation default value is 10%
     */
    private double allowRange;
    /**
     * The modification is performed only once in a time range, If this value is not set and only
     * allowRange is set, changes will be triggered as soon as they occur. If only this value is
     * set, period is reset with the smallest value for each cycle, regardless of whether an
     * out-of-range change has occurred
     */
    private long checkInterval;

    /**
     * following are all configurable params
     * */
    private double incThreshold = 0.25;

    private double decThreshold = 0.25;

    private long taskTimerInterval = 1000;

    private double EMA = 0.8;

    private int counterThreshold = 3;

    private int taskWindowSize = 4;

    public long getRecoveryTime() {
        return recoveryTime;
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

    public long getTaskTimerInterval() {
        return taskTimerInterval;
    }

    public double getEMA() {
        return EMA;
    }

    public int getCounterThreshold() {
        return counterThreshold;
    }

    public int getTaskWindowSize() {
        return taskWindowSize;
    }

    public boolean isAdapterEnable() {
        return recoveryTime > 0;
    }

    public void setAllowRange(double allowRange) {
        this.allowRange = allowRange;
    }

    public void setCheckInterval(long checkInterval) {
        this.checkInterval = checkInterval;
    }

    public void setIncThreshold(double incThreshold) {
        this.incThreshold = incThreshold;
    }

    public void setDecThreshold(double decThreshold) {
        this.decThreshold = decThreshold;
    }

    public void setTaskTimerInterval(long taskTimerInterval) {
        this.taskTimerInterval = taskTimerInterval;
    }

    public void setEMA(double EMA) {
        this.EMA = EMA;
    }

    public void setCounterThreshold(int counterThreshold) {
        this.counterThreshold = counterThreshold;
    }

    public void setTaskWindowSize(int taskWindowSize) {
        this.taskWindowSize = taskWindowSize;
    }

    public JobCheckpointAdapterConfiguration(long recoveryTime) {
        this.recoveryTime = recoveryTime;
    }

    public JobCheckpointAdapterConfiguration(
            long recoveryTime,
            double allowRange,
            long checkInterval,
            double incThreshold,
            double decThreshold,
            long taskTimerInterval,
            double EMA,
            int counterThreshold,
            int taskWindowSize) {
        this.recoveryTime = recoveryTime;
        this.allowRange = allowRange;
        this.checkInterval = checkInterval;
        this.incThreshold = incThreshold;
        this.decThreshold = decThreshold;
        this.taskTimerInterval = taskTimerInterval;
        this.EMA = EMA;
        this.counterThreshold = counterThreshold;
        this.taskWindowSize = taskWindowSize;
    }

    public JobCheckpointAdapterConfiguration() {
        this.recoveryTime = DEFAULT_RECOVERY;
    }

    @Override
    public String toString() {
        return String.format(
                "SnapshotAdapterSettings: "
                        + recoveryTime
                        + ","
                        + allowRange
                        + ","
                        + checkInterval
                        + ","
                        + incThreshold
                        + ","
                        + decThreshold
                        + ","
                        + taskTimerInterval
                        + ","
                        + EMA
                        + ","
                        + counterThreshold
                        + ","
                        + taskWindowSize
        );
    }
}
