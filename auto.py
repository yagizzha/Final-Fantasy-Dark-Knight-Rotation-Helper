from os import stat
from re import X
import numpy as np
import cv2
import pygetwindow 
from time import time
from time import sleep
import win32gui
import win32ui
import win32con
import win32api
import pyautogui
import keyboard
import tkinter
from skimage.metrics import structural_similarity as compare_ssim
from impwincap import WindowCapture
from skilltrack import SkillTrack
import threading
import signal
import sys
import random

global x,img

x=True

class StatTracker:
    def __init__(self,yfrom,yto,xfrom,xto,lower_val,upper_val,font,inp1,inp2):
        self.yfrom=yfrom
        self.yto=yto
        self.xfrom=xfrom
        self.xto=xto
        self.lower_val=lower_val
        self.upper_val=upper_val
        self.font=font
        self.inp1=inp1
        self.inp2=inp2
        self.stat=None
    def getStat(self,scr):
        cutimage=scr[self.yfrom:self.yto,self.xfrom:self.xto]
        mask = cv2.inRange(cutimage, self.lower_val, self.upper_val)
        return getAmount(mask,self.lower_val,self.upper_val,self.font,self.inp1,self.inp2)
    def getStatGauge(self,scr):
        cutimage=scr[self.yfrom:self.yto,self.xfrom:self.xto]
        mask = cv2.inRange(cutimage, self.lower_val, self.upper_val)
        return getGauge(mask,self.lower_val,self.upper_val,self.font)
    def update(self,img):
        if len(self.font)==11:
            self.stat=self.getStatGauge(img)
        else:
            self.stat=self.getStat(img)
  
class CDTracker:
    def __init__(self,yfrom,yto,xfrom,xto,inpimg,corner,lower_val=None,upper_val=None,font=None,inp1=None,inp2=None):
        self.yfrom=yfrom
        self.yto=yto
        self.xfrom=xfrom
        self.xto=xto
        self.base=inpimg
        self.corner=corner
        self.lower_val=lower_val
        self.upper_val=upper_val
        self.font=font
        self.inp1=inp1
        self.inp2=inp2
        self.usable=False
        self.combo=False
    def isUsable(self,scr):
        cutimage=scr[self.yfrom:self.yto,self.xfrom:self.xto]
        return match(cutimage,self.base)>0.99
    def isCombo(self,scr):
        cutimage=scr[self.yfrom:self.yto,self.xfrom:self.xto]
        return match(cutimage,self.corner)!=None and match(cutimage,self.corner)<0.9
    def getCooldown(self,scr):
        if self.font!=None:
            cutimage=scr[self.yfrom:self.yto,self.xfrom:self.xto]
            mask = cv2.inRange(cutimage, self.lower_val, self.upper_val)
            return getAmount(mask,self.lower_val,self.upper_val,self.font,self.inp1,self.inp2)
        return None
    def update(self,img):
        self.usable=self.isUsable(img)
        self.combo=self.isCombo(img)
             
class Range:
    def __init__(self,yfrom=898,yto=949,xfrom=703,xto=750):
        self.cross=cv2.imread("tests/"+"cross"+".png")
        self.lower_val = np.array([0,0,150])
        self.upper_val = np.array([255,255,255]) 
        self.yfrom=yfrom
        self.yto=yto
        self.xfrom=xfrom
        self.xto=xto
        self.crossmasked=cv2.inRange(self.cross, self.lower_val, self.upper_val) 
    def inRange(self,scr):
        cutimage=scr[self.yfrom:self.yto,self.xfrom:self.xto]
        mask = cv2.inRange(cutimage, self.lower_val, self.upper_val)
        return containsImage(mask,self.crossmasked)

class HPBar:
    def __init__(self,yfrom=996,yto=1000,xfrom=808,xto=952):
        self.yfrom=yfrom
        self.yto=yto
        self.xfrom=xfrom
        self.xto=xto
        self.stat=None
    def update(self,img):
        HPBARTEST=img[self.yfrom:self.yto,self.xfrom:self.xto]
        hsv = cv2.cvtColor(HPBARTEST, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (36, 25, 25), (70, 255,255))
        self.stat= np.count_nonzero(mask == 255)

def containsImage(mask,target):
    result=cv2.matchTemplate(mask,target,cv2.TM_CCOEFF_NORMED)
    min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)
    if max_val>0.7:
        return False
    return True

def match(inpimg,target):
    result=cv2.matchTemplate(inpimg,target,cv2.TM_CCOEFF_NORMED)
    min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)
    return max_val
    
def getGauge(mask,lower_val,upper_val,gaugenumarr):
    crmax=0
    maxind=None
    for i in range(11):
        result=cv2.matchTemplate(mask,gaugenumarr[i],cv2.TM_CCOEFF_NORMED)
        min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)
        if max_val>crmax:
            crmax=max_val
            maxind=i
    return maxind*10
    
def getAmount(mask,lower_val,upper_val,numarr,offset,divide):
    try:
        found=True
        curr=0
        minx=999
        minxind=0
        for i in range(10):
            result=cv2.matchTemplate(mask,numarr[i],cv2.TM_CCOEFF_NORMED)
            min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)
            if max_val>0.80:
                found=True
                if max_loc[0]<minx:
                    minx=max_loc[0]
                    minxind=i
                    if i==1:
                        minx=minx-4
        mask=mask[0:len(mask),minx:len(mask[0])]
        #cv2.imshow("masktry",mask)
        #cv2.waitKey(1)
        #sleep(1)
        while found:
            minx=999
            minxind=0
            found=False
            if len(mask[0])>divide:
                masktest=mask[0:len(mask),0:divide]
            else:
                masktest=mask[0:len(mask),0:len(mask[0])]
            #cv2.imshow("masktest",masktest)
            #sleep(0.5)
            #cv2.waitKey(1)
            for i in range(10):
                result=cv2.matchTemplate(masktest,numarr[i],cv2.TM_CCOEFF_NORMED)
                min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)
                #print(i,max_val)
                #cv2.imshow("masktest",masktest)
                #sleep(0.5)
                #cv2.waitKey(1)
                if max_val>0.80:
                    found=True
                    if max_loc[0]<minx:
                        minx=max_loc[0]
                        minxind=i
                    if max_loc[0]<17 and max_val>0.9:
                        minx=max_loc[0]
                        minxind=i
            #sleep(2)
            curr=(curr+minxind)*10
            if len(mask[0])>offset:
                if minxind==1:
                    mask=mask[0:len(mask),offset:len(mask[0])]
                else:
                    mask=mask[0:len(mask),offset:len(mask[0])]
            else:
                found=False
        return int(curr/100)
    except:
        return None

def update(arr):
    try:
        global img
        for i in range(len(arr)):
            arr[i].update(img)
    except:
        pass

lower_val = np.array([220,230,240])
upper_val = np.array([255,255,255]) 
cd_lower_val = np.array([220,220,220])
cd_upper_val = np.array([255,255,255])
red_lower_val = np.array([0,0,150])
red_upper_val = np.array([255,255,255]) 

numarr=[]
for i in range(10):
    masked=cv2.inRange(cv2.imread("numbs/"+str(i)+".png"), lower_val, upper_val)
    numarr.append(masked)
    print(i)
    
powernumarr=[]
for i in range(10):
    masked=cv2.inRange(cv2.imread("powernumbs/"+str(i)+".png"), lower_val, upper_val)
    powernumarr.append(masked)
    print(i)
    
cdnumarr=[]
for i in range(10):
    masked=cv2.inRange(cv2.imread("cdnumbs/"+str(i)+".png"), cd_lower_val, cd_upper_val)
    cdnumarr.append(masked)
    print(i)

gaugenumarr=[]
for i in range(11):
    masked=cv2.inRange(cv2.imread("gaugenumbs/"+str(i*10)+".jpg"), lower_val, upper_val)
    gaugenumarr.append(masked)
    print(i)

wwpng=cv2.imread("tests/worldwarnimg.jpg")
wincap=WindowCapture("FINAL FANTASY XIV")

img=wincap.windowcap()
hwnd=win32gui.FindWindow(None,wincap.windowname)
bar=[]
line=[]
xadd=0
yadd=0
for z in range(3):
    for i in range(12):
        x=CDTracker(901-yadd,949-yadd,703+xadd,750+xadd,cv2.imread("skills/"+str(z+1)+"x"+str(i+1)+".png"),cv2.imread("skills/"+str(z+1)+"x"+str(i+1)+"c"+".png"),cd_lower_val,cd_upper_val,cdnumarr,8,14)
        #line.append(img[901-yadd:947-yadd,709+xadd:750+xadd])
        line.append(x)
        xadd+=45
    xadd=0
    bar.append(line)
    line=[]
    yadd+=49
rangecheck=Range()
rangecheck15=Range(926,949,1067,1081)
path="skills/"
#"CD:",getAmount(maskcd,lower_val,upper_val,cdnumarr,8,14),


BStatus = tkinter.Label(text='Casts: Inactive', font=('Times','15'), fg='red', bg='black')
BStatus.master.overrideredirect(True)
BStatus.master.geometry("+1450+450")
BStatus.master.lift()
BStatus.master.wm_attributes("-topmost", True)
BStatus.master.wm_attributes("-disabled", True)
BStatus.pack()

#HPTr=StatTracker(998,1020,820,959,lower_val,upper_val,numarr,16,27)
HPTr=HPBar()
SPTr=StatTracker(998,1020,960,1150,lower_val,upper_val,numarr,16,27)
GaugeTr=StatTracker(765,829,432,506,lower_val,upper_val,gaugenumarr,16,27)
PowerTr=StatTracker(850,950,496,596,lower_val,upper_val,powernumarr,16,27)

statarr=[]
statarr.append(HPTr)
statarr.append(SPTr)
statarr.append(GaugeTr)
statarr.append(PowerTr)

lastthread1=time()
lastthread2=time()
lastthread3=time()
lastthread4=time()

t1 = threading.Thread(target=update,args=(bar[0],))
t1.start()
t2 = threading.Thread(target=update,args=(bar[1],))
t2.start()
t3 = threading.Thread(target=update,args=(bar[2],))
t3.start()
t4 = threading.Thread(target=update,args=(statarr,))
t4.start()

continuable=False
timer=time()
timerx=0
mode=0  #0 stop 1 ST 2 AOE 
burst=False
maxHP=None
lastmove=True
afktimer=time()
afkmax=random.randrange(150)
#statarr  HP SP Gauge Power
lastmode=mode
lastmodetime=time()
while True:
    try:
        timer=time()
        img=wincap.windowcap()
        if (not t1.is_alive() ) and time()-lastthread1>=0.1:
            t1.join()
            t1 = threading.Thread(target=update,args=(bar[0],))
            t1.start()
            lastthread1=time()
        if (not t2.is_alive() ) and time()-lastthread2>=0.1:
            t2.join()
            t2 = threading.Thread(target=update,args=(bar[1],))
            t2.start()
            lastthread2=time()
        if (not t3.is_alive() ) and time()-lastthread3>=0.1:
            t3.join()
            t3 = threading.Thread(target=update,args=(bar[2],))
            t3.start()
            lastthread3=time()
        if (not t4.is_alive() ) and time()-lastthread4>=0.1:
            t4.join()
            t4 = threading.Thread(target=update,args=(statarr,))
            t4.start()
            lastthread4=time()

        #print("HP:",statarr[0].stat,"SP:",statarr[1].stat,"Gauge:",statarr[2].stat,"Power:",statarr[3].stat,end=" ")

        cv2.waitKey(1)
        if keyboard.is_pressed('ü') and not keyboard.is_pressed('shift') and not keyboard.is_pressed('ctrl'):
            print("SINGLE TARGET")
            if burst:
                BStatus['text']='Single Target:Burst'
            else:
                BStatus['text']='Single Target'
            BStatus['fg']='green'
            mode=1
        if keyboard.is_pressed(','):
            print("S T O P")
            BStatus['text']='Inactive'
            BStatus['fg']='red'
            mode=0
            burst=False
        if keyboard.is_pressed('shift+ü') and not keyboard.is_pressed('ctrl'):
            print("AOE")
            if burst:
                BStatus['text']='AoE Mode:Burst'
            else:
                BStatus['text']='AoE Mode'
            BStatus['fg']='green'
            mode=2
        if keyboard.is_pressed('ctrl+ü') and not keyboard.is_pressed('shift'):
            print("ANTIAFK")
            BStatus['text']='ANTI AFK'
            BStatus['fg']='yellow'
            afktimer=-180
            mode=5
            burst=False
        if keyboard.is_pressed('0') and not keyboard.is_pressed('shift') and not keyboard.is_pressed('ctrl'):
            print("SINGLE TARGET")
            if burst:
                BStatus['text']='Cleave Mode:Burst'
            else:
                BStatus['text']='Cleave Mode'
            BStatus['fg']='green'
            mode=3
        if keyboard.is_pressed('9'):
            print("BURST UNLOCK")
            if "Burst" not in BStatus['text']:
                BStatus['text']=BStatus['text']+":Burst"
                BStatus['fg']='green' 
            burst=True
        if maxHP==None or keyboard.is_pressed('ctrl+shift+ü'):
            maxHP=statarr[0].stat
            print("SETTING MAX HP TO",maxHP)
        if lastmode!=mode:
            lastmode=mode
            lastmodetime=time()
        if time()-lastmodetime>180:
            if mode==lastmode and mode==5:
                continue
            else:
                print("ANTIAFK")
                BStatus['text']='ANTI AFK'
                BStatus['fg']='yellow'
                mode=5
                afktimer=-180
                burst=False

        BStatus.update_idletasks()
        BStatus.update()
            
        if mode!=0 and mode!=5:
            #ST Normal:
            sleep(0.06)
            if mode==1:
                if rangecheck.inRange(img):
                    if burst and bar[2][1].usable and statarr[1].stat!=None and statarr[1].stat<9600:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x10, 0)
                        sleep(0.01)
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x32, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x32, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x10, 0)
                    if burst and bar[2][4].usable and statarr[2].stat<50:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x10, 0)
                        sleep(0.01)
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x35, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x35, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x10, 0)

                    if bar[0][0].usable:
                        if bar[0][1].combo:
                            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x32, 0)
                            win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x32, 0)
                        elif bar[0][2].combo:
                            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x33, 0)
                            win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x33, 0)
                        elif bar[0][3].usable:
                            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x34, 0)
                            win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x34, 0)
                        else:
                            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x31, 0)
                            win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x31, 0)
                    if bar[1][0].usable:
                        if bar[1][0].combo or (statarr[3].stat==None or statarr[3].stat<29 or burst) and (statarr[1].stat !=None and statarr[1].stat>6000):
                            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x46, 0)
                            win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x46, 0)
                    if bar[2][5].usable:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x10, 0)
                        sleep(0.01)
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x51, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x51, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x10, 0)
                elif rangecheck15.inRange(img):
                    if bar[0][8].usable:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x51, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x51, 0)
                    elif bar[0][4].usable:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x35, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x35, 0)
            if mode==2:
                if rangecheck.inRange(img):
                    if burst and bar[2][1].usable and statarr[1].stat<9600:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x10, 0)
                        sleep(0.01)
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x32, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x32, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x10, 0)
                    if burst and bar[2][4].usable and statarr[2].stat<50:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x10, 0)
                        sleep(0.01)
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x35, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x35, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x10, 0)
                    if bar[2][0].usable:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x10, 0)
                        sleep(0.02)
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x31, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x31, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x10, 0)
                    if bar[0][7].usable:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x52, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x52, 0)
                    if bar[2][6].usable:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x10, 0)
                        sleep(0.02)
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x45, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x45, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x10, 0)
                    if bar[1][1].usable:
                        if bar[1][1].combo or (statarr[3].stat==None or statarr[3].stat<29 or burst) and (statarr[1].stat !=None and statarr[1].stat>6000) :
                            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x47, 0)
                            win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x47, 0)
            if mode==3:
                if rangecheck.inRange(img):
                    if burst and bar[2][0].usable:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x10, 0)
                        sleep(0.02)
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x31, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x31, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x10, 0)
                    if burst and bar[2][1].usable and statarr[1].stat!=None and statarr[1].stat<9600:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x10, 0)
                        sleep(0.01)
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x32, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x32, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x10, 0)
                    if burst and bar[2][4].usable and statarr[2].stat<50:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x10, 0)
                        sleep(0.01)
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x35, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x35, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x10, 0)
                    if burst and bar[2][2].usable:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x10, 0)
                        sleep(0.02)
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x33, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x33, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x10, 0)
                    if bar[2][6].usable:
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x10, 0)
                        sleep(0.02)
                        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x45, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x45, 0)
                        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x10, 0)
                    if bar[1][0].usable:
                        if bar[1][0].combo or (statarr[3].stat==None or statarr[3].stat<29 or burst) and (statarr[1].stat !=None and statarr[1].stat>6000):
                            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x47, 0)
                            win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x47, 0)
                    if bar[0][0].usable:
                        if bar[0][1].combo:
                            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x32, 0)
                            win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x32, 0)
                        elif bar[0][2].combo:
                            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x33, 0)
                            win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x33, 0)
                        else:
                            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x31, 0)
                            win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x31, 0)
            if maxHP==0:
                maxHP=1
            HPpercentage=statarr[0].stat/maxHP
            if HPpercentage<=0.9:
                if bar[0][6].usable:
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x45, 0)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x45, 0)
            if HPpercentage<=0.75:
                if bar[1][7].usable:
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x11, 0)
                    sleep(0.02)
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x33, 0)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x33, 0)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x11, 0)
            if HPpercentage<=0.60:
                if bar[1][2].usable:
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x5A, 0)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x5A, 0)
            if HPpercentage<=0.50:
                if bar[1][5].usable:
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x11, 0)
                    sleep(0.02)
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x31, 0)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x31, 0)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x11, 0)
            if HPpercentage<=0.30:
                if bar[1][6].usable:
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x11, 0)
                    sleep(0.02)
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x32, 0)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x32, 0)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x11, 0)
                if bar[2][2].usable:
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x11, 0)
                    sleep(0.02)
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x33, 0)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x33, 0)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x11, 0)
            if HPpercentage<=0.15:
                if bar[1][9].usable:
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x11, 0)
                    sleep(0.02)
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x35, 0)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x35, 0)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x11, 0)
            
        if mode==5:
            #ST Normal:
            if (time()-afktimer)>afkmax:
                print("we in ")
                if lastmove:
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x57, 0)
                    sleep(1)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x57, 0)
                    lastmove=not lastmove
                    afkmax=random.randrange(60)
                    afktimer=time()
                else:
                    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x53, 0)
                    sleep(1)
                    win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x53, 0)
                    lastmove=not lastmove
                    afkmax=random.randrange(60)
                    print(afkmax)
                    afktimer=time()
            print(match(img[127:173,1846:1896],wwpng))#699 442   1203 606
            """
            if match(img[127:173,1846:1896],wwpng)<0.55:
                BStatus['text']='WARNING'
                BStatus['fg']='red'
                continue"""

                

                

                    


                
            



            
    except KeyboardInterrupt:
        x=False
        print ("Bye")
        sys.exit()
    timerx=time()-timer





























    """
        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x10, 0)
        sleep(0.1)
        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x31, 0)
        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x31, 0)
        win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x10, 0)
        sleep(2)"""
       




































    









