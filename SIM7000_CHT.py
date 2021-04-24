#!/usr/bin/env python3
#coding=utf-8
#測試: 利用http協議直接傳送狀態回服務器, 在CAT-M1 or NB-IOT
'''NET LED: (SIM7000C module)
Standby: 開機1秒閃爍週期
Internet online: 0.5秒閃爍週期
Shuntdowm: 是3秒閃爍週期
PowerDown: 熄滅
'''
#Raspberry pi need to setup 
#sudo raspi-config      #Interfacing Options -> Serial login -> no, Serial hardware -> yes
#sudo nano /boot/config.txt     #add==> enable_uart=1
#sudo nano /boot/cmdline.txt    #deleted "console=ttyAMA0,115200 kgdboc=ttyAMA0,115200"
#sudo apt-get install minicom   #for try AT command
#minicom -D /dev/ttyAMA0 -b115200     #Run minicom for Raspberry pi3 pi4

#cd /SIM7000C/bcm2835
#chmod +x configure && ./configure && sudo make && sudo make install    #遮個才成功

import  RPi.GPIO as GPIO
import time
import serial
#import threading
import json
import paho.mqtt.client as mqtt     #pip3 install paho-mqtt          #要搞這個
import code 

ser=''
MQTTHOST = "iot.cht.com.tw"
MQTTPORT = 1883
apikey = "DKERAFHXXXXXXX335F"       #需要替代自己的
#DeviceNum = "18030600759"          #需要替代自己的
DeviceNum = "25997573353"           #需要替代自己的
'''#to 魚場
#SensorsID="Temp" or "Text"         
data_cht = [{"id":"Temp","value":["25.0"]},{"id":"Text","value":["SIM7-"]}]
'''
'''#to 發電廠'''
#SensorsID="id" or "name" or "done" 
data_cht = [{"id":"id","value":[2]},{"id":"name","value":["LOUIS"]},{"id":"done","value":[1]}]

def init_gpio():
    GPIO.setwarnings(False) 	#disable warnings
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4,GPIO.OUT)     #PWR Control for Power ON or Power OFF
    GPIO.setup(26,GPIO.IN,pull_up_down=GPIO.PUD_UP)  #DTR control

def get_chtiot(DevicesID=DeviceNum, SensorsID="id"):
    '''Check local IP is ready'''
    try:
        close_http()    #若是已經關閉會得到ERROR
        init_http()
        cmdstr='AT+HTTPPARA="URL","http://iot.cht.com.tw/iot/v1/device/'+ DevicesID +'/sensor/'+ SensorsID +'/rawdata"' #device num.
        Send_AT(cmdstr, 2)
        cmdstr='AT+HTTPPARA="USERDATA","CK: '+ apikey + '"'
        Send_AT(cmdstr)
        Send_AT('AT+HTTPACTION=0', 4)    #"GET" session return: +HTTPACTION: 0,601,0
    except:
        GPIO.cleanup()

def post_chtiot(DevicesID=DeviceNum, post_data=data_cht):
    '''Check local IP is ready'''
    try:
        close_http()
        init_http()
        #Send_AT('AT+HTTPSSL=1')   #https (SSL)
        cmdstr='AT+HTTPPARA="URL","http://iot.cht.com.tw/iot/v1/device/'+ DevicesID +'/rawdata"'  #device num.
        Send_AT(cmdstr)
        cmdstr='AT+HTTPPARA="CONTENT","application/json"'
        Send_AT(cmdstr)
        cmdstr='AT+HTTPPARA="USERDATA","CK: '+ apikey + '"'
        Send_AT(cmdstr)

        cmdstr='AT+HTTPDATA=100,3000'
        ser.write((cmdstr+'\r\n').encode('utf-8'))
        time.sleep(0.5)   #坑阿!!!SIM7000處理不來???
        print(receiving())
        ser.write(json.dumps(post_data).encode('utf-8')) #json or text
        #ser.write(chr(26).encode('utf-8')) #調整DOWNLOAD時間達到目的, 否則會多一個字元(Ctrl+z)
        print(receiving(3.8))   #坑阿!!!SIM7000處理不來???
        Send_AT('AT+HTTPACTION=1', 4)    #POST session return: +HTTPACTION: 1,601,0

    except:
        GPIO.cleanup()

def read_http():
    try:
        Send_AT('AT+HTTPREAD', 6)           #read back the http
        '''
        Send_AT('AT+SAPBR=1,1')
        Send_AT('AT+HTTPREAD', 4)           #read back the http
        '''
    except:
        GPIO.cleanup()

def init_http():
    '''Check local IP is ready'''
    '''Bearer Configure'''
    try:
        Send_AT('AT+SAPBR=3,1,"APN","internet.iot"')
        Send_AT('AT+SAPBR=0,1')             #Close Bearer
        Send_AT('AT+SAPBR=1,1')             #Open Bearer    firmware update need it
        Send_AT('AT+SAPBR=2,1')             #Query Bearer
        #Send_AT('AT+SAPBR=4,1')            #取得 Bearer
        Send_AT('AT+HTTPINIT')
        Send_AT('AT+HTTPPARA="CID",1')
        #Send_AT('AT+HTTPPARA="REDIR",1')   #Enable HTTP redirect
    except:
        GPIO.cleanup()
def close_http():
    try:
        Send_AT('AT+HTTPTERM')              #HTTP Terminal mode #若是已經關閉會得到ERROR
    except:
        GPIO.cleanup()



def connect_mqtt():
    '''Check local IP is ready'''
    close_mqtt()
    Send_AT('AT+CNACT=1,"internet.iot"')
    Send_AT('AT+SMCONF="URL","tcp://iot.cht.com.tw","1883"')
    #Send_AT('AT+SMCONF="CLIENTID","FISH"')
    Send_AT('AT+SMCONF="CLIENTID","18030600759"')
    Send_AT('AT+SMCONF="KEEPTIME",60')
    Send_AT('AT+SMCONF="CLEANSS",1')
    Send_AT('AT+SMCONF="QOS",0')
    cmdstr='AT+SMCONF="USERNAME","'+ apikey + '"'
    Send_AT(cmdstr)
    cmdstr='AT+SMCONF="PASSWORD","'+ apikey + '"'
    Send_AT(cmdstr)
    Send_AT('AT+SMCONF="TOPIC","/v1/device/18030600759/rawdata"') #device num.

    '''
    #cmdstr='AT+SMCONF="MESSAGE","'+ json.dumps(data_cht) +'"\r\n'
    cmdstr='AT+SMCONF="MESSAGE","'+ str(data_cht) +'"\r\n'
    #cmdstr='AT+SMCONF="MESSAGE","'+ str({"id":"Text","value":["SIM70"]})+'"\r\n'
    ser.write(cmdstr.encode('utf-8'))
    time.sleep(0.5)
    print(receiving())
    '''
    ser.write('AT+SMCONN\r\n'.encode('utf-8'))
    time.sleep(0.5)
    print(receiving(5))

    '''Mqtt Publish'''
    cmdstr='AT+SMPUB="/v1/device/18030600759/rawdata",100,1,"'+ str(data_cht) +'"\r\n'
    ser.write(cmdstr.encode('utf-8'))
    time.sleep(0.5)
    print(receiving(5))
    
def close_mqtt():       #Close TCP/UDP
    Send_AT('AT+SMDISC', 1)



#echo 'AT+SAPBR=2,1\r\n' > /dev/ttyAMA0     #Under bash
def receiving(timeout=0.25):    #簡單做法, 基礎用0.25秒計時, 否則自行定義
    #ser.flushInput()           #清除接收緩衝區
    last_received=''
    while timeout>0:
        time.sleep(0.2)
        count = ser.inWaiting() #取得當下緩衝區字元數
        while count != 0:
            last_received += ser.read(count).decode('utf-8')    #getData += bytes.decode(ch)
            time.sleep(0.2)    #
            count = ser.inWaiting() #取得當下緩衝區字元數
        timeout = timeout-0.25
    return last_received.strip()

def Send_AT(cmd, timeout=0.25):
    ser.write((cmd+'\r\n').encode('utf-8')) 
    print(receiving(timeout=timeout))

def init_comm():        #Module connect 
    global ser
    if ser!='':
        ser.close()
    try:
        ser = serial.Serial("/dev/ttyUSB3",115200)  #SIM7000C USB port
        #ser = serial.Serial("/dev/ttyUSB4",115200)  #SIM7000C USB port
        #ser = serial.Serial("/dev/ttyAMA0",115200) #Pi3,Pi4 serial port
        #ser = serial.Serial("/dev/ttyS0",115200)  #Pi2 serial port
        if ser=='':
            #print("ser:null")
            print("Check the serial port")
            exit(1)     #terminate this program
        print(ser)
        #st1 = threading.Thread(target=receiving, args=(ser,))
        #st1.start()
    except:
        #print("ser:null")
        print("Check the serial port")
        exit(1)     #terminate this program

def shut_module():
    Send_AT('AT+CIPSHUT') #Shut Down module (成功是LED 3秒閃爍一次)
    
def init_module():      #LTE module test
    '''Check module is ready'''
    ser.write('AT\r\n'.encode('utf-8'))         #同步測試
    if receiving()=='':
        print('Turn ON PWR')
        GPIO.output(4,GPIO.HIGH)                #PWR pin Hi
        time.sleep(2)
        GPIO.output(4,GPIO.LOW)                 #PWR pin Low
    Send_AT('AT+CPIN?')                             #SIM-car here ?
    Send_AT('AT+CSQ')                               #查询信号强度 #查詢訊號品質Rssi,Ber
    #Send_AT('AT+CGDCONT=1,"IP","internet.iot"')    #設定電信公司APN
    Send_AT('AT+CGDCONT=1,"IP",""')                 #自動(由基地台決定), 不過要先激活PDP
    return 'OK'

################連線基地台LTE#################
def lte_link():             #連線到...(尚失IP後here)
    Send_AT('AT+SAPBR=3,1,"Contype","GPRS"')
    Send_AT('AT+SAPBR=3,1,"APN","internet.iot"')
    #Send_AT('AT+SAPBR=3,1,"USER",""')
    #Send_AT('AT+SAPBR=3,1,"PWD",""')
    
    Send_AT('at+cstt="internet.iot"', 3)#連到internet網路
    Send_AT('at+CIICR', 4)              #啟動IP數據網路(成功是LED 0.5秒閃爍)

################連線基地台GSM#################
def link_GSM():             #連線到...(尚失IP後here)
    Send_AT('AT+CNMP=13')   #Switch GSM only
    Send_AT('AT+CMNB=3')
    
    Send_AT('at+cstt="internet.iot"', 3)#連到internet網路
    Send_AT('at+CIICR', 4)              #啟動IP數據網路(成功是LED 0.5秒閃爍)

################連線基地台LTE#################
def lte_linking():      #連線到...(尚失IP後here)
    #Send_AT('at+cops=1,0,"46692"', 3)   #連上基地台(中華電信), 第一次會花很長時間
    Send_AT('AT+CNMP=38', 1)            #Switch LTE only
    #Send_AT('AT+CNMP=13', 1)             #Switch GSM only
    Send_AT('AT+CMNB=1', 1)             #LTE(1:Cat-M1 2:NB-IOT 3:Cat-M1 & NB-IOT)
    Send_AT('AT+NBSC=1', 1)             #開啟擾碼
    
    ################連線到IP網路################
    #Send_AT('at+cstt="internet,username,password"', 3)    #中華電信 
    #Send_AT('at+cstt="nbiot"', 3)       #遠傳電信
    #Send_AT('at+cstt="ctnb"', 3)        #中國電信
    #Send_AT('at+cstt="CMNET"', 3)       #中國移動
    #Send_AT('at+cstt="internet"', 3)    #中華電信 NB-IOT (低速)
    Send_AT('at+cstt="internet.iot"', 3)#連到internet網路
    Send_AT('at+CIICR', 4)              #啟動IP數據網路(成功是LED 0.5秒閃爍)

def lte_scanning():         #查詢掃描基地台(index,format,oper),(9 is NB-IOT,7 is CAT-M1)
    Send_AT('AT+COPS?', 3)              #+COPS: 1,0,"Chunghwa Telecom",7
    #Send_AT('AT+COPS=?', 5)            #查詢詳細

def link_status():          #取得連線後帳號資訊
    ###########透過 AT+CGATT? & AT+CPSI? 指令來確認已連線基地台###########
    Send_AT('AT+CPSI?')     #查詢 註冊訊息 +CPSI: LTE CAT-M1,Online,466-92,0x2CEC,28608801,434,EUTRAN-BAND3,1750,5,5,-6,-77,-57,16
    Send_AT('AT+CGATT?')    #基站註冊激活AT+CGATT=1 (手動設置) +CGATT: 1 表示可以正常使用數據
    Send_AT('AT+CGNAPN')    #查詢系統APN +CGNAPN: 1,"internet.iot"
    Send_AT('AT+SAPBR=2,1') #查詢bearer setting +SAPBR: 1,1,"10.173.135.201"
    Send_AT('AT+SAPBR=4,1') #查詢bearer setting 
    '''
    +SAPBR:
    CONTYPE: GPRS
    APN: internet.iot
    USER:
    PWD:
    '''

def localip():              #取得連線後獲得的IP
    Send_AT('AT+CIFSR')     #查詢本地IP (Get local IP)

def ping():
    Send_AT('AT+CIPPING="168.95.1.1"', 1)   #Ping IP
    #Send_AT('AT+CIPPING="8.8.8.8"', 1)

def ping50():
    Send_AT('AT+CIPPING="168.95.1.1",50', 3)#Ping IP
    #Send_AT('AT+CIPPING="8.8.8.8"', 3)

def function():
    #lte_scanning()     #查詢可以連線...?
    #lte_link()       #連線到...基地台與internet online if OK
    lte_linking()       #連線到...基地台與internet online if OK
    #############應用:查看IP################
    localip()
    #############應用:查詢連線狀態##########
    link_status()
    #############應用:ping測試##############
    #ping()
    #ping50()
    #############應用:HTTP連線測試##########
    
    #get_chtiot(DeviceNum, SensorsID="id")
    #get_chtiot(DeviceNum, SensorsID="name")
    get_chtiot(DeviceNum, SensorsID="done")
    #post_chtiot(DeviceNum, data_cht)
    read_http()
    close_http()
    
    #############應用:MQTT連線測試##########
    '''never testing
    connect_mqtt()
    close_mqtt()
    '''
    status=1
    while True:
        localip()       #check & show my IP address
        #my_get_http()
        #read_http()
        if GPIO.input(26) == True:
            if status==1:
                #post_http(1)
                
                print("STATUS: Door-Close")
                status=0
            else:
                pass
        else:
            if status==0:
                #post_http(0)
                
                print("STATUS: Door-Open")
                status=1
            else:
                pass
        time.sleep(3)

if __name__ == '__main__':
    init_gpio()
    init_comm()
    #code.interact(local=locals())   #remark for auto-run ('#' cancel interact mode)
    #if init_module()=='OK':         #Success initial SIM7000
    if 'OK' in init_module():         #Success initial SIM7000
        try:
            function()
        except KeyboardInterrupt: 
            shut_module()
            #if ser != None:  
            #    ser.close()
        except:
            pass
        finally:
            #st1.join()
            GPIO.cleanup() 
    if ser != None:  
        ser.close()
        GPIO.cleanup() 