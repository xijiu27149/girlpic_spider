
from re import I

import requests
import json
import os
import time
img_apiurl="https://16k.club/api.php?lang=zh-cn&type=index&size=30&p={}"
foldername = "G:\\folder\\16kclub\\"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type":"text/html;charset=UTF-8"}
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
RETRYTIME=0
def downloadpic(fname, furl):
    global RETRYTIME
    try:
        req = requests.get(furl,headers=headers, proxies=proxy)
        # res = openner.open(req)
        with open(fname, 'wb')as f:
            f.write(req.content)
        return furl
    except Exception as e:
        if(RETRYTIME == 2):
            RETRYTIME = 0
            return "failed"
        RETRYTIME += 1
        downloadpic(fname, furl)

for i in range(1,302):
    apiurl=img_apiurl.format(i)
    resdata=requests.get(apiurl,headers=headers, proxies=proxy)
    res = json.loads(resdata.text)
    imgdata=res['list']
    for img in imgdata:
        imgid=img['id']
        imgpath=img['path']
        imgtitle=img['alt']
        imgname = foldername+"{}_{}{}".format(imgid, imgtitle, os.path.splitext(imgpath)[-1])
        if(not os.path.exists(imgname)):
            downloadpic(imgname, imgpath)
            time.sleep(1)
        print("【{}/{}】{}——{}".format(i, 300, imgid, imgname))        
print("Done")