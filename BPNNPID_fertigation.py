##################################################
'''首先导入需要用到python库文件'''
##################################################
import numpy as np
import time
import math
import copy
import control
from control import tf
import harold
from PID_fertigation import PID
import matplotlib.pyplot as plt
import pylab as pl
# from pylab import *[]
import pandas as pd
from openpyxl import load_workbook

book = load_workbook('/volumes/takeyourcap/graduating/disertation/data/data.xlsx')
writer = pd.ExcelWriter('/volumes/takeyourcap/graduating/disertation/data/data.xlsx', engine='openpyxl') 
writer.book = book
writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

# xite=1.5;alfa=0.4
# xite=0.9;alfa=0.25
# xite=1.00;alfa=0.45
# xite=0.8;alfa=0.35
# xite=1.0;alfa=0.35
# xite=0.9;alfa=0.35
# xite=0.9;alfa=0.30
xite=0.9;alfa=0.4  #学习速率和惯性系数进行赋值

S=1  # Step Signal
# S=2  # Sine Signal

IN=4;H=5;Out=3  # NN Structure
if S==1:         # Step Signal
##################################
首先初始化网络的连接权重 wi和wo
##################################

    # wi=np.array([[-0.6394,-0.2696, -0.3756, -0.7023],
    #    [-0.8603, -0.2013, -0.5024, -0.2596],
    #    [-1.0749, 0.5543, -1.6820, -0.5437],
    #    [-0.3625, -0.0724, -0.6463, -0.2859],
    #    [0.1425, 0.0279, -0.5406, -0.7660]])
#    wi=[-0.0174    0.2499   -0.4179   -0.3139;
#        -0.2282    0.3294   -0.3675    0.1082;
#        0.0217    0.4564    0.0348   -0.3386;
#        0.5613   -0.3930    0.1574    0.5078;
#        0.6429   -0.5376    0.1234    0.6353]
    wi=np.array([[-0.00372942,0.26199387,0.00454584,0.0831662 ],
 [ 0.32319411, 0.3136847, 0.43053337, 0.29574572],
 [ 0.17937996, 0.23113142, 0.14170142, 0.3885484 ],
 [ 0.05508348, 0.33237108, 0.47315091, 0.29816402],
 [ 0.16028424, 0.30256423, 0.30851771, 0.41721664]])
#     wi=np.array([[-0.95818833,0.22196414,-0.90988335,-0.29861736],
#  [ -0.54633383, -0.42837965, 0.30306978, -0.05206546],
#  [ 1.02105962, 0.29643355, 0.91807895, 0.72522026 ],
#  [ 0.54239676, 0.39710861, 0.89572667, 0.49308933],
#  [ 0.73614099,  0.33552372,  0.85141498, 0.64755934]])
    # wi=0.5*np.random.rand(H,IN)
    # print("++++++++",wi)
    wi_1=wi;wi_2=wi;wi_3=wi
    
#    wo=[0.7576 0.2616 0.5820 -0.1416 -0.1325;
#        -0.1146 0.2949 0.8352 0.2205 -0.4508;
#        0.7201 0.4566 0.7672 0.4962 0.3632]
    wo=np.array([[-0.1269,0.1816,0.2980,-0.1666,-0.3634],
       [0.1058,0.3458,0.2020,-0.3936,-0.5664],
       [0.0333,0.0861,-0.1519,-0.6027,-0.4803]])
    # wo=np.array([[-0.09168068, 0.21681932, 0.33321932, -0.13138068, -0.32818068],
    #    [0.14101932, 0.38101932, 0.23721932, -0.35838068, -0.53118068],
    #    [0.06851932, 0.12131932, -0.11668068, -0.56748068, -0.44508068]])    
    # wo=0.5*np.random.rand(Out,H)
    wo_1=wo;wo_2=wo;wo_3=wo

x=[0,0,0]
du_1=0
u_1=0;u_2=0;u_3=0;u_4=0;u_5=0;u_6=0;u_7=0
y_1=0;y_2=0;y_3=0

Oh=np.zeros((H,1))  #Output from NN middle layer
I=Oh          #Input to NN middle layer
error_2=0
error_1=0
EC_setpoint=2.5
BP_experiment_period=[]
rin=[]
yout=[]
error=[]
xi=[]
kp=[]
ki=[]
kd=[]
du=[]
u=[]
dyu=[]
dK=[0, 0, 0]
delta3=[0, 0, 0]
dO=[0, 0, 0, 0, 0]
delta2=[0, 0, 0, 0, 0]
a=[]

ts=1  # sampling time
for k in range(150):
    BP_experiment_period.append(k*ts)
    if S==1:
        rin.append(EC_setpoint)
    # elif S==2:
    #     rin.append(sin(1*2*pi*k*ts))
    
    # ym(k)=0;       #扰动，3 s时刻添加了0.1的扰动
    # if k==3000
    #     ym(k)=0.1
    
    #Sampling the system output, the EC value of the fertigation solution
    # EC_current=EC_read(EC_pin)
    # yout.append(EC_current)

    yout.append(0.8599*y_1+0.02188*u_6+0.01955*u_7) # 括号内为水肥一体化系统一阶辨识传递函数(差分方程形式)
    
    error.append(rin[k]-yout[k])
    
    xi=[[rin[k],yout[k],error[k],1]]
    
    x[0]=error[k]-error_1
    x[1]=error[k]
    x[2]=error[k]-2*error_1+error_2
    
    epid=np.array([[x[0], x[1], x[2]]]).T
    # print("*****",wi.T)
    I=np.dot(xi, wi.T)
    for j in range(H):
        # print("*****",I[0][j])
        Oh[j][0]=(np.exp(np.array([I[0][j]],dtype=np.float128))[0]-np.exp(np.array([-I[0][j]],dtype=np.float128))[0])/(np.exp(np.array([I[0][j]],dtype=np.float128))[0]+np.exp(np.array([-I[0][j]],dtype=np.float128))[0])    #Middle layer output
    K=np.dot(wo,Oh)                                                    #Output layer
    for l in range(Out):
        K[l][0]=np.exp(np.array([K[l][0]],dtype=np.float128))[0]/(np.exp(np.array([K[l][0]],dtype=np.float128))[0]+np.exp(np.array([-K[l][0]],dtype=np.float128))[0])                 #Getting kp,ki,kd
    kp.append(K[l][0])
    ki.append(K[l][0])
    kd.append(K[l][0])
    
    Kpid=[kp[k],ki[k],kd[k]]
    
    du.append(np.dot(Kpid,epid)[0])
    u.append(u_1+du[k])
    
    dyu.append(np.sign((yout[k]-y_1)/(du[k]-du_1+0.0001)))    
    
    #Output layer
    for j in range(Out):
        dK[j]=2/(np.exp(np.array([K[j][0]],dtype=np.float128))[0]+np.exp(np.array([-K[j][0]],dtype=np.float128))[0])**2
    for l in range(Out):
        delta3[l]=error[k]*dyu[k]*epid[l][0]*dK[l]
    for l in range(Out):
        for i in range(H):
            d_wo=xite*delta3[l]*Oh[i][0]+alfa*(wo_1-wo_2)
    wo=wo_1+d_wo+alfa*(wo_1-wo_2)
    
    #Hidden layer
    for i in range(H):
# print("+++++++",I[0][i])      dO[i]=4/(np.exp(np.array([I[0][i]],dtype=np.float128))[0]+np.exp(np.array([-I[0][i]],dtype=np.float128))[0])**2
        # print(dO)
    segma=np.dot(delta3,wo)
    # print("segma", segma)
    for i in range(H):
        delta2[i]=dO[i]*segma[i]
    d_wi=xite*np.dot(np.array([delta2]).T, np.array(xi))
    # print("9999999",d_wi)
    wi = (wi_1+d_wi+alfa*(wi_1-wi_2))
    # print("8888888",wi)
    
    #Parameters Update
    du_1=du[k]
    u_7=u_6;u_6=u_5;u_5=u_4;u_4=u_3;u_3=u_2;u_2=u_1;u_1=u[k]
    y_2=y_1;y_1=yout[k]
    
    wo_3=wo_2;wo_2=wo_1;wo_1=wo
    
    wi_3=wi_2;wi_2=wi_1;wi_1=wi
    
    error_2=error_1;error_1=error[k]

print("wi",wi)
print("wo",wo)

# df=pd.DataFrame(data=yout, columns=['1.5+0.4'])
# df=pd.DataFrame(data=yout, columns=['0.90+0.25'])
# df=pd.DataFrame(data=yout, columns=['1.0+0.45'])
# df=pd.DataFrame(data=yout, columns=['1.80+0.35'])
# df=pd.DataFrame(data=yout, columns=['1.0+0.35'])
# df=pd.DataFrame(data=yout, columns=['0.9+0.35'])
# df=pd.DataFrame(data=yout, columns=['0.9+0.3'])
df=pd.DataFrame(data=yout, columns=['0.9+0.4'])

# df.to_excel(writer, "Sheet1", startcol=0)
# df.to_excel(writer, "Sheet1", startcol=2)
# df.to_excel(writer, "Sheet1", startcol=4)
# df.to_excel(writer, "Sheet1", startcol=6)
# df.to_excel(writer, "Sheet1", startcol=8)
# df.to_excel(writer, "Sheet1", startcol=10)
# df.to_excel(writer, "Sheet1", startcol=12)
# df.to_excel(writer, "Sheet1", startcol=14)
writer.save()

pl.plot(BP_experiment_period,rin,'r', label=u'input')
pl.plot(BP_experiment_period,yout,'b', label=u'ouput')
pl.legend()
pl.show()
# plot(BP_experiment_period,rin,'r', label=u'input')
# plot(BP_experiment_period,yout,'b', label=u'ouput')
# legend()；show()
