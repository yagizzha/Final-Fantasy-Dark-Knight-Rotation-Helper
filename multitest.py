# Python program to illustrate the concept
# of threading
# importing the threading module
from re import X
import threading
from time import time
from time import sleep
import signal
import sys
global x
global a
x=True
a=1
def print_cube(arr):    
    """
	function to print cube of given num
	"""
    global a
    while x:
        for i in range(len(arr)):
            arr[i]=arr[i]+1
        a+=1
        timer=time()
        sleep(0.1)
        print("T1:",time()-timer,"A:",arr)

def print_square(arr):
    """
    function to print square of given num
    """
    global a
    while x:
        for i in range(len(arr)):
            arr[i]=arr[i]+1
        a+=1
        timer=time()
        sleep(0.1)
        print("T2:",time()-timer,"A:",arr)
def T3():
    print("In,testing")

if __name__ == "__main__":
    # creating thread
    arr1=[0,1,2,3,4]
    arr2=[5,6,7,8,9]
    #t1 = threading.Thread(target=print_square, args=(arr1,))
    #t2 = threading.Thread(target=print_cube, args=(arr2,))
    t3 = threading.Thread(target=T3)

    # starting thread 1
    #t1.start()
    sleep(1)
    # starting thread 2
    #t2.start()
    while True:
        try:
            y=1
            t3 = threading.Thread(target=T3)
            t3.start()
            sleep()
            print("MAIN1:",arr1)
            print("MAIN2:",arr2)
            t3.join()
        except KeyboardInterrupt:
            x=False
            print ("Bye")
            sys.exit()
    # wait until thread 1 is completely executed
    t1.join()
    # wait until thread 2 is completely executed
    t2.join()
    t3.join()

    # both threads completely executed
    print("Done!")
