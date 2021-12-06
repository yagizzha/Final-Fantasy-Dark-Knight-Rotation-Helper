import numpy as np
import cv2
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


class SkillTrack():
    name=""
    base=[]
    Xfrom=0
    Xto=0
    Yfrom=0
    Yto=0
    dot=[]
    def __init__(self,namestr,xf,xt,yf,yt,baseimg,dt):
        self.name=namestr
        self.Xfrom=xf
        self.Xto=xt
        self.Yfrom=yf
        self.Yto=yt
        self.base=baseimg
        self.dot=dt
    def cut(self,screen):
        scrcrnt=screen[self.Yfrom:self.Yto,self.Xfrom:self.Xto]
        return scrcrnt
        
        

    def cdLeft(self,screen,searchlist):
        scrcrnt=screen[self.Yfrom:self.Yto,self.Xfrom:self.Xto]
        result=cv2.matchTemplate(scrcrnt,self.base,cv2.TM_CCOEFF_NORMED)
    
        min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)

        if max_val>=0.90:
            return 0
        result=cv2.matchTemplate(scrcrnt,self.dot,cv2.TM_CCOEFF_NORMED)
    
        min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)
        if max_val>0.82:
            left=-1
            right=-1
            scrcrnt=screen[self.Yfrom:self.Yto,self.Xfrom:self.Xfrom+max_loc[0]]
            length=10
            for i in range(10):
                result2=cv2.matchTemplate(scrcrnt,searchlist[i],cv2.TM_CCOEFF_NORMED)
                min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result2)
                #print("i",i)
                if max_val>0.65:
                    left=i
                    break
            scrcrnt=screen[self.Yfrom:self.Yto,self.Xfrom+max_loc[0]:self.Xto]
            for j in range(10):
                result3=cv2.matchTemplate(scrcrnt,searchlist[j],cv2.TM_CCOEFF_NORMED)
                min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result3)
                #print("j",j)
                if max_val>0.65:
                    right=j
                    break
            if left>=10:
                left=9
            for x in range(left+1,10):
                result4=cv2.matchTemplate(scrcrnt,searchlist[x],cv2.TM_CCOEFF_NORMED)
                min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result4)
                if max_val>0.65:
                    right=x
                    break
            #print("LEFT",left,"RIGHT",right)
            return left+(right/10)
            
        else:
            for i in range(len(searchlist)-1,-1,-1):
                result2=cv2.matchTemplate(scrcrnt,searchlist[i],cv2.TM_CCOEFF_NORMED)
                min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result2)
                if max_val>0.65:

                    if max_loc[0]<=(self.Xto-self.Xfrom)*0.33 or max_loc[0]>=(self.Xto-self.Xfrom)*0.40:
                        #print("MAXLOC ",max_loc[0],"CALC ",(self.Xto-self.Xfrom)*0.33)
                        return self.cdLeft30(screen,searchlist)
                    #print("OUT")
                    return i
    def cdLeft30(self,screen,searchlist):
        
        lft=0
        right=0
        left=screen[self.Yfrom:self.Yto,self.Xfrom:5+(self.Xfrom+self.Xto)//2]
        length=10
        for i in range(length):
            result2=cv2.matchTemplate(left,searchlist[i],cv2.TM_CCOEFF_NORMED)
            min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result2)
            if max_val>0.65:
                lft=i
                break
        scrcrnt=screen[self.Yfrom:self.Yto,((self.Xfrom+self.Xto)//2)-5:self.Xto]
        for j in range(length):
            result3=cv2.matchTemplate(scrcrnt,searchlist[j],cv2.TM_CCOEFF_NORMED)
            min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result3)
            if max_val>0.65:
                right=j
                break
        
        for x in range(lft+1,length):
            result4=cv2.matchTemplate(scrcrnt,searchlist[x],cv2.TM_CCOEFF_NORMED)
            min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result4)
            if max_val>0.65:
                right=x
                break
        return (lft*10)+right
    def match(self,screen):
        scrcrnt=screen[self.Yfrom:self.Yto,self.Xfrom:self.Xto]
        result=cv2.matchTemplate(scrcrnt,self.base,cv2.TM_CCOEFF_NORMED)
    
        min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)

        if max_val>=0.90:
            return True
        return False
        
        
