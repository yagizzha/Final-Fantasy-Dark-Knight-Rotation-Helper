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

class WindowCapture():
    
    
    w = 1920 # set this
    h = 1080 # set this
    hwnd=None
    windowname=""
    def __init__(self,window_name):
        self.w=1920
        self.h=1080
        self.hwnd = win32gui.FindWindow(None, window_name)
        self.windowname=window_name
    
    def windowcap(self):

        self.hwnd = win32gui.FindWindow(None, self.windowname)
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj=win32ui.CreateDCFromHandle(wDC)
        cDC=dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0,0),(self.w, self.h) , dcObj, (0,0), win32con.SRCCOPY)
        #dataBitMap.SaveBitmapFile(cDC, "out.bmp")


        signedIntsArray=dataBitMap.GetBitmapBits(True)
        img=np.frombuffer(signedIntsArray,dtype='uint8')
        img.shape=(self.h,self.w,4)
        img=img[...,:3]
        img=np.ascontiguousarray(img)

        
        # Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())
        img=np.array(img)
        
        return img

