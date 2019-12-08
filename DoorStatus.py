#!/usr/bin/env python
#coding=utf-8
#尚未測試完成: 利用http協議直接傳送狀態回服務器, 在NB-IOT module
import  RPi.GPIO as GPIO
import time
import serial   
def gpio_init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(23,GPIO.OUT)
def send_data(param):
    W_http_6='AT+HTTPPARA="URL","https://iot.cht.com.tw/iot/v1/device/'+param+'/snapshot"\r\n'
    ser.write(W_http_6)
    time.sleep(2)
    W_http_7='AT+HTTPACTION=0\r\n'
    ser.write(W_http_7)
    time.sleep(3)


if __name__ == '__main__':
    #ser = serial.Serial("/dev/ttyS0",115200)
    ser = serial.Serial("/dev/ttyAMA0",115200)  #Pi2
    W_http_1='AT+HTTPTERM\r\n'
    ser.write(W_http_1)
    time.sleep(3)
    W_http_2='AT+SAPBR=3,1,"CONTYPE","GPRS"\r\n'
    ser.write(W_http_2)
    time.sleep(3)
    W_http_3='AT+SAPBR=3,1,"APN","internet"\r\n'
    ser.write(W_http_3)
    time.sleep(3)
    W_http_4='AT+SAPBR=1,1\r\n'
    ser.write(W_http_4)
    time.sleep(3)
    W_http_5='AT+HTTPINIT\r\n'
    ser.write(W_http_5)
    time.sleep(3)
    gpio_init()
    status=1
    while True:
        if GPIO.input(23) == True:
            if status==1:
                send_data(2)
                status=2
                print "Status: close"
            else:
                pass
        else:
            if status==2:
                send_data(1)
                status=1
                print "Status: open"
            else:
                pass
        time.sleep(3)
    GPIO.cleanup()