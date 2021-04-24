### CHT_Client_NB-IOT 

> Python client application SIM7000C of NB-IOT module on Raspberry Pi, SIM7000C終端應用運行在樹莓派上, SIM7000C NB-IoT/LTE/GPRS 擴展板模組, CHT SIM card(大卡) 採用中華電信CAT. M1(門市申請即可)

#### 1. Close power-saving of the display on Raspberry Pi
#### 先關閉視窗下螢幕休眠功能(當然也可以不用關閉)

sudo nano /etc/lightdm/lightdm.conf 
* [SeatDefaults]
* ...
* #xserver-command=X	    #Change to as below
* xserver-command=X -s 0 –dpms
* ...

#### 2. Auto run application after log-in termainal in the X-Windows mode.
#### 視窗模式下自動開啟一個終端機模式(用戶登入或自動登入), 並運行應用程序

sudo nano /home/pi/.config/autostart/autoboot.desktop 
* ...
* [Desktop Entry]
* Type=Application
* Name=MyApplicationRun
* #Exec = lxterminal -e /home/pi/autorun.sh               #運行掛機 applivcation close aftern run 5day 
* Exec = lxterminal -e "bash -c /home/pi/autorun.sh;bash" #運行測試(Stay Bash)
* Icon=pictur.png
* ...
or

* [Desktop Entry]
* Encoding=UTF-8
* Type=Application
* Name=myprogram
* Exec=lxterminal -e bash -c '/home/pi/autorun.sh;$SHELL' #bash run autorun.sh
* Terminal=true
* ...

* sudo nano /home/pi/autorun.sh
* ...
* python3 SIM7000_CHT.py
* ...

#### 3. Coding & Testing SIM7000_CHT.py
#### 試試
