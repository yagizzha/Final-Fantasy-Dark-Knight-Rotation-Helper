import numpy as np
import cv2
import win32gui
import win32ui
import win32con
import win32api
import windowcapture as wincap
import time 



loop_time=time.time()
wincp=wincap.WindowCapture("Ascension")

hwnd=win32gui.FindWindow(None,wincp.windowname)

win=win32ui.CreateWindowFromHandle(hwnd)

goalimg=cv2.imread("dot.jpg")
n0=cv2.imread("numbs/0.jpg")
x=cv2.Canny(goalimg,50,50)
cv2.imshow("x",goalimg)
numarr=[]
for i in range(10):
    numarr.append(cv2.imread("numbs/"+str(i)+".jpg"))
    

counter=0
ct=9
while True:
    #print('FPS ',1/(time.time()-loop_time)," counter:",counter)
    counter+=1
    scr=wincp.windowcap()
    scr=np.array(scr)
    scr_blurred = cv2.blur(scr, (5, 5))
    scrcrnt=scr[555:608,718:771]
    result=cv2.matchTemplate(scrcrnt,goalimg,cv2.TM_CCOEFF_NORMED)
    
    min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result)

    print('Best matched :',str(max_loc),'Confidence   :',max_val)
    #print(len(goalimg),len(goalimg[0])) #first Y then X 
    #print('Confidence   :',max_val)
    #print(type(max_val))
    img=scr
    if max_val>=0.8:
        cv2.circle(img,(718+max_loc[0],555+max_loc[1]),1,(0,0,255),1,10)
        left=scr[555+12:608-12,718+10:(718+max_loc[0])]
        cv2.imshow("left",left)
        if(time.time()-loop_time>=1):
            cv2.imwrite(('numbs/'+(str)(ct)+'.jpg'),left)
            loop_time=time.time()
            ct=ct-1
        """
        for i in range(10):
            result2=cv2.matchTemplate(left,numarr[i],cv2.TM_CCOEFF_NORMED)
            min_val,max_val,min_loc,max_loc=cv2.minMaxLoc(result2)
            if max_val>=0.8:
                print("WE IN",i)
                cv2.circle(img,(718+max_loc[0],555+max_loc[1]),10,(0,0,255),10,10)
    """
    cv2.imshow("frame",scr)
    cv2.waitKey(1)
