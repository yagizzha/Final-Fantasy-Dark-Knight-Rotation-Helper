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
from impwincap import WindowCapture
from skilltrack import SkillTrack
xadd=0
yadd=0

wincap=WindowCapture("FINAL FANTASY XIV")

img=wincap.windowcap()
cv2.imwrite("skills/scr.png",img)
for z in range(3):
    for i in range(12):
        a=img[908-yadd:933-yadd,718+xadd:742+xadd]
        xadd+=45
        cv2.imwrite("skills/"+str(z+1)+"x"+str(i+1)+".png",a)
        cv2.waitKey(1)
    xadd=0
    yadd+=49
xadd=0
yadd=0

wincap=WindowCapture("FINAL FANTASY XIV")

img=wincap.windowcap()
for z in range(3):
    for i in range(12):
        a=img[909-yadd:939-yadd,710+xadd:713+xadd]
        xadd+=45
        cv2.imwrite("skills/"+str(z+1)+"x"+str(i+1)+"c"+".png",a)
        cv2.waitKey(1)
    xadd=0
    yadd+=49
