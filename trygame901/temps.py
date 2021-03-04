#!/usr/bin/env python

# This script polls the yokogawa GX temperature recorders via telnet on port 34434 for temperatures on channels 1-20 and saves to a text file.

import sys
import telnetlib
import time

HOST = ["181","182","183","184","185","186","187","188","189","190","191","192","193","194","195","196","197","198"]
# HOST1 = ["181","182","183","184","185","186","188","189","190","191","192","193","194","195","196","197","198","182","183","184","185","186","188","189","190","191","192","193","194","195","196","197","198","182","183","184","185","186","188","189","190","191","192","193","194","195","196","197","198","182","183","184","185","186","188","189","190","191","192","193","194","195","196","197","198"]

port = "34434"
user = "CLogin,Admin,<password>"
request = "FData,0,0001,0020"

def main():
    results=[]
    print("Creating file")
    with open("outputall.txt", "w") as op:
        for item in HOST:
            try:
                print("Connecting to 10.110.40."+item)
                tn = telnetlib.Telnet('10.110.40.'+item, port)
                op.write("10.110.40."+item+"\n")
                tn.set_debuglevel(0) # debugging
                print("Logging in")
                tn.read_until(b"E1,401:1:0\r\n").decode('utf-8')
                tn.write(user.encode('utf-8') + b"\n")
                print("Waiting for ready signal")
                tn.read_until(b"E0\r\n").decode('utf-8')
                tn.write(request.encode('utf-8') + b"\n")
                print("Requesting data")
                lastpost = tn.read_very_eager().decode('utf-8')
                op.write(lastpost)
                results.append(lastpost)
                print("Writing data to file")
                tn.close()
                HOST1.append(HOST1**2)
            except TimeoutError :
                print(" ** Timeout on 10.110.40."+item)
                op.write("10.110.40."+item+" timeout\n")
        print("Closing connection, saving file")
    len(set(results))
    #print(results)
    time.sleep(2)
main()