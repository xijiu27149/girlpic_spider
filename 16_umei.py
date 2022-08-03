
import sys
from threading import Thread
from numpy import empty
import requests
from lxml import etree
import os
import time
import re
homeurl = "https://www.umei.cc/meinvtupian/"
page_api = "https://www.umei.cc/e/action/get_img_a.php"
pdictemplate = "H:\\folder\\umei\\{}\\{}\\"
ppfolder = "H:\\folder\\umei\\{}\\"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type": "text/html;charset=UTF-8"}
RETRYTIME=0
def checkfolderexist(classname,title):   
    dirs = os.listdir(ppfolder.format(classname))
    for dir in dirs:
        temp = dir.split('[')
        temp = dir.replace("[{}".format(temp[len(temp)-1]), "")
        if(temp == title):
            return dir
    return title
def getapidata(next,classid):
    para={
        'next':(None,next),
        'table':(None,"news"),
        'action': (None, "getmorenews"),
        'limit':(None,10),
        'small_length':(None,120),
        'classid':(None,classid)
    }
    resp = requests.post(page_api,data=para)
    return resp.text
def getpagehtml(pageurl):
    global RETRYTIME
    try:
       resp = requests.get(pageurl, headers=headers)  
       
       resp.encoding="utf-8"          
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
def docrawler(classname,classindex,totalclass,pageno,items):
    global totalitems
    global finisheditem
    for item in items:
        title=item.xpath('span/text()')[0]        
        title = title.replace("[", "【").replace("]", "】").replace(
            "/", " ").replace("?", "").replace("*", " ").replace(":", " ").replace("|", " ").strip()
        title = checkfolderexist(classname,title)
        #if(not operator.contains(title, "香月杏珠")):
        #    continue
        print("class:【{}/{}】_{},page:{}开始下载：{}".format(classindex, totalclass,classname, pageno, title))
        imgfolder = pdictemplate.format(classname,title)
        if(not os.path.exists(imgfolder)):
            os.makedirs(imgfolder)
        suburl = "https://www.umei.cc"+item.xpath('@href')[0]
        subhtmlext=getpagehtml(suburl)
        subhtml=etree.HTML(subhtmlext)
        pagestr = subhtml.xpath('//div[@class="gongneng"]/span[4]/text()')[0]
        pagestr = pagestr.split('/')[1].replace("\"", "")
        imgurltemplate = os.path.splitext(
            suburl)[0]+"_{}"+os.path.splitext(suburl)[-1]
        for k in range(1,int(pagestr)+1):
            if(k==1):                
                imgurl = subhtml.xpath('//section[@class="img-content"]/a/img/@src')[0]
            else:
                imgpageurl=imgurltemplate.format(k)
                imgpagehtmltext=getpagehtml(imgpageurl)
                imgpagehtml=etree.HTML(imgpagehtmltext)
                imgurl = imgpagehtml.xpath(
                    '//section[@class="img-content"]/a/img/@src')[0]
                if imgurl=="":
                    continue
            imgname = "{}{}".format(imgfolder, "{}{}".format(
                str(k).rjust(3, '0'), os.path.splitext(imgurl)[-1]))
            if(not os.path.exists(imgname)):
                downloadpic(imgname, imgurl)
            print("class:【{}/{}】_{},page:【{}】,items:【{}/{}】imgpage:【{}/{}】-{}下载完毕".format(classindex, totalclass, classname, pageno, finisheditem, totalitems,
                                                                k, int(pagestr),  imgname))
        
        tempf = os.path.dirname(imgfolder).split('[')
        tempf = os.path.dirname(imgfolder).replace(
            "[{}".format(tempf[len(tempf)-1]), "")
        newpicfolder = "{}[{}P]".format(tempf, int(pagestr))
        if(imgfolder!=newpicfolder):
            os.rename(imgfolder, newpicfolder)    
        finisheditem += 1
        print("class:【{}/{}】_{},page:【{}】,items:【{}/{}】_{}_下载完毕".format(classindex, totalclass, classname, pageno, 
               finisheditem, totalitems, title))
        
if(__name__=="__main__"):
    totalpage=129
    classindex = int(sys.argv[1])  # 3
    pageindex = int(sys.argv[2])  # 1
    GroupNum=1
    totalitems=0
    finisheditem=0
    homepagehtmltext=getpagehtml(homeurl)
    homepagehtml=etree.HTML(homepagehtmltext)
    classnames=homepagehtml.xpath('//div[@class="pic-box"]')
    for i in range(0,len(classnames)):
        if(i+1<classindex):           
            continue
        classname=classnames[i].xpath('h1/text()')[0]
        if(not os.path.exists(ppfolder.format(classname))):
            os.makedirs(ppfolder.format(classname))
        classurl=classnames[i].xpath('h1/small/a/@href')[0]
        classurl = "https://www.umei.cc"+classurl
        classpagehtmltext=getpagehtml(classurl)        
        classid = re.findall(r"classid='(.+?)';", classpagehtmltext)[0]
        for j in range(1,10000000000):
            if(i+1==classindex and j<pageindex):
                continue
            apidata=getapidata(j,classid)
            itemlisthtml=etree.HTML(apidata)
            itemlist=itemlisthtml.xpath('//ul/li/a')
            if(len(itemlist)==0):
                print("class:【{}/{}】_{}，下载完毕，共{}页".format(i+1,
                      len(classnames), classname, j-1))
                break
            totalitems = len(itemlist)
            finisheditem = 0
            #创建多线程
            t_list = []
            for t in range(0, len(itemlist), GroupNum):
                th = Thread(target=docrawler, args=(classname,i+1, len(classnames),j,
                    itemlist[t:t+GroupNum]))
                t_list.append(th)
                th.start()
            for t in t_list:
                t.join()
            print("class:【{}/{}】_{}，page:{}下载完毕".format(i, len(classnames),classname,j))
    print("Done")