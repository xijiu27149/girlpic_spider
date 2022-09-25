from cgitb import html
from turtle import home
import requests
import time
import os
from lxml import etree
from threading import Thread
import operator
from urllib import request
import sys

homeurl="https://www.vmgirls.com/topics/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type": "text/html;charset=UTF-8",
    "cookie": "disqus_unique=s1p9h51ht375u; __jid=8djoiru2vfduq9"}
# proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
# httpproxy_handler = request.ProxyHandler(
#     {
#         "http": "http://127.0.0.1:7890",
#         "https": "http://127.0.0.1:7890"
#     },
# )
openner = request.build_opener()
ppfolder="/Users/dujingwei/Temp/folder/vmgirls/"
dictemp="/Users/dujingwei/Temp/folder/vmgirls/{}/"
# ppfolder = "H:\\folder\\hotgirl\\"
# dictemp = "H:\\folder\\hotgirl\\{}\\"

RETRYTIME = 0
def downloadpic(fname, furl):
    global RETRYTIME
    try:
        req = requests.get(furl)
        # res = openner.open(req)
        with open(fname, 'wb')as f:
            f.write(req.content)
        return furl
    except Exception as e:        
        if(RETRYTIME == 2):
            RETRYTIME = 0
            return "failed"
        RETRYTIME += 1
        time.sleep(20)
        downloadpic(fname, furl)        


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
        resp = requests.get(pageurl, headers=headers)
        return resp.text
    except:
        if(RETRYTIME == 3):
            RETRYTIME = 0
            return "failed"
        RETRYTIME += 1
        print("{}请求超时，20秒后重试第{}次".format(pageurl, RETRYTIME))
        time.sleep(20)
        getpagehtml(pageurl)

def docrawler(classname,pageno,totalpage,items):
    global totalitems
    global finisheditem
    for item in items:
        title=item.xpath('div/div[2]/div[1]/a/text()')[0]        
        title = title.replace("[", "【").replace("]", "】").replace(
            "/", " ").replace("?", "").replace("*", " ").replace(":", " ").replace("|", " ").replace('\n','').strip()
        title=checkfolderexist(title)
        #if(not operator.contains(title, "The Ultimate Black Silk Legs Series")):
        #    continue
        print("page:【{}】【{}/{}】开始下载：{}".format(classname,pageno,totalpage,title))  
        imgfolder=dictemp.format(title)
        if(not os.path.exists(imgfolder)):
            os.makedirs(imgfolder)
        suburl=item.xpath('div/div[2]/div[1]/a/@href')[0]    
        imgpagehtmltext=getpagehtml(suburl)
        imgpagehtml=etree.HTML(imgpagehtmltext)
        imgs=imgpagehtml.xpath('//img[contains(@class,"size-full wp-image")]/@src')
        imgs1=imgpagehtml.xpath('//div[@class="nc-light-gallery"]/a/img/@src')
        imgs2=imgpagehtml.xpath('//div[@class="nc-light-gallery"]/p/a/img/@src')
        if(len(imgs1)>0):
            imgs.extend(imgs1)
        if(len(imgs2)>0):
            imgs.extend(imgs2)
        imgindex=1
        for imgurl in imgs:           
            imgname = os.path.basename(imgurl)
            imgname = "{}{}".format(imgfolder, "{}{}".format(
            str(imgindex).rjust(3, '0'), os.path.splitext(imgurl)[-1]))
            if(os.path.splitext(imgname)[-1] == ""):
                imgname+=".jpg"
            if(not os.path.exists(imgname)):
                downloadpic(imgname, imgurl)     
            print("【{}】page:【{}/{}】,items:【{}/{}】,imgs:【{}/{}】-{}下载完毕".format(classname,pageno, totalpage, finisheditem, totalitems,
                                                             imgindex, len(imgs),  imgname))
            
            imgindex += 1
            # if(imgindex==len(imgs)-1):
            #     break
        tempf = os.path.dirname(imgfolder).split('[')
        tempf = os.path.dirname(imgfolder).replace(
            "[{}".format(tempf[len(tempf)-1]), "")
        newpicfolder = "{}[{}P]".format(tempf, imgindex-1)
        if(imgfolder!=newpicfolder):
            os.rename(imgfolder, newpicfolder)    
        finisheditem += 1
        print("【{}】page:【{}/{}】,items:【{}/{}】_{}_下载完毕".format(classname,pageno,totalpage,finisheditem,totalitems, title))

GroupNum=1
totalitems=0
finisheditem=0
homehtmltext=getpagehtml(homeurl)
homehtml=etree.HTML(homehtmltext)
classitem=homehtml.xpath('//a[@class="list-goto"]')
cur_class=int(sys.argv[1])-1
cur_page=int(sys.argv[2])
for i in range(0,len(classitem)):
    if(i<cur_class):
        continue
    classurl=classitem[i].xpath('@href')[0]
    classname=classitem[i].xpath('@title')[0]
    classhtmltext=getpagehtml(classurl)
    classhtml=etree.HTML(classhtmltext)
    
    urltemplate=classurl+"page/{}/"
    pageitems=classhtml.xpath('//a[@class="page-numbers"]/text()')
    pagecount=pageitems[len(pageitems)-1]
    for j in range(1,int(pagecount)+1):
        if(i==cur_class and j<cur_page):
            continue
        pageurl=urltemplate.format(j)
        pagehtmltext=getpagehtml(pageurl)
        pagehtml=etree.HTML(pagehtmltext)
        items=pagehtml.xpath('//div[@class="col-6 col-md-3"]')
        totalitems=len(items)
        finisheditem=0
        #创建多线程
        t_list = []
        for t in range(0, len(items), GroupNum):
            th = Thread(target=docrawler, args=(
                classname,j,pagecount, items[t:t+GroupNum]))
            t_list.append(th)
            th.start()
        for t in t_list:
            t.join()
        print("page:【{}】【{}/{}】下载完毕".format(classname,i, pagecount))
        time.sleep(3)
print("Done")