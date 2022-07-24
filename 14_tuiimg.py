
from threading import Thread
import requests
from lxml import etree
import os
import time

urltemplate="https://www.tuiimg.com/meinv/list_{}.html"
pdictemplate="/Users/dujingwei/Temp/folder/tuiimg/{}/"
ppfolder="/Users/dujingwei/Temp/folder/tuiimg/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type": "text/html;charset=UTF-8"}
RETRYTIME=0
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
def downloadpic(fname, furl):
    global RETRYTIME
    try:
        res = requests.get(furl, headers=headers)    
        with open(fname, 'wb')as f:
            f.write(res.content)
        return furl
    except:
        if(RETRYTIME == 2):
            RETRYTIME = 0
            return "failed"
        RETRYTIME += 1
        time.sleep(20)
        downloadpic(fname, furl)       
def docrawler(pageno,items):
    global totalitems
    global finisheditem
    for item in items:
        title=item.xpath('a[2]/text()')[0]        
        title = title.replace("[", "【").replace("]", "】").replace(
            "/", " ").replace("?", "").replace("*", " ").replace(":", " ").replace("|", " ").strip()
        title=checkfolderexist(title)
        #if(not operator.contains(title, "香月杏珠")):
        #    continue
        print("page:【{}/{}】开始下载：{}".format(pageno,totalpage,title))  
        imgfolder=pdictemplate.format(title)
        if(not os.path.exists(imgfolder)):
            os.makedirs(imgfolder)
        suburl=item.xpath('a[1]/@href')[0]
        subhtmlext=getpagehtml(suburl)
        subhtml=etree.HTML(subhtmlext)
        pagestr=subhtml.xpath('//*[@id="allbtn"]/text()')[0]
        pagestr=pagestr.split('/')[1].replace(")","")
        firstimgurl=subhtml.xpath('//*[@id="nowimg"]/@src')[0]
        imgurltemplate=os.path.splitext(firstimgurl)[0][:-1]+"{}"+os.path.splitext(firstimgurl)[-1]
        for k in range (1,int(pagestr)+1):
            imgurl=imgurltemplate.format(k)
            imgname="{}{}".format(imgfolder,"{}{}".format(
                str(k).rjust(3, '0'), os.path.splitext(imgurl)[-1]))
            if(not os.path.exists(imgname)):
                downloadpic(imgname, imgurl)
            print("page:【{}/{}】,items:【{}/{}】【{}/{}】-{}下载完毕".format(pageno, totalpage, finisheditem, totalitems,
                                                                        k, int(pagestr),  imgname))          
        #if(not os.path.dirname(imgfolder)[-2:] == "P]"):  
        tempf = os.path.dirname(imgfolder).split('[')
        tempf = os.path.dirname(imgfolder).replace(
            "[{}".format(tempf[len(tempf)-1]), "")
        newpicfolder = "{}[{}P]".format(tempf, int(pagestr))
        if(imgfolder!=newpicfolder):
            os.rename(imgfolder, newpicfolder)    
        finisheditem += 1
        print("page:【{}/{}】,items:【{}/{}】_{}_下载完毕".format(pageno,totalpage,finisheditem,totalitems, title))
        

totalpage=129
pageindex=1
GroupNum=2
totalitems=0
finisheditem=0
for i in range(pageindex,totalpage+1):   
    print("page：【{}/{}】开始下载".format(i,totalpage))
    starturl=urltemplate.format(i)
    htmltext=getpagehtml(starturl)
    htmls=etree.HTML(htmltext)
    items = htmls.xpath('//div[@class="beauty"]/ul/li')
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