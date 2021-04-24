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
apikey = "DKERAFHXXXXXXX335F"      #需要替代自己的
#DeviceNum = "18030600759"          #需要替代自己的
DeviceNum = "25997573353"           #需要替代自己的
'''
#SensorsID = "Temp" or "Text"
data_cht = [{"id":"Temp","value":["25.0"]},{"id":"Text","value":["SIM7-"]}]
'''
#SensorsID = "id" or "name" or "done"
data_cht = [{"id":"id","value":[2]},{"id":"name","value":["JIM{"]},{"id":"done","value":[1]}]

data = {"id":"4","name":"LOUIS","done":"True"}   #39 for json

def init_gpio():
    GPIO.setwarnings(False) 	#disable warnings
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4,GPIO.OUT)     #PWR
    GPIO.setup(26,GPIO.IN,pull_up_down=GPIO.PUD_UP)  #DTR

    #GPIO.output(4,GPIO.HIGH)
    #time.sleep(2)
    #GPIO.output(4,GPIO.LOW)

def get_chtiot(DevicesID=DeviceNum, SensorsID="id"):
    '''Check local IP is ready'''
    close_http()    #若是已經關閉會得到ERROR
    init_http()
    cmdstr='AT+HTTPPARA="URL","http://iot.cht.com.tw/iot/v1/device/'+ DevicesID +'/sensor/'+ SensorsID +'/rawdata"' #device num.
    ser.write((cmdstr+'\r\n').encode('utf-8'))
    print(receiving(2))
    cmdstr='AT+HTTPPARA="USERDATA","CK: '+ apikey + '"'
    ser.write((cmdstr+'\r\n').encode('utf-8'))
    print(receiving())
    ser.write('AT+HTTPACTION=0\r\n'.encode('utf-8'))    #"GET" session return: +HTTPACTION: 0,601,0
    print(receiving(4))
    #time.sleep(1)

def post_chtiot(DevicesID=DeviceNum, post_data=data_cht):
    '''Check local IP is ready'''
    try:
        close_http()
        init_http()
        #ser.write('AT+HTTPSSL=1\r\n'.encode('utf-8'))   #https (SSL)
        #print(receiving())
        cmdstr='AT+HTTPPARA="URL","http://iot.cht.com.tw/iot/v1/device/'+ DevicesID +'/rawdata"'  #device num.
        ser.write((cmdstr+'\r\n').encode('utf-8'))
        print(receiving())
        cmdstr='AT+HTTPPARA="CONTENT","application/json"'
        ser.write((cmdstr+'\r\n').encode('utf-8'))
        print(receiving())
        cmdstr='AT+HTTPPARA="USERDATA","CK: '+ apikey + '"'
        ser.write((cmdstr+'\r\n').encode('utf-8'))
        print(receiving())
        cmdstr='AT+HTTPDATA=100,3000'
        ser.write((cmdstr+'\r\n').encode('utf-8'))
        time.sleep(0.5)   #坑阿!!!SIM7000處理不來???
        print(receiving())
        ser.write(json.dumps(post_data).encode('utf-8')) #json or text
        #ser.write(chr(26).encode('utf-8')) #調整DOWNLOAD時間達到目的, 否則會多一個字元(Ctrl+z)
        print(receiving(3.8))   #坑阿!!!SIM7000處理不來???
        ser.write('AT+HTTPACTION=1\r\n'.encode('utf-8'))    #POST session return: +HTTPACTION: 1,601,0
        print(receiving(4))
    except:
        GPIO.cleanup()

def read_http():
    ser.write('AT+HTTPREAD\r\n'.encode('utf-8'))        #read back the http
    print(receiving(6))
    '''
    ser.write('AT+SAPBR=1,1\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+HTTPREAD\r\n'.encode('utf-8'))        #read back the http
    print(receiving(4))
    '''

def init_http():
    '''Check local IP is ready'''
    '''Bearer Configure'''
    ser.write('AT+SAPBR=3,1,"APN","internet.iot"\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+SAPBR=0,1\r\n'.encode('utf-8'))   #Close Bearer
    print(receiving())
    ser.write('AT+SAPBR=1,1\r\n'.encode('utf-8'))   #Open Bearer    firmware update need it
    print(receiving())
    ser.write('AT+SAPBR=2,1\r\n'.encode('utf-8'))   #Query Bearer
    print(receiving())
    #ser.write('AT+SAPBR=4,1\r\n'.encode('utf-8'))   #取得 Bearer
    #print(receiving())

    ser.write('AT+HTTPINIT\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+HTTPPARA="CID",1\r\n'.encode('utf-8'))
    print(receiving())
    #ser.write('AT+HTTPPARA="REDIR",1\r\n'.encode('utf-8'))  #Enable HTTP redirect
    #print(receiving())

def close_http():
    ser.write('AT+HTTPTERM\r\n'.encode('utf-8'))        #HTTP Terminal mode #若是已經關閉會得到ERROR
    print(receiving())




def connect_mqtt():
    '''Check local IP is ready'''
    close_mqtt()
    ser.write('AT+CNACT=1,"internet.iot"\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+SMCONF="URL","tcp://iot.cht.com.tw","1883"\r\n'.encode('utf-8'))
    print(receiving())
    #ser.write('AT+SMCONF="CLIENTID","FISH"\r\n'.encode('utf-8'))
    ser.write('AT+SMCONF="CLIENTID","18030600759"\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+SMCONF="KEEPTIME",60\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+SMCONF="CLEANSS",1\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+SMCONF="QOS",0\r\n'.encode('utf-8'))
    print(receiving())
    cmdstr='AT+SMCONF="USERNAME","'+ apikey + '"'
    ser.write((cmdstr+'\r\n').encode('utf-8'))
    print(receiving())
    cmdstr='AT+SMCONF="PASSWORD","'+ apikey + '"'
    ser.write((cmdstr+'\r\n').encode('utf-8'))
    print(receiving())
    ser.write('AT+SMCONF="TOPIC","/v1/device/18030600759/rawdata"\r\n'.encode('utf-8')) #device num.
    print(receiving())
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
    ser.write('AT+SMDISC\r\n'.encode('utf-8'))
    print(receiving(1))




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
    return last_received

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
            print("ser:null")
            exit(1)
        print(ser)
        #st1 = threading.Thread(target=receiving, args=(ser,))
        #st1.start()
    except:
        print("ser:null")
        exit(1)

def shut_module():
    ser.write('AT+CIPSHUT\r\n'.encode('utf-8')) #Shut Down module (成功是LED 3秒閃爍一次)
    print(receiving())
    
def init_module():      #LTE module test
    '''Check module is ready'''
    ser.write('AT\r\n'.encode('utf-8'))         #同步測試
    if receiving()=='':
        GPIO.output(4,GPIO.HIGH)                #PWR pin Hi
        time.sleep(2)
        GPIO.output(4,GPIO.LOW)                 #PWR pin Low
    ser.write('AT+CPIN?\r\n'.encode('utf-8'))   #SIM-car ?
    print(receiving())
    ser.write('AT+CSQ\r\n'.encode('utf-8'))     #查询信号强度 #查詢訊號品質Rssi,Ber
    print(receiving())

    #ser.write('AT+CGDCONT=1,"IP","internet.iot"\r\n'.encode('utf-8'))  #設定電信公司APN
    ser.write('AT+CGDCONT=1,"IP",""\r\n'.encode('utf-8'))              #自動(由基地台決定), 不過要先激活PDP
    print(receiving())
    return 'OK'

################連線基地台LTE#################
def lte_link():         #連線到...(尚失IP後here)
    ser.write('AT+SAPBR=3,1,"Contype","GPRS"\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+SAPBR=3,1,"APN","internet.iot"\r\n'.encode('utf-8'))
    print(receiving())
    #ser.write('AT+SAPBR=3,1,"USER",""\r\n'.encode('utf-8'))
    #print(receiving())
    #ser.write('AT+SAPBR=3,1,"PWD",""\r\n'.encode('utf-8'))
    #print(receiving())
    
    ser.write('at+cstt="internet.iot"\r\n'.encode('utf-8')) #連到internet網路
    print(receiving(3))
    ser.write('at+CIICR\r\n'.encode('utf-8'))   #啟動IP數據網路(成功是LED 0.5秒閃爍)
    print(receiving(4))

################連線基地台GSM#################
def link_GSM():         #連線到...(尚失IP後here)
    ser.write('AT+CNMP=13\r\n'.encode('utf-8')) #Switch GSM only
    print(receiving())
    ser.write('AT+CMNB=3\r\n'.encode('utf-8'))
    print(receiving())
    
    ser.write('at+cstt="internet.iot"\r\n'.encode('utf-8')) #連到internet網路
    print(receiving(3))
    ser.write('at+CIICR\r\n'.encode('utf-8'))   #啟動IP數據網路(成功是LED 0.5秒閃爍)
    print(receiving(4))

################連線基地台LTE#################
def lte_linking():      #連線到...(尚失IP後here)
    '''
    ser.write('at+cops=1,0,”46692”\r\n')   #連上基地台(中華電信), 第一次會花很長時間
    print(receiving(1))
    '''
    ser.write('AT+CNMP=38\r\n'.encode('utf-8')) #Switch LTE only
    #ser.write('AT+CNMP=13\r\n'.encode('utf-8')) #Switch GSM only
    print(receiving(1))
    ser.write('AT+CMNB=1\r\n'.encode('utf-8'))  #LTE(1:Cat-M1 2:NB-IOT 3:Cat-M1 & NB-IOT)
    print(receiving(1))
    ser.write('AT+NBSC=1\r\n'.encode('utf-8'))  #開啟擾碼
    print(receiving(1))
    
    ################連線到IP網路################
    #ser.write('at+cstt="internet,username,password"\r\n'.encode('utf-8'))    #中華電信 
    #ser.write('at+cstt="nbiot"\r\n'.encode('utf-8'))       #遠傳電信
    #ser.write('at+cstt="ctnb"\r\n'.encode('utf-8'))        #中國電信
    #ser.write('at+cstt="CMNET"\r\n'.encode('utf-8'))       #中國移動
    #ser.write('at+cstt="internet"\r\n'.encode('utf-8'))    #中華電信 NB-IOT (低速)
    ser.write('at+cstt="internet.iot"\r\n'.encode('utf-8')) #連到internet網路
    print(receiving(3))
    ser.write('at+CIICR\r\n'.encode('utf-8'))   #啟動IP數據網路(成功是LED 0.5秒閃爍)
    print(receiving(4))

def lte_scanning():     #查詢掃描基地台(index,format,oper),(9 is NB-IOT,7 is CAT-M1)
    ser.write('AT+COPS?\r\n'.encode('utf-8'))       #+COPS: 1,0,"Chunghwa Telecom",7
    print(receiving(3))
    #ser.write('AT+COPS=?\r\n'.encode('utf-8')) #查詢詳細
    #print(receiving(5))

def link_status():       #取得連線後帳號資訊
    ###########透過 AT+CGATT? & AT+CPSI? 指令來確認已連線基地台###########
    ser.write('AT+CPSI?\r\n'.encode('utf-8'))   #查詢 註冊訊息 +CPSI: LTE CAT-M1,Online,466-92,0x2CEC,28608801,434,EUTRAN-BAND3,1750,5,5,-6,-77,-57,16
    print(receiving())
    ser.write('AT+CGATT?\r\n'.encode('utf-8'))  #基站註冊激活AT+CGATT=1 (手動設置) +CGATT: 1 表示可以正常使用數據
    print(receiving())
    ser.write('AT+CGNAPN\r\n'.encode('utf-8'))  #查詢系統APN +CGNAPN: 1,"internet.iot"
    print(receiving())
    ser.write('AT+SAPBR=2,1\r\n'.encode('utf-8'))   #查詢bearer setting +SAPBR: 1,1,"10.173.135.201"
    print(receiving())
    ser.write('AT+SAPBR=4,1\r\n'.encode('utf-8'))   #查詢bearer setting 
    '''
    +SAPBR:
    CONTYPE: GPRS
    APN: internet.iot
    USER:
    PWD:
    '''
    print(receiving())

def localip():          #取得連線後獲得的IP
    ser.write('AT+CIFSR\r\n'.encode('utf-8'))   #查詢本地IP (Get local IP)
    print(receiving())

def ping():
    ser.write('AT+CIPPING="168.95.1.1"\r\n'.encode('utf-8')) #Ping IP
    #ser.write('AT+CIPPING="8.8.8.8"\r\n')
    print(receiving(1))

def ping50():
    ser.write('AT+CIPPING="168.95.1.1",50\r\n'.encode('utf-8')) #Ping IP
    #ser.write('AT+CIPPING="8.8.8.8"\r\n')
    #print(receiving(2))
    print(receiving(3))

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
    '''
    connect_mqtt()
    close_mqtt()
    '''
    status=1
    while True:
        localip()       #check & show my IP address
        #get_http()
        #read_http()
        if GPIO.input(26) == True:
            if status==1:
                #post_http(1)
                
                print("STATUS: Close")
                status=0
            else:
                pass
        else:
            if status==0:
                #post_http(0)
                
                print("STATUS: Open")
                status=1
            else:
                pass
        time.sleep(3)

if __name__ == '__main__':
    init_gpio()
    init_comm()
    #code.interact(local=locals())   #remark for auto-run ('#' cancel interact mode)
    if init_module()=='OK':         #Success initial SIM7000
        try:
            function()
        except KeyboardInterrupt: 
            shut_module()
            if ser != None:  
                ser.close()
        except:
            pass
        finally:
            #st1.join()
            GPIO.cleanup() 