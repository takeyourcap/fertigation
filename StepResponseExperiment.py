##################################################
'''首先导入需要用到的python库文件。'''
##################################################
import numpy as np
import random
import time
import math
import copy
import control
from control import tf
import harold
from PID_fertigation import PID
##################################################
''' first-order system '''
##################################################
# 1 Step response experiment
def steady_state(output):
''' function to calculate the steady state value of EC by seting variacne < 0.001 (if not working, set it bigger) '''
    if len(output)<20:
        return False
    EC_sample=output[-20:]
    variance=np.var(EC_sample,dtype=float64)
    if variance<0.001:
        return True
EC_expect = 1.5 
# EC is limited to {0, 20}, mapping the duty cycle of the output PWM # to {0, 100%}
experimentStartTime=time.time()
experimentPeriod=[experimentStartTime]
EC_current=EC_read(EC_pin)
step_inputRecord=[]
step_outputRecord=[]
while steady_state(step_outputRecord) != True:
    try:
        PWM_output(EC_expect)
        time.sleep(1)    # 采样周期为1 s
        EC_current=EC_read(EC_pin)
        experimentPeriod.append(time.time()-experimentStartTime)
        step_outputRecord.append(EC_current)
        step_inputRecord.append(EC_expect)
# 2 System identification - calculating system time dalay L
def system_response(output, var):
    if len(output)<5:
        return False
    variance=np.var(output)
    if variance>var:
        return True
while system_response(outEC, 0.001) != True:
    outEC=step_outputRecord[k:k+5]
    k+=1
L=experimentPeriod[k+4]-experimentPeriod[0]
# 2 System identification - calculating system gain K
K=(step_outputRecord[-1]-step_outputRecord[0])/(2.5-1.5)
# 2 System identification - calculating system time constan T
T63=(step_outputRecord[-1]-step_outputRecord[0])*0.632
Tindex=find_T(step_outputRecord, T63)
def find_T(out,val):  #function to find the real T63 value which is mostly close to T63
    diff=100
    index=0
    for i in range(len(out)):
        diff_current = math.fabs(out[i]-val)
        if diff_current < diff:
            index=i
            diff=diff_current
    return index
T = experimentPeriod[Tindex]-L
# 3 Incremental PID tuning 
k_P=(1.2*T)/(K*L)
t_I=2*L
t_D=0.5*L
k_I=k_P/t_I
k_D=k_P/t_D
 
