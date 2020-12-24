# 首先导入必要的库，需要提前下载安装(如通过pip install终端命令进行安装)
import os  
import subprocess
import re
import smbus
import time
from time import sleep
bus = smbus.SMBus(1)
# i2c bus (0 -- original Pi, 1 -- Rev 2 Pi)
I2CBUS = 1

#devices I2C address
Ferti_addr = -1  #初始化地址为-1
Irria1_addr = -1
Irria2_addr = -1
Irria3_addr = -1
Irria4_addr = -1
Irria5_addr = -1
Irria6_addr = -1
Screen_addr = -1
Addr_list = [Ferti_addr,Irria1_addr,Irria2_addr,Irria3_addr,Irria4_addr,Irria5_addr,Irria6_addr,Screen_addr]
print(Addr_list)
#switch for every single fertigation line
Fertig1 = 0xfe  ### Pump          or  fertigation line
Fertig2 = 0xfd  ### Acid          or  fertigation line
Fertig3 = 0xfb  ### F fertilizer  or  fertigation line
Fertig4 = 0xf7  ### E fertilizer  or  fertigation line
Fertig5 = 0xef  ### D fertilizer  or  fertigation line
Fertig6 = 0xdf  ### C fertilizer  or  fertigation line
Fertig7 = 0xbf  ### B fertilizer  or  fertigation line
Fertig8 = 0x7f  ### A fertilizer  or  fertigation line
Fertig_all_off = 0xff   ### all off

# test Address
Test_ADDRESS = 0x21

bus.write_byte(Test_ADDRESS,Fertig_all_off)
time.sleep(1)

p = subprocess.Popen(['i2cdetect', '-y','1'],stdout=subprocess.PIPE,) 
#cmdout = str(p.communicate())
print(p.stdout)
for i in range(0,9):
  line = str(p.stdout.readline())
  #print(line)
  for match in re.finditer("2[0-9]:.*[0-9][0-9]", line):
    print (match.group())
    words = match.group().split(" ") # ["10:", "10", "11"]
    print(words)
    for i in range(len(words)):
        if words[i] == '20:':
            continue
        if words[i] != '--' :
            Addr_list[i-1] = words[i]
    print(Addr_list)
    print(Irria1_addr)
class i2c_device:  # I2C寻址及读写库函数
   def __init__(self, addr, port=I2CBUS):
      self.addr = addr
      self.bus = smbus.SMBus(port)
# Write a single command
   def write_cmd(self, cmd):
      self.bus.write_byte(self.addr, cmd)
      sleep(0.0001)
# Write a command and argument
   def write_cmd_arg(self, cmd, data):
      self.bus.write_byte_data(self.addr, cmd, data)
      sleep(0.0001)
# Write a block of data
   def write_block_data(self, cmd, data):
      self.bus.write_block_data(self.addr, cmd, data)
      sleep(0.0001)
# Read a single byte
   def read(self):
      return self.bus.read_byte(self.addr)
# Read
   def read_data(self, cmd):
      return self.bus.read_byte_data(self.addr, cmd)
# Read a block of data
   def read_block_data(self, cmd):
      return self.bus.read_block_data(self.addr, cmd)

class Fertigation_Switch:
    def __init__(self, addr, Fertig_LED1 = 0xff, Fertig_LED2 = 0xff, Fertig_LED3 = 0xff, Fertig_LED4 = 0xff, Fertig_LED5 = 0xff, Fertig_LED6 = 0xff, Fertig_LED7 = 0xff, Fertig_LED8 = 0xff):
        self.my_addr = addr
        self.Fertig_LED1 = Fertig_LED1
        self.Fertig_LED2 = Fertig_LED2
        self.Fertig_LED3 = Fertig_LED3
        self.Fertig_LED4 = Fertig_LED4
        self.Fertig_LED5 = Fertig_LED5
        self.Fertig_LED6 = Fertig_LED6
        self.Fertig_LED7 = Fertig_LED7
        self.Fertig_LED8 = Fertig_LED8
        self.LED_SWITCH = self.Fertig_LED1 & self.Fertig_LED2 & self.Fertig_LED3 & self.Fertig_LED4 & self.Fertig_LED5 & self.Fertig_LED6 & self.Fertig_LED7 & self.Fertig_LED8
        print(self.LED_SWITCH)
        print(1)
        
    def Switch(self):
        self.MyAction = i2c_device(self.my_addr)
        self.MyAction.write_cmd(self.LED_SWITCH)
        sleep(0.0001)

def Fertigation_SwitchC(add, A = 0xff, B = 0xff, C = 0xff, D = 0xff, E = 0xff, F = 0xff, G = 0xff, H = 0xff):
    
    addr = add
    L1=A; L2=B; L3=C; L4=D; L5=E; L6=F; L7=G; L8=H
    LED = L1 & L2 & L3 & L4 & L5 & L6 & L7 & L8
    MyAction = i2c_device(addr)
    MyAction.write_cmd(LED)
    
#fertilizer_switch = i2c_device(Test_ADDRESS)
fertilizer_switch = Fertigation_Switch(0x21,Fertig2,Fertig5)

fertilizer_switcha=-1

class TestThreading(object):  #后台线程，与MySQL数据库通信库函数
    def __init__(self, interval=0.01):
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        global fertilizer_switcha
        while True:
            mydb = mysql.connector.connect(user='smart1',
                             password='greenhouse',
                             host='202.205.84.162',
                             port='6004',
                             database='yunnan_shangde')
            print(mydb)
            mycursor = mydb.cursor()
            mycursor.execute("select * from fertig_switch")
            myresult = mycursor.fetchall()
            for x in myresult:
                print(x)
                fertilizer_switcha=x[1]
                print("*****",fertilizer_switcha,"****")
            time.sleep(self.interval)
tr = TestThreading()
while(True):
    print("what" + ' : First output',fertilizer_switcha)
    time.sleep(0.03)
    Fertigation_SwitchC(0x21,fertilizer_switcha)
    time.sleep(0.03)
    Fertigation_SwitchC(0x21,Fertig5)
    time.sleep(0.03)
    Fertigation_SwitchC(0x21,Fertig6)
    time.sleep(0.03)
    Fertigation_SwitchC(0x21,Fertig7)
    time.sleep(0.03)
    Fertigation_SwitchC(0x21,Fertig8)
    time.sleep(0.03)
