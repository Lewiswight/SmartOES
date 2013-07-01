import os
import time

data = os.system("python dpdsrv.py")
with open("./log.txt", "a") as myfile:
    myfile.write(data)
