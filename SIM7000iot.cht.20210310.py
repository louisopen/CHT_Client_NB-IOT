#!/usr/bin/env python3
#coding=utf-8
#測試: 利用http協議直接傳送狀態回服務器, 在CAT-M1
'''NET LED: of SIM7000C
Standby: 開機1秒閃爍週期
Internet: 0.5秒閃爍週期
Shuntdowm: 是3秒閃爍週期
PowerDown: 熄滅
'''
#Setup Raspberry pi system 
#sudo raspi-config      #Interfacing Options -> Serial login -> no, Serial hardware -> yes
#sudo nano /boot/config.txt     #add==> enable_uart=1
#sudo nano /boot/cmdline.txt    #deleted "console=ttyAMA0,115200 kgdboc=ttyAMA0,115200"
#sudo apt-get install minicom   #Try application
#minicom -D /dev/ttyAMA0 -b115200     #Raspberry pi3

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
apikey = "DKERAFHXXXXXXX335F"
DeviceNum = "18030600759"
Sensor_Temp = "Temp"
Sensor_Text = "Text"
headers = '{"accept": "application/json","CK": '+apikey+'}'
data='{"id":"Text","value":"SIM70"}'   #String
#data={"id":"Text","value":["SIM70"]}    #Json

def init_gpio():
    GPIO.setwarnings(False) 	#disable warnings
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4,GPIO.OUT)     #PWR
    GPIO.setup(26,GPIO.IN,pull_up_down=GPIO.PUD_UP)  #DTR

    #GPIO.output(4,GPIO.HIGH)
    #time.sleep(2)
    #GPIO.output(4,GPIO.LOW)

def get_http():
    close_http()    #若是已經關閉會得到ERROR
    init_http()
    #ser.write('AT+HTTPPARA="URL","http://www.m2msupport.net/m2msupport/test.php"\r\n'.encode('utf-8'))  #GET "test"
    #ser.write('AT+HTTPPARA="URL","http://httpbin.org/get"\r\n'.encode('utf-8'))     #GET the sample
    ser.write('AT+HTTPPARA="URL","http://iot.cht.com.tw/iot"\r\n'.encode('utf-8')) #GET my test page
    print(receiving())
    #ser.write('AT+HTTPPARA="PROPORT",1883\r\n'.encode('utf-8'))   #Restful 80 or 443
    #ser.write('AT+HTTPPARA="CONTENT",multipart/form-data\r\n'.encode('utf-8'))
    #ser.write('AT+HTTPPARA="CONTENT","text/plain; charset=UTF-8"\r\n'.encode('utf-8'))
    #print(receiving())

    ser.write('AT+HTTPACTION=0\r\n'.encode('utf-8'))    #"GET" session return: +HTTPACTION: 0,601,0
    print(receiving(4))

def post_http(param="SensorID"):
    try:
        close_http()
        init_http()
        ser.write('AT+HTTPPARA="URL","https://iot.cht.com.tw/iot/v1/device/18030600759/rawdata"\r\n'.encode('utf-8')) #device num.
        print(receiving())
        '''
        ser.write('AT+HTTPPARA="UA",80\r\n'.encode('utf-8'))   #tcp port: default is 80
        print(receiving())
        ser.write('AT+HTTPPARA="PROIP","10.0.0.172"\r\n'.encode('utf-8'))   #Proxy IP ?
        print(receiving())
        ser.write('AT+HTTPPARA="PROPORT",80\r\n'.encode('utf-8'))   #Proxy port ?
        print(receiving())
        '''
        #ser.write('AT+HTTPPARA="CONTENT","text/html"\r\n'.encode('utf-8'))
        ser.write('AT+HTTPPARA="CONTENT","application/json"\r\n'.encode('utf-8'))
        #ser.write('AT+HTTPPARA="CONTENT","'+str(headers)+'"\r\n'.encode('utf-8'))
        print(receiving())
        #rawdatas=json.dumps(data)
        #ser.write('AT+HTTPPARA="USERDATA",'+data+'\r\n'.encode('utf-8'))
        #ser.write('AT+HTTPPARA="USERDATA","'+json.dumps(data)+'"\r\n'.encode('utf-8'))
        #ser.write('AT+HTTPPARA="USERDATA",'+str(json.dumps(data))+'\r\n'.encode('utf-8'))
        #ser.write('AT+HTTPPARA="USERDATA",{"accept":"application/json","CK": '+apikey+'"}\r\n'.encode('utf-8'))
        #print(receiving())

        ser.write('AT+HTTPDATA=94,5000\r\n'.encode('utf-8'))   #size,time(ms)
        ser.write(str(headers+data).encode('utf-8'))
        ser.write(chr(26).encode('utf-8'))
        print(receiving())
        
        ser.write('AT+HTTPPARA="TIMEOUT",60\r\n'.encode('utf-8'))
        print(receiving())
        #ser.write('AT+HTTPPARA?\r\n'.encode('utf-8'))
        #print(receiving(3))

        #ser.write('AT+HTTPDATA=50,1000\r\n'.encode('utf-8')) #module will download it
        #print(receiving(1))
        ser.write('AT+HTTPACTION=1\r\n'.encode('utf-8'))    #POST session return: +HTTPACTION: 1,601,0
        print(receiving(5))
        #ser.write('AT+HTTPSTATUS?\r\n'.encode('utf-8'))
        #print(receiving(3))
    except:
        GPIO.cleanup()

def read_http():
    ser.write('AT+HTTPREAD\r\n'.encode('utf-8'))        #read back the http
    print(receiving(4))
    '''
    ser.write('AT+SAPBR=1,1\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+HTTPREAD\r\n'.encode('utf-8'))        #read back the http
    print(receiving(4))
    '''
def init_http():
    '''Bearer Configure'''
    ser.write('AT+SAPBR=3,1,"APN","internet.iot"\r\n'.encode('utf-8'))
    print(receiving())
    #ser.write('AT+SAPBR=1,1\r\n'.encode('utf-8'))   #Open Bearer
    #print(receiving())
    ser.write('AT+SAPBR=2,1\r\n'.encode('utf-8'))   #Query Bearer
    print(receiving())
    #ser.write('AT+SAPBR=4,1\r\n'.encode('utf-8'))   #取得 Bearer
    #print(receiving())
    #ser.write('AT+SAPBR=0,1\r\n'.encode('utf-8'))   #Close Bearer, ERROR not support
    #print(receiving())
    #ser.write('AT+HTTPSSL=?\r\n'.encode('utf-8'))   #https (SSL), ERROR not support
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





def send_tcp(param=1):
    connect_tcp()
    ser.write('AT+CIPSEND\r\n'.encode('utf-8')) 
    #ser.write('AT+CIPSEND="HEAD/HTTP/1.1\r\nHost:www.taobao.com\r\nConnection:keep-alive\r\n\r\n"'.encode('utf-8'))
    print(receiving(2))
    
    #ser.write('Hello!\r\n'.encode('utf-8'))    #for 101.132.43.66
    ser.write('GET/HTTP/1.1'.encode('utf-8'))   #for www.taobao.com
    #ser.write('1234567890ABCDEFGHIJ'.encode('utf-8')) #for 47.94.228.89
    ser.write(chr(26).encode('utf-8'))          #結束輸入模式0x1A
    print(receiving(3))
    
def read_tcp(param=1):  #read back
    ser.write('AT+CIPSEND?\r\n'.encode('utf-8')) 
    print(receiving(5))

def connect_tcp():
    #ser.write('AT+CIPSTART="TCP","iot.cht.com.tw",1883\r\n'.encode('utf-8'))   #for CHT mqtt
    ser.write('AT+CIPSTART="TCP","www.taobao.com",80\r\n'.encode('utf-8'))
    #ser.write('AT+CIPSTART="tcp","101.132.43.66","80"\r\n'.encode('utf-8'))
    #ser.write('AT+CIPSTART="UDP","101.132.43.66","80"\r\n'.encode('utf-8'))
    #ser.write('AT+CIPSTART="tcp","47.94.228.89","4066"\r\n'.encode('utf-8'))
    print(receiving(4))
    #ser.write('AT+CIPATS=1,3\r\n'.encode('utf-8'))
    #print(receiving(4))

def close_tcp():       #Close TCP/UDP
    ##################關閉連線###################
    #ser.write('AT+CIPCLOSE=1\r\n'.encode('utf-8'))
    ser.write('AT+CIPCLOSE\r\n'.encode('utf-8'))
    print(receiving())




def connect_mqtt():
    ser.write('AT+SMCONF="CLIENTID","FISH"\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+SMCONF="KEEPTIME",60\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+SMCONF="QOS",1\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+SMCONF="USERNAME",'+apikey+'\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+SMCONF="PASSWORD",'+apikey+'\r\n'.encode('utf-8'))
    print(receiving())

    ser.write('AT+SMCONF="TOPIC","/v1/device/'+DeviceNum+'/rawdata"\r\n'.encode('utf-8')) #device num.
    print(receiving())

    data=[{"id":"Text","value":["SIM7000CCC"]}] 
    ser.write('AT+SMCONF="MESSAGE",'.encode('utf-8') + ('"'+ json.dumps(data)+'"\r\n').encode('utf-8'))
    print(receiving())

    #ser.write('AT+SMCONF="URL","iot.cht.com.tw","1883"\r\n'.encode('utf-8'))
    #ser.write('AT+SMCONF="URL","iot.cht.com.tw"'.format())
    ser.write('AT+SMCONF="URL","iot.cht.com.tw"\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+SMCONN\r\n'.encode('utf-8'))
    #Wait data for 3 sec.
    print(receiving(3))

def publish_http(sensor_number="Text", sensor_value="SIM7000C"): #發佈
    #my_sensor_temp(self.DeviceNum, sensor_number, sensor_value)
    data=[{"id":sensor_number,"value":[sensor_value]}]    
    #return (json.dumps(data)+'\r\n').encode('utf-8')
    ser.write('AT+SMCONF="MESSAGE",'.encode('utf-8') + ('"'+ json.dumps(data)+'"\r\n').encode('utf-8'))
    print(receiving(1))

def close_mqtt():       #Close TCP/UDP
    ser.write('AT+SMDISC\r\n'.encode('utf-8'))
    print(receiving(1))




#echo 'AT+SAPBR=2,1\r\n' > /dev/ttyAMA0     #Under bash
def receiving(timeout=0.25):     #簡單做法, 基礎用0.25秒計時, 否則自行定義
    #ser.flushInput()           #清除接收緩衝區
    last_received=''
    while timeout>0:
        time.sleep(0.125)
        count = ser.inWaiting() #取得當下緩衝區字元數
        while count != 0:
            last_received += ser.read(count).decode('utf-8')    #getData += bytes.decode(ch)
            time.sleep(0.125)       #
            count = ser.inWaiting() #取得當下緩衝區字元數
        timeout = timeout-0.25
    return last_received

def init_comm():        #Module connect 
    global ser
    if ser!='':
        ser.close()
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

def shut_module():
    ser.write('AT+CIPSHUT\r\n'.encode('utf-8')) #Shut Down module (成功是LED 3秒閃爍一次)
    print(receiving())
    
def init_module():      #LTE module test
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
    ser.write('AT+CGDCONT=1,"IP",""\r\n'.encode('utf-8'))              #自動(由基地台決定)
    print(receiving())
    return 'OK'

def lte_scanning():     #查詢掃描基地台(index,format,oper),(9 is NB-IOT,7 is CAT-M1)
    ser.write('AT+COPS?\r\n'.encode('utf-8'))
    print(receiving(3))

    #ser.write('AT+COPS=?\r\n'.encode('utf-8')) #查詢詳細
    #print(receiving(5))

################連線基地台LTE#################
def lte_link():
    ser.write('AT+SAPBR=3,1,"Contype","GPRS"\r\n'.encode('utf-8'))
    print(receiving())
    ser.write('AT+SAPBR=3,1,"APN","internet.iot"\r\n'.encode('utf-8'))
    print(receiving())
    #ser.write('AT+SAPBR=3,1,"USER",""\r\n'.encode('utf-8'))
    #print(receiving())
    #ser.write('AT+SAPBR=3,1,"PWD",""\r\n'.encode('utf-8'))
    #print(receiving())
    #ser.write('AT+SAPBR=1,1\r\n'.encode('utf-8'))
    #print(receiving(5))

################連線基地台GSM#################
def link_GSM():
    ser.write('AT+CNMP=13\r\n'.encode('utf-8')) #Switch GSM only
    print(receiving())
    ser.write('AT+CMNB=3\r\n'.encode('utf-8'))
    print(receiving())

################連線基地台LTE#################
def lte_linking():      #連線到...
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

def link_status():       #取得連線後帳號資訊
    ###########透過 AT+CGATT? & AT+CPSI? 指令來確認已連線基地台###########
    ser.write('AT+CPSI?\r\n'.encode('utf-8'))   #查詢 註冊訊息
    print(receiving())
    ser.write('AT+CGATT?\r\n'.encode('utf-8'))  #註冊激活AT+CGATT=1 (自動運行) 1:表示可以正常使用數據
    print(receiving())
    ser.write('AT+CGNAPN\r\n'.encode('utf-8'))  #查詢系統APN
    print(receiving())
    ser.write('AT+SAPBR=4,1\r\n'.encode('utf-8'))   #查詢
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
    try:
        #lte_scanning()     #查詢可以連線...?
        #lte_link()       #連線到...基地台與internet
        lte_linking()       #連線到...基地台與internet
        #############應用:查看IP################
        localip()
        #############應用:查詢連線狀態##########
        link_status()
        #############應用:ping測試##############
        #ping()
        #ping50()
        #############應用:TCP連線測試###########
        '''
        send_tcp()
        read_tcp()
        close_tcp()
        '''
        #############應用:HTTP連線測試##########
        
        #get_http()
        post_http()
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
            #link_status()
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
    except KeyboardInterrupt: 
        shut_module()
        if ser != None:  
            ser.close()
    except:
        pass
    finally:
        #st1.join()
        GPIO.cleanup() 

if __name__ == '__main__':
    init_gpio()
    init_comm()
    #code.interact(local=locals())   #remark for auto-run ('#' cancel interact mode)
    if init_module()=='OK':         #Initial SIM7000
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