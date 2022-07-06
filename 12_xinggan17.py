from re import I
import shutil
import sys
from urllib import request
from lxml import etree
import os
import time
import operator
import math
from requests_html import HTMLSession
import ssl
urltemplate = "https://www.xinggan17.com/forum.php?gid=169"
#urltemplate="https://xchina.co/photos/kind-2/{}.html" 171页
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type": "text/html;charset=UTF-8"}
ssl._create_default_https_context = ssl._create_unverified_context
httpproxy_handler = request.ProxyHandler(
    {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    },
)
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}

pdictemplate = "H:\\folder\\xinggan17\\{}\\{}\\"
ppfolder ="H: \\folder\\xinggan17\\"
#pdictemplate="/Users/dujingwei/Movies/folder/xchina/{}/"
#pdictemplate="/Volumes/ExtremePro/folder/xchina/{}/"
openner = request.build_opener(httpproxy_handler)

RETRYTIME = 0


def downloadpic(fname, furl):
    global RETRYTIME
    try:
        req = request.Request(furl, headers=headers)
        res = openner.open(req)
        with open(fname, 'wb')as f:
            f.write(res.read())
        return furl
    except:
        if(RETRYTIME == 2):
            RETRYTIME = 0
            return "no"
        RETRYTIME += 1
        time.sleep(20)
        downloadpic(fname, furl)
        return furl+"下载失败"


def checkfolderexist(title):
    dirs = os.listdir(ppfolder)
    for dir in dirs:
        temp = dir.split('[')
        temp = dir.replace("[{}".format(temp[len(temp)-1]), "")
        if(temp == title):
            return dir
    return title

def getpagehtml(pageurl):
    global RETRYTIME
    try:
        req = request.Request(pageurl, headers=headers)
        resp = openner.open(req)
        return resp.read()
    except:
        if(RETRYTIME == 3):
            RETRYTIME = 0
            return "failed"
        RETRYTIME += 1
        print("{}请求超时，20秒后重试第{}次".format(pageurl, RETRYTIME))
        time.sleep(20)
        getpagehtml(pageurl)

currentclassindex=0
currentsubclasspage=0

classpagetext=getpagehtml(urltemplate)
if(classpagetext == "failed"):
    print("请求超时")
    sys.exit()
classpagehtml=etree.HTML(classpagetext)
classitems = classpagehtml.xpath('//div[@class="cEefyz"]')
classitemindex=1
for classitem in classitems:
    if(classitemindex<currentclassindex):
        classitemindex+=1
        continue
    classname = classitem.xpath('div/a[2]/text()')[0] + classitem.xpath('div/a[2]/em/text()')[0]
    classurl = "https://www.xinggan17.com/"+classitem.xpath('div/a/@href')[0]
    classsubpagehtmltext=getpagehtml(classurl)
    if(classpagetext == "failed"):
        print("请求超时")
        sys.exit()
    classsubpagehtml=etree.HTML(classsubpagehtmltext)
    totalpage = classsubpagehtml.xpath('//div[@class=pg]/label/span/text()')[0]
    totalpage=totalpage.replace("页","").replace("/","").strip()
    for i in range(1,int(totalpage)+1):
        if(classitemindex == currentclassindex and i < currentsubclasspage):
            continue
        subclasspageurl = classurl.replace(
            classurl.split("/")[-1], "{}.html".format(i))
        subclasspagehtmltext=getpagehtml(subclasspageurl)
        subclasspagehtml=etree.HTML(subclasspagehtmltext)
        items = subclasspagehtml.xpath('//h3[@class="xw0"]')
        itemindex=1
        for item in items:
            itemurl = "https: // www.xinggan17.com/"+item.xpath('a/@href')[0]
            itemtitle = item.xpath('a/text()')[0]
            imgfolder = pdictemplate.format(classname,itemtitle)


    classitemindex+=1


print("Done")
