#!/usr/bin/env python3
#coding=utf-8
#測試: 利用http協議直接傳送狀態回服務器, 在CAT-M1

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

def init_gpio():
	GPIO.setwarnings(False) 	#disable warnings
	GPIO.setmode(GPIO.BCM)
    GPIO.setup(04,GPIO.OUT)     #PWR
    GPIO.setup(26,GPIO.IN,pull_up_down=GPIO.PUD_UP)  #DTR
    GPIO.output(04,GPIO.LOW)
    time.sleep(0.5)

def get_http():
    ser.write('AT+HTTPPARA="URL","http://iot.cht.com.tw/iot"\r\n'.encode('utf-8'))
    #ser.write('AT+HTTPPARA="URL","http://minimi.ukfit.webfactional.com"\r\n'.encode('utf-8'))
    print(receiving(ser))
    ser.write('AT+HTTPACTION=0\r\n'.encode('utf-8'))    #GET session start,  +HTTPACTION: 0,601,0
    print(receiving(ser))
    #Wait data for 3 sec.
    #ser.write('AT+HTTPREAD\r\n'.encode('utf-8'))        #read back the http
    #print(receiving(ser))
    #ser.write('AT+HTTTERM\r\n'.encode('utf-8'))        
    #print(receiving(ser))
    #ser.write('AT+SAPBR=0,1\r\n'.encode('utf-8'))
    #print(receiving(ser))

def post_http(param="SensorID"):

    ser.write('AT+HTTPPARA="USERDATA","id:Text&value:SIM7000"\r\n'.encode('utf-8'))
    print(receiving(ser))

    ser.write('AT+HTTPPARA="URL","http://iot.cht.com.tw/iot/v1/device/18030600759/rawdata"\r\n'.encode('utf-8')) #device num.
    print(receiving(ser))

    ser.write('AT+HTTPPARA="UA",80\r\n'.encode('utf-8'))   #Restful 80 or 443
    print(receiving(ser))

    ser.write('AT+HTTPPARA="PROPORT",80\r\n'.encode('utf-8'))   #Restful 80 or 443
    print(receiving(ser))

    #ser.write('AT+HTTPPARA="CONTENT","text/html"\r\n'.encode('utf-8'))
    ser.write('AT+HTTPPARA="CONTENT","application/json"\r\n'.encode('utf-8'))
    print(receiving(ser))

    ser.write('AT+HTTPPARA="TIMEOUT",60\r\n'.encode('utf-8'))
    print(receiving(ser))

    #ser.write('AT+HTTPDATA=50,1000\r\n'.encode('utf-8')) #module will download it
    #print(receiving(ser))
    #time.sleep(1)
    ser.write('AT+HTTPACTION=1\r\n'.encode('utf-8'))    #POST session start
    print(receiving(ser))
    #Wait data for 3 sec.

def read_http():
    ser.write('AT+HTTPREAD\r\n'.encode('utf-8'))        #read back the http
    print(receiving(ser))

def init_http():
    ser.write('AT+SAPBR=3,1,"APN","internet.iot"\r\n'.encode('utf-8'))
    print(receiving(ser))
    ser.write('AT+SAPBR=1,1\r\n'.encode('utf-8'))
    print(receiving(ser))
    ser.write('AT+SAPBR=2,1\r\n'.encode('utf-8'))
    print(receiving(ser))
    ser.write('AT+HTTPPARA="CID",1\r\n'.encode('utf-8'))
    print(receiving(ser))
    #ser.write('AT+HTTPTERM\r\n'.encode('utf-8'))   #HTTP Terminal mode
    #print(receiving(ser))
    ser.write('AT+HTTPINIT\r\n'.encode('utf-8'))
    print(receiving(ser))




def connect_tcp():
    ser.write('AT+CIPSTART="TCP","iot.cht.com.tw",1883\r\n'.encode('utf-8'))
    #ser.write('AT+CIPSTART="TCP","www.taobao.com",80\r\n'.encode('utf-8'))
    #ser.write('at+cipstart="tcp","ftp.isu.edu.tw",21\r\n'.encode('utf-8'))     #FTP
    #ser.write('AT+CIPSTART="TCP","123.123.123.123",9487\r\n'.encode('utf-8'))
    print(receiving(ser))
    #Wait 3 sec.

def close_tcp():       #Close TCP/UDP
    ser.write('AT+CIPCLOSE\r\n'.encode('utf-8'))
    print(receiving(ser))

def send_tcp(param=1):
    ser.write('AT+CIPSEND=I love you\r\n'.encode('utf-8')) 
    #ser.write('AT+CIPSEND="HEAD/HTTP/1.1\r\nHost:www.taobao.com\r\nConnection:keep-alive\r\n\r\n"'.encode('utf-8'))
    print(receiving(ser))
    #Wait 3 sec.
    ##################關閉連線###################
    #ser.write('AT+CIPCLOSE=1\r\n'.encode('utf-8'))
    #print(receiving(ser))

def publish_http(sensor_number="Text", sensor_value="SIM7000C"): #發佈
    #my_sensor_temp(self.DeviceNum, sensor_number, sensor_value)
    data=[{"id":sensor_number,"value":[sensor_value]}]    
    #return (json.dumps(data)+'\r\n').encode('utf-8')
    ser.write('AT+SMCONF="MESSAGE",'.encode('utf-8') + ('"'+ json.dumps(data)+'"\r\n').encode('utf-8'))
    time.sleep(1)    
    print(receiving(ser))




#echo 'AT+SAPBR=2,1\r\n' > /dev/ttyAMA0     #Under bash
def receiving(ser):     #寫法簡單, 但有坑! 先頂著!
    #ser.flushInput()           #清除接收緩衝區
    last_received=''
    time.sleep(0.1)       
    count = ser.inWaiting()     #取得當下緩衝區字元數
    while count != 0:
        last_received += ser.read(count).decode('utf-8')        #getData += bytes.decode(ch)
        #print(count)
        time.sleep(0.125)       #
        count = ser.inWaiting() #取得當下緩衝區字元數
    last_received += ser.read(count).decode('utf-8')
    #print(count)
    return last_received

def init_comm():        #Module connect 
    global ser
    ser = serial.Serial("/dev/ttyAMA0",115200) #Pi3
    #ser = serial.Serial("/dev/ttyS0",115200)  #Pi2 
    if ser=='':
        print("ser:null")
        exit(0)
    print(ser)
    #st1 = threading.Thread(target=receiving, args=(ser,))
    #st1.start()

def shut_module():
    ser.write('AT+CIPSHUT\r\n'.encode('utf-8')) #Shut Down module
    print(receiving(ser))
    
def init_module():      #LTE module test
    ser.write('AT\r\n'.encode('utf-8'))         #同步測試
    print(receiving(ser))
    ser.write('AT+CPIN?\r\n'.encode('utf-8'))   #SIM-car ?
    print(receiving(ser))
    ser.write('AT+CSQ\r\n'.encode('utf-8'))     #查询信号强度 #查詢訊號品質Rssi,Ber
    print(receiving(ser))

def lte_scanning():     #查詢掃描基地台(index,format,oper),(9 is NB-IOT,7 is CAT-M1)
    ser.write('AT+COPS?\r\n'.encode('utf-8'))
    #ser.write('AT+COPS=?\r\n'.encode('utf-8'))
    time.sleep(2)
    print(receiving(ser))

def lte_linking():      #連線
    ################連線基地台#################
    #ser.write('AT+CGDCONT=1,"IP","internet.iot"\r\n')  #設定電信公司APN
    #ser.write('AT+CGDCONT=1,"IP",""\r\n')              #自動(由基地台決定)
    #print(receiving(ser))
    #ser.write('at+cops=1,2,”46692”\r\n')   #連上基地台(中華電信), 第一次會花很長時間
    #print(receiving(ser))
    ser.write('AT+CNMP=38\r\n'.encode('utf-8')) #LTE only
    print(receiving(ser))
    time.sleep(0.5)
    ser.write('AT+CMNB=1\r\n'.encode('utf-8'))  #LTE(1:Cat-M1 and 3:NB-IOT)
    print(receiving(ser))
    time.sleep(0.5)
    ser.write('AT+NBSC=1\r\n'.encode('utf-8'))  #開啟擾碼
    print(receiving(ser))
    time.sleep(0.5)
    ################連線IP網路################
    #ser.write('at+cstt="nbiot"\r\n'.encode('utf-8'))       #遠傳電信
    #ser.write('at+cstt="ctnb"\r\n'.encode('utf-8'))        #中國電信
    #ser.write('at+cstt="CMNET"\r\n'.encode('utf-8'))       #中國移動
    #ser.write('at+cstt="internet"\r\n'.encode('utf-8'))    #中華電信 NB-IOT (低速)
    ser.write('at+cstt="internet.iot"\r\n'.encode('utf-8')) #連到internet網路
    print(receiving(ser))
    time.sleep(4)
    ser.write('at+CIICR\r\n'.encode('utf-8'))               #啟動IP數據網路
    print(receiving(ser))

def lte_linked():       #取得連線後帳號資訊
    ###########透過 AT+CGATT? & AT+CPSI? 指令來確認已連線基地台###########
    ser.write('AT+CPSI?\r\n'.encode('utf-8'))   #查詢 註冊訊息
    print(receiving(ser))
    time.sleep(0.5)
    ser.write('AT+CGATT?\r\n'.encode('utf-8'))  #查詢業務機能OK, 1:表示可以正常使用數據
    print(receiving(ser))
    time.sleep(0.5)
    ser.write('AT+CGNAPN\r\n'.encode('utf-8'))  #查詢系統APN
    print(receiving(ser))
    time.sleep(0.5)
    ser.write('AT+CIFSR\r\n'.encode('utf-8'))   #查詢本地IP (Get local IP)
    print(receiving(ser))

def localip():          #取得連線後獲得的IP
    ser.write('AT+CIFSR\r\n'.encode('utf-8'))   #查詢本地IP (Get local IP)
    print(receiving(ser))

def ping():
    ser.write('AT+CIPPING="168.95.1.1"\r\n'.encode('utf-8')) #Ping IP
    #ser.write('AT+CIPPING="8.8.8.8"\r\n')
    time.sleep(1)
    print(receiving(ser))

def ping50():
    ser.write('AT+CIPPING="168.95.1.1",50\r\n'.encode('utf-8')) #Ping IP
    #ser.write('AT+CIPPING="8.8.8.8"\r\n')
    time.sleep(2)
    print(receiving(ser))

def function():
    try:
        time.sleep(0.5)
        init_module()
        time.sleep(0.5)
        lte_linking()
        time.sleep(0.5)
        #############查看 IP####################
        localip()
        #############應用:ping測試##############
        ping50()
        #############應用:TCP連線測試###########
        connect_tcp()
        #############應用:連線測試##############
        send_tcp()

        status=1
        while True:
            if GPIO.input(26) == True:
                if status==1:
                    #post_http(2)
                    status=2
                    print("STATUS: Close")
                else:
                    pass
            else:
                if status==2:
                    #post_http(1)
                    status=1
                    print("STATUS: Open")
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
    code.interact(local=locals())   #remark for auto-run ('#' cancel interact mode)
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