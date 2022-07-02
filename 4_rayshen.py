import requests
from lxml import etree
import math
import os
import time

picpath = "E:\\poco\\rayshen\\{}"
url = "http://rayshen.poco.cn/?page={}"
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
    except:
        if(RETRYTIME == 10):
            RETRYTIME = 0
            return "no"
        RETRYTIME += 1
        time.sleep(20)
        downloadpic(fname, furl)
        return furl+"下载失败"
pageindex=1
totalpage=30
while pageindex<totalpage:
    starturl=url.format(pageindex)
    resp=requests.get(url=starturl,headers=headers)
    html=etree.HTML(resp.text)
    for i in range(3,len(html.xpath('//div'))-4):
        title=html.xpath('//div[{}]/h2/text()'.format(i))[0]
        suburl=html.xpath('//div[{}]/a/@href'.format(i))[0]
        imgcount = html.xpath('//div[{}]/p[4]/text()'.format(i))[0].split('：')[1]
        subresp=requests.get(url=suburl,headers=headers)
        subhtml=etree.HTML(subresp.text)
        for j in range(5,5+int(imgcount)):
            imgurl = 'https:{}'.format(
                subhtml.xpath('//div[{}]/img/@data-src'.format(j))[0])
            imgdic = picpath.format(title)
            if(not os.path.exists(imgdic)):
                os.makedirs(imgdic)
            imgname = "{}\\{}".format(imgdic, os.path.basename(imgurl))
            if(not os.path.exists(imgname)):
                downloadpic(imgname,imgurl)
            print("page{}_{}_{}".format(pageindex,title,imgname))
    pageindex+=1     
		