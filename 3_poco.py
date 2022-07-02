import requests
from lxml import etree
import math
import os
import time

record = "E:\\poco\\rayshen.txt"
picpath = "E:\\poco\\rayshen\\{}"

#url = "https://hm.baidu.com/hm.gif?cc=1&ck=1&cl=24-bit&ds=1920x1080&vl=14456&et=0&ja=0&ln=zh-cn&lo=0&lt=1656227989&rnd=1107857940&si=6ecae4b4661639f51be579865c839753&su=https://www.poco.cn/user/id65856082?page=4&type=works&v=1.2.94&lv=2&api=4_0&sn=38558&r=0&ww=1702&ct=!!&u=https://www.poco.cn/user/id65856082?page={}&type=works&tt=谭钰桐YuTong的个人空间_颇可网"
headers={	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type":"text/html;charset=UTF-8"}
RETRYTIME=0
def downloadpic(fname, furl):
    global RETRYTIME
    try:
        RETRYTIME = 0
        res = requests.get(furl, headers=headers)
        with open(fname, 'wb')as f:
            f.write(res.content)        
        return furl
    except Exception as e:
        if(RETRYTIME == 10):
            RETRYTIME = 0
            return "no"
        RETRYTIME += 1
        time.sleep(20)
        downloadpic(fname, furl)
        return furl+e 


f = open(record, "r", encoding='utf-8')
for line in f:   
    itemurl=line.strip().split(';')[1]
    title=line.strip().split(';')[0]
    resp = requests.get(url=itemurl, headers=headers)
    html=etree.HTML(resp.text)    
    imgdic = picpath.format(title).strip()
    if(not os.path.exists(imgdic)):
        os.makedirs(imgdic)        
    for i in range(5, len(html.xpath('//div'))-31):
        imgurl = 'https:{}'.format(
            html.xpath('//div[{}]/img/@data-src'.format(i))[0])
        imgname = "{}\\{}".format(imgdic, os.path.basename(imgurl))
        if(not os.path.exists(imgname)):
            downloadpic(imgname, imgurl)
        print("{}_{}".format(title,imgname))