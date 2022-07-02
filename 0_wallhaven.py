from asyncio import futures
import os
import requests
import time
import math
picurl = "https://w.wallhaven.cc/full/{0}/wallhaven-{1}.jpg"

count = 0
total =188437  ##len(open("E:\wallhaven_sfw\wallhaven_sfw.txt", 'r').readlines())
f = open('E:\\wallhaven_sfw\\wallhaven_sfw.txt', "r", encoding='utf-8')

RETRYTIME = 0


def downloadpic(fname, furl):
    global RETRYTIME
    try:
        RETRYTIME=0
        res = requests.get(furl)
        with open(fname, 'wb')as f:
            f.write(res.content)
        if(os.path.getsize(fname) < 1000):
            os.remove(fname)
            furl = furl.replace(".jpg", ".png")
            fname = fname.replace(".jpg", ".png")        
            res = requests.get(furl)
            with open(fname, 'wb') as pf:
                pf.write(res.content)
        return furl
    except:
        if(RETRYTIME==10):
            RETRYTIME=0
            return "no"
        RETRYTIME+=1
        time.sleep(20)
        downloadpic(fname,furl)
        return furl+"下载失败"

for line in f:
    count=count+1
    imgurl=line.strip().split("_")[0]
    favcount = line.strip().split("_")[1]
    pid = imgurl.strip().split("/")[4]
    url = picurl.format(pid[:2],pid)
    fname=os.path.basename(url)
    if(int(favcount)>100):
        max=math.ceil(int(favcount)/100)*100
        min=max-100
    else:
        max = math.ceil(int(favcount)/10)*10
        min=max-10
    subdic = "E:\\wallhaven_sfw\\"+"{}-{}".format(min, max)
    if(not os.path.exists(subdic)):
        os.mkdir(subdic)
    fullname = subdic+"\\"+fname
    if(os.path.exists(fullname)):
        print("【{}/{}】{}已下载".format(count, total, url))
        continue
    if(os.path.exists(fullname.replace(".jpg", ".png"))):
        print("【{}/{}】{}已下载".format(count, total, url.replace(".jpg", ".png")))
        continue
    ##download
    msg = downloadpic(fullname, url)
    print("【{}/{}】{}_{}".format(count, total, msg, favcount))
    ##time.sleep(0.5)  
