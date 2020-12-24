#!/usr/bin/python
#
# This is an implementation of incremental PID controller for fertigation system control.
# Copyright (C) 2020 takeyourcap@foxmail.com
#
# title           :PID_fertigation.py
# date            :20200111
# =====================================================================

import time
class PID:
    """incremental PID Controller
    """
    def __init__(self, P=0.2, I=0.0, D=0.0, current_time=None):
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.sample_time = 0.00
        self.current_time = current_time if current_time is not None else time.time()
        self.last_time = self.current_time
        self.clear()
        # self.integrator_flag=True
    def clear(self):
        """Clears PID computations and coefficients"""
        self.SetPoint = 0.0
        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_second_error = 0.0
        self.last_error = 0.0
        # Windup Guard
        # self.int_error = 0.0
        # self.windup_guard = 20.0
        self.windup_max=100
        self.windup_min=0.0
        self.output = 0.0
    def update(self, feedback_value, current_time=None):
        """Calculates PID value for given reference feedback
        .. math::
                ∆u(t_k )=K_p∙[e(k∙T)-e(k∙T-T)]+K_i∙e(k∙T)+K_d∙[e(k∙T)-2e(k∙T-T)+e(k∙T-2T)]
        """
        error = self.SetPoint - feedback_value
        # self.integrator_flag=True
        self.current_time = current_time if current_time is not None else time.time()
        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error
        # if (delta_time >= self.sample_time):
        self.PTerm = self.Kp * delta_error
        # if (self.integrator_flag==True):
        if self.output>self.windup_max:
            if error<=0:
                self.ITerm=error
        elif self.output<self.windup_min:
            if error>=0:
                self.ITerm=error
        else:
            self.ITerm=error
        # print("99999", self.ITerm)
        # return self.output                
        #    self.ITerm += error * delta_time           
        # if (self.ITerm < -self.windup_guard):
        #     self.ITerm = -self.windup_guard
        # elif (self.ITerm > self.windup_guard):
        #     self.ITerm = self.windup_guard
        # self.DTerm = 0.0
        # if delta_time > 0:
        self.DTerm = error - 2*self.last_error + self.last_second_error
            # self.DTerm = delta_error / delta_time
        print("8888888",self.DTerm)
        # Remember last time and last 2 error for next calculation
        self.last_time = self.current_time
        self.last_second_error = self.last_error
        self.last_error = error
        self.output += self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)
        # if self.output>self.windup_max:
        #     self.output=self.windup_max
        # elif self.output<self.windup_min:
        #     self.output=self.windup_min
        return self.output
    def setKp(self, proportional_gain):
        """Determines how aggressively the PID reacts to the current error with setting Proportional Gain"""
        self.Kp = proportional_gain
    def setKi(self, integral_gain):
        """Determines how aggressively the PID reacts to the current error with setting Integral Gain"""
        self.Ki = integral_gain
    def setKd(self, derivative_gain):
        """Determines how aggressively the PID reacts to the current error with setting Derivative Gain"""
        self.Kd = derivative_gain
    def setWindup(self, windup_h=100, windup_l=0.0):
        """Integral windup, also known as integrator windup or reset windup,
        refers to the situation in a PID feedback controller where
        a large change in setpoint occurs (say a positive change)
        and the integral terms accumulates a significant error
        during the rise (windup), thus overshooting and continuing
        to increase as this accumulated error is unwound
        (offset by errors in the other direction).
        The specific problem is the excess overshooting.
        """
        # self.windup_guard = windup
        self.windup_max=windup_h
        self.windup_min=windup_l

    def setSampleTime(self, sample_time):
        """PID that should be updated at a regular interval.
        Based on a pre-determined sampe time, the PID decides if it should compute or return immediately.
        """
        self.sample_time = sample_time

    def setSetPoint(self, setpoint):
        """setting for a desired EC、pH value. Before runing the PID controller, a EC、pH setpoint should be given.
        """
        self.SetPoint = setpoint
