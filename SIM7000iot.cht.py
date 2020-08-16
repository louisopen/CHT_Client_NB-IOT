#!/usr/bin/env python
#coding=utf-8

#Setup Raspberry pi system 
#sudo raspi-config      #Interfacing Options -> Serial login -> no, Serial hardware -> yes
#sudo nano /boot/config.txt     #add==> enable_uart=1
#sudo nano /boot/cmdline.txt    #deleted console=ttyAMA0,115200 kgdboc=ttyAMA0,115200
#sudo apt-get install minicom   #Try application
#minicom -D /dev/ttyS0 -b115200     #Raspberry pi3
#minicom -D /dev/ttyAMA0 -b115200     #Raspberry pi2 

#cd /SIM7000C/bcm2835
#chmod +x configure && ./configure && sudo make && sudo make install    #遮個才成功

import  RPi.GPIO as GPIO
import time
import serial
#import threading
import code 

ser=''

def gpio_init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(23,GPIO.OUT)
    
#echo 'AT+SAPBR=2,1\r\n' > /dev/ttyAMA0     #Under bash
def receiving(ser):             #寫法簡單, 但有坑! 先頂著!
    #ser.flushInput()           #清除接收緩衝區
    last_received=''
    time.sleep(0.1)       
    count = ser.inWaiting()     #取得當下緩衝區字元數
    while count != 0:
        last_received += ser.read(count) 
        time.sleep(0.125)       #
        count = ser.inWaiting() #取得當下緩衝區字元數
    last_received += ser.read(count) 
    return last_received

def lte_test():
    ser.write('AT\r\n')         #同步測試
    print(receiving(ser))
    time.sleep(0.5)  
    ser.write('AT+CPIN?\r\n')   #SIM-car ?
    print(receiving(ser))
    time.sleep(0.5)
    ser.write('AT+CSQ\r\n')     #查询信号强度 #查詢訊號品質Rssi,Ber
    print(receiving(ser))
    time.sleep(0.5)
    ###########透過 AT+CGATT? & AT+CPSI? 指令來確認已連線基地台###########
    ser.write('AT+CPSI?\r\n')   #查詢 註冊訊息
    print(receiving(ser))
    time.sleep(0.5)
    ser.write('AT+CGATT?\r\n')  #查询业务是否附着，确保卡不欠费
    print(receiving(ser))

def init_comm():
    global ser
    gpio_init()
    ser = serial.Serial("/dev/ttyAMA0",115200)  #Pi2
    #ser = serial.Serial("/dev/ttyS0",115200)  #Pi3 
    if ser=='':
        print("ser:null")
        exit(0)
    #st1 = threading.Thread(target=receiving, args=(ser,))
    #st1.start()
    ser.write('AT+CIFSR\r\n')               #查詢本地IP (Get local IP)
    print(receiving(ser))

def lte_setup():
    ser.write('AT+CNMP=38\r\n') #LTE only
    print(receiving(ser))
    time.sleep(0.5)
    ser.write('AT+CMNB=1\r\n')  #LTE(1:Cat-M1 and 3:NB-IOT)
    print(receiving(ser))
    time.sleep(0.5)
    ser.write('AT+NBSC=1\r\n')  #開啟擾碼
    print(receiving(ser))
    time.sleep(0.5)
    ################連線IP網路#################
    ser.write('at+cstt="internet.iot"\r\n') #連到internet網路
    print(receiving(ser))
    time.sleep(4)
    ser.write('at+CIICR\r\n')               #啟動IP數據網路
    print(receiving(ser))

def localip():
    ser.write('AT+CIFSR\r\n')               #查詢本地IP (Get local IP)
    print(receiving(ser))

def ping50():
    ser.write('AT+CIPPING="168.95.1.1",50\r\n') 
    #ser.write('AT+CIPPING="8.8.8.8"\r\n')
    print(receiving(ser))

def function():
    try:    
        lte_test()
        time.sleep(0.5)
        lte_setup()
        time.sleep(0.5)
        '''
        ser.write('AT+CGNAPN\r\n')  #查詢APN
        print(receiving(ser))
        time.sleep(1)

        ser.write('AT+COPS?\r\n')  #查詢掃描基地台(index,format,oper),(9 is NB-IOT,7 is CAT-M1)
        print(receiving(ser))
        time.sleep(1)
        '''
        #ser.write('AT+SAPBR=3,1,"APN","CMNET"\r\n')  #中国移動
        #ser.write('AT+SAPBR=3,1,"APN","internet"\r\n')  #中華電信 NB-IOT (低速)
        #ser.write('AT+SAPBR=3,1,"APN","internet.iot"\r\n')  #中華電信 Cat-M1  

        ser.write('AT+CGDCONT=1,"IP","internet.iot"\r\n')   #設定電信公司APN
        #ser.write('AT+CGDCONT=1,"IP",""\r\n')              #自動(由基地台決定)
        print(receiving(ser))
        time.sleep(4)

        ser.write('at+cops=1,2,”46692”\r\n')   #連上基地台(中華電信), 第一次會花很長時間
        print(receiving(ser))
        time.sleep(1)

        ################啟用移動場景###############
        #ser.write('AT+CIMI\r\n') 
        #print(receiving(ser))
        #time.sleep(1)
        ###############查看一下IP##################
        #ser.write('AT+SAPBR=2,1\r\n')          #To query the IP
        ser.write('AT+CIFSR\r\n')               #查詢IP (Get local IP)
        print(receiving(ser))
        time.sleep(1)


        ##############應用1. ping測試##############
        ser.write('AT+CIPPING="168.95.1.1"\r\n') 
        #ser.write('AT+CIPPING="8.8.8.8"\r\n')
        print(receiving(ser))
        time.sleep(1)
        #############應用2. TCP連線測試############
        ser.write('at+cipstart=”tcp”,”ftp.isu.edu.tw”,21\r\n') 
        #ser.write('AT+CIPSTART="TCP","123.123.123.123",9487\r\n')
        print(receiving(ser))
        time.sleep(1)
        #############應用3. 連線測試############
        ser.write('AT+CIPSEND=I love you\r\n') 
        print(receiving(ser))
        time.sleep(1)

        status=1
        while True:
            if GPIO.input(23) == True:
                if status==1:
                    status=2
                    print("STATUS: Close")
                else:
                    pass
            else:
                if status==2:
                    status=1
                    print("STATUS: Open")
                else:
                    pass
            time.sleep(3)

    except KeyboardInterrupt: 
        ser.write('AT+CIPSHUT\r\n')   #Shur Down module
        print(receiving(ser))
        time.sleep(0.2) 

        if ser != None:  
            ser.close()
    except:
        pass
    finally:
        #st1.join()
        GPIO.cleanup() 

if __name__ == '__main__':
    #init_comm()
    #function()
    code.interact(local=locals())