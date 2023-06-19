
from re import I

import requests
import json
from threading import Thread
import os
import time
from lxml import etree
homeurl="https://16k.club/"
pageurltemplate="https://16k.club/index.php?p={}&size=50"
foldername = "G:\\folder\\16kclub\\"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type":"text/html;charset=UTF-8"}
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
RETRYTIME=0
def getpagehtml(pageurl):
    global RETRYTIME
    try:
        resp = requests.get(pageurl, headers=headers,proxies=proxy)
        return resp.text
    except:
        if(RETRYTIME == 3):
            RETRYTIME = 0
            return "failed"
        RETRYTIME += 1
        print("{}请求超时，20秒后重试第{}次".format(pageurl, RETRYTIME))
        time.sleep(20)
        getpagehtml(pageurl)

def getmaxpageno():    
    respdata=getpagehtml(homeurl)
    htmldata = etree.HTML(respdata)
    pageitems=htmldata.xpath('//ul[@class="m-pager"]/li')
    maxitem=pageitems[len(pageitems)-1]
    maxpageno=maxitem.xpath('a/text()')[0]
    return int(maxpageno)
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
def docrawler(pageno,items):
    global totalitems
    global finisheditem
    for item in items:
        targeturl=homeurl+item.xpath('@href')[0]
        imgid=targeturl.split('=')[-1]
        imgtitle=item.xpath('img/@alt')[0]
        imgpath=item.xpath('img/@src')[0]
        imgname = foldername+"{}_{}{}".format(imgid, imgtitle, os.path.splitext(imgpath)[-1])
        if(not os.path.exists(imgname)):
            downloadpic(imgname, imgpath)
            print("【{}/{}】{}——{}".format(pageno, totalpage, imgid, imgname))   
            time.sleep(1)
        tag=item.xpath('span/text()')
        if(len(tag)>0):
            tag=tag[0]
            if(tag=="mp4"):
                mp4text=getpagehtml(targeturl)
                mp4html=etree.HTML(mp4text) 
                videourl=mp4html.xpath('//video/source/@src')[0]
                videoname=foldername+"{}_{}{}".format(imgid, imgtitle, os.path.splitext(videourl)[-1])
                if(not os.path.exists(videoname)):
                    downloadpic(videoname, videourl)
                    print("page:【{}/{}】{}——{}".format(pageno, totalpage, imgid, videoname))   
                    time.sleep(1)
      
        finisheditem += 1
        print("page:【{}/{}】,items:【{}/{}】_{}_下载完毕".format(pageno,totalpage,finisheditem,totalitems,imgtitle))
      
totalpage=getmaxpageno()
pageindex=1
GroupNum=2
totalitems=0
finisheditem=0
for i in range(1,totalpage+1):
    print("page：【{}/{}】开始下载".format(i,totalpage))
    starturl=pageurltemplate.format(i)
    htmltext=getpagehtml(starturl)
    htmls=etree.HTML(htmltext)   
    items=htmls.xpath('//div[@class="row grid"]/div/div/a')
    totalitems=len(items)
    finisheditem=0
     #创建多线程
    t_list = []
    for t in range(0, len(items), GroupNum):
        th = Thread(target=docrawler, args=(
            i, items[t:t+GroupNum]))
        t_list.append(th)
        th.start()
    for t in t_list:
        t.join()
    print("page:【{}/{}】下载完毕".format(i, totalpage))
    time.sleep(3)
print("Done")