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

def gpio_init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(23,GPIO.OUT)
    
#echo 'AT+SAPBR=2,1\r\n' > /dev/ttyAMA0
#cat /dev/ttyAMA0

def receiving(ser):
    ser.flushInput()    #清除接收緩衝區
    last_received=''
    while True:
        time.sleep(0.05) #時間太短, 字元來不及傳回, 斷字
        count = ser.inWaiting() #取得當下緩衝區字元數
        if count != 0:
            last_received = ser.read(count) 
            #print(last_received)
            break
    return last_received



if __name__ == '__main__':
    gpio_init()
    ser = serial.Serial("/dev/ttyAMA0",115200)  #Pi2
    #ser = serial.Serial("/dev/ttyS0",115200)  #Pi3 
    #st1 = threading.Thread(target=receiving, args=(ser,))
    #st1.start()
    try:
        ser.write('AT+CPIN?\r\n') #SIM-car ?
        print(receiving(ser))
        time.sleep(0.5)
        #ser.write('AT+CNMP=38\r\n') #LTE only
        #print(receiving(ser))
        #time.sleep(0.5)
        #ser.write('AT+CMNB=3\r\n') #LTE(Cat-M1 and NB-IOT)
        #print(receiving(ser))
        #time.sleep(0.5)
        #ser.write('AT+NBSC=1\r\n') #開啟擾碼
        #print(receiving(ser))
        #time.sleep(0.5)
        ser.write('AT+CPSI?\r\n') #查詢註冊訊息
        print(receiving(ser))
        time.sleep(1)
        ser.write('AT+COPS?\r\n') #查詢
        print(receiving(ser))
        time.sleep(1)
        ser.write('AT+CGNAPN\r\n') #查詢
        print(receiving(ser))
        time.sleep(1)
        #ser.write('at+cops=1,2,”46692”\r\n')
        #print(receiving(ser))
        #time.sleep(1)

        #ser.write('AT+SAPBR=3,1,"APN","CMNET"\r\n')  #中国移動 Configure bearer profile 1 
        ser.write('AT+SAPBR=3,1,"APN","internet.iot"\r\n')  #中華電信 Configure bearer profile 1  
        #ser.write('AT+CGDCONT=1,"IP","internet.iot"\r\n')
        #ser.write('at+cstt="internet"\r\n')
        print(receiving(ser))
        time.sleep(4)

        #ser.write('AT+CIICR\r\n') 
        #print(receiving(ser))
        #time.sleep(1)

        ser.write('AT+SAPBR=2,1\r\n')  #To query the IP
        #ser.write('AT+CIFSR\r\n') #Get local IP
        print(receiving(ser))
        time.sleep(1)

        #ser.write('AT+CIPPING="168.95.1.1"\r\n') 
        #print(receiving(ser))
        #time.sleep(1)

        #ser.write('at+cipstart=”tcp”,”ftp.isu.edu.tw”,21\r\n') 
        #print(receiving(ser))
        #time.sleep(1)
        
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
        if ser != None:  
            ser.close()
    except:
        pass
    finally:
        #st1.join()
        GPIO.cleanup() 