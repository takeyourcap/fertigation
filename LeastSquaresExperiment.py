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
###########################################################
''' second-order system '''
###########################################################
# 1 Least squares method experiment (PRBS)
EC_set=0.0
experimentStartTime=time.time()
experimentPeriod=[experimentStartTime]
prbs_input=[]
prbs_output=[]
prbs_inputRecord=[]
prbs_outputRecord=[]
P=0.1 # probability for generating PRBS
for i in range(100): # 运行时间为100 s
    PWM_output(EC_set)
    time.sleep(1)    # 采样周期为1 s
    EC_current=EC_read(EC_pin)
    experimentPeriod.append(time.time()-experimentStartTime)
    prbs_output.append(EC_current)
    prbs_input.append(EC_set)
    k = random.random()
    if k < P: 
        if EC_set == 0:
            EC_set=2.5
        else:
            EC_set==0
for i in range(1,len(prbs_outputRecord)):
prbs_outputRecord.append(prbs_output[i]-prbs_output[0])   
prbs_inputRecord.append(prbs_input[i]-prbs_input[0])
# 2 system identification -- calculating ph matirx
###  θ = (Φ^T*Φ)^-1*Φ^T*Y 
ph=[[prbs_outputRecord[0],0,prbs_inputRecord[0],1]]
for k in range(1,len(prbs_outputRecord)):
    newPh=[prbs_outputRecord[k], prbs_outputRecord[k-1],prbs_inputRecord[k], prbs_inputRecord[k-1]]
    ph.append(newPh)
ph_T=np.matrix(ph).T
ph_I=np.matrix(np.dot(ph_T,ph)).I
th = np.dot(np.dot(ph_I,ph_T),np.array(prbs_outputRecord))
th = th.tolist()[0]
# 2 system identification -- calculating the system discrete transfer function in z-domain
num=[float(th[2]),float(th[3])]
den=[float(-th[0]),float(-th[1])]
tf_z=harold.Transfer(num,den,2)
# 2 system identification -- convert z-domain to s-domain
tf_s=harold.undiscretize(tf_z,method='zoh')
# 3 Incremental PID tuning 
k_P=(1.2*T)/(K*L)
t_I=2*L
t_D=0.5*L
k_I=k_P/t_I
k_D=k_P/t_D
