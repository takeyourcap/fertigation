# Kalman filter example demo in Python
import numpy as np
import matplotlib.pyplot as plt
import xlrd
plt.rcParams['figure.figsize'] = (10, 8)
loc=("G:\\VS_python\\python\\FertigationSystem\\ec_data_kalman_filter.xlsx")
wb=xlrd.open_workbook(loc)
sheet=wb.sheet_by_index(0)
nor=sheet.nrows
EC_raw=[]  # EC测量值（未去噪）
EC_f=[]    # 增强均值滤波值
for i in range(nor-1):
    EC_raw.append(sheet.cell_value(i+1,1))
    EC_f.append(sheet.cell_value(i+1,3))
# intial parameters
n_iter = nor-1
sz = (n_iter,) # size of array
# print("****",sz,"****",type(sz))
x = -0.37727 # truth value (typo in example at top of p. 13 calls this z)
z = np.random.normal(x,0.1,size=sz) # observations (normal about x, sigma=0.1)
# print("******",z)
# print(type(z))
Q = 1e-5 # process variance 过程噪声协方差（不同初始值会影响滤波效果）
# allocate space for arrays
xhat=np.zeros(sz)      # a posteri estimate of x  卡尔曼滤波值
P=np.zeros(sz)         # a posteri error estimate
xhatminus=np.zeros(sz) # a priori estimate of x
Pminus=np.zeros(sz)    # a priori error estimate
K=np.zeros(sz)         # gain or blending factor
R = 1e-4 # estimate of measurement variance测量噪声协方差（不同初始值会影响滤波效
# 果）
# intial guesses
xhat[0] = 0.55 #本文中为水肥溶液的初始EC值（即进水的初始EC值，未吸肥）
P[0] = 1.0
for k in range(1,n_iter):
    # time update
    xhatminus[k] = xhat[k-1]
    Pminus[k] = P[k-1]+Q
    # measurement update
    K[k] = Pminus[k]/( Pminus[k]+R )
    xhat[k] = xhatminus[k]+K[k]*(EC_raw[k]-xhatminus[k])
    P[k] = (1-K[k])*Pminus[k]
plt.figure()
plt.plot(EC_raw,'k-',label='EC raw measurements')  
plt.plot(EC_f,'r-',label='repeated mean filter')
print(xhat)
plt.plot(xhat,'b-',label='Kalman filter’)
plt.legend()
plt.title('Estimate vs. iteration step', fontweight='bold')
plt.xlabel('Iteration')
plt.ylabel('Voltage')
plt.show()
 
