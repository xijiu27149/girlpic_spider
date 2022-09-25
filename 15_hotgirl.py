import requests
import time
import os
from lxml import etree
from threading import Thread
import operator
from urllib import request
import sys
from PIL import Image
urltemplate="https://hotgirl.asia/photos/page/{}/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type": "text/html;charset=UTF-8",
    "cookie": "disqus_unique=s1p9h51ht375u; __jid=8djoiru2vfduq9"}
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
httpproxy_handler = request.ProxyHandler(
    {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    },
)
openner = request.build_opener(httpproxy_handler)
#ppfolder="/Users/dujingwei/Temp/folder/hotgirl/"
#dictemp="/Users/dujingwei/Temp/folder/hotgirl/{}/"
ppfolder = "H:\\folder\\hotgirl\\"
dictemp = "H:\\folder\\hotgirl\\{}\\"

RETRYTIME = 0
def downloadpic(fname, furl):
    global RETRYTIME
    try:
        req = request.Request(furl, headers=headers)
        res = openner.open(req)
        with open(fname, 'wb')as f:
            f.write(res.read())
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


def getpagehtml(pageurl,protype=0):
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
def checkfilesize(filepath):
    fsize = Image.open(filepath).size
    try:
        if(int(fsize[0] == 180) and int(fsize[1] == 180)):
            return True
        else:
            return False
    except:
        return True
def getmaxfileNo(dicpath):
    files=os.listdir(dicpath)
    if len(files)==0:
        return 0
    maxno=0
    for file in files:
        filename=file.split('.')[0]
        if(int(filename)>maxno):
            maxno = int(filename)
    return maxno
def docrawler(pageno,items):
    global totalitems
    global finisheditem
    for item in items:
        title=item.xpath('div/div[1]/text()')[0]        
        title = title.replace("[", "【").replace("]", "】").replace(
            "/", " ").replace("?", "").replace("*", " ").replace(":", " ").replace("|", " ").replace('\n','').strip()
        title=checkfolderexist(title)
        #if(not operator.contains(title, "So Hot")):
        #    continue     
        print("page:【{}/{}】开始下载：{}".format(pageno,totalpage,title))  
        imgfolder=dictemp.format(title)
        if(not os.path.exists(imgfolder)):
            os.makedirs(imgfolder)
        suburl=item.xpath('a/@href')[0]
        imgpagehtmltext=getpagehtml(suburl)
        imgpagehtml=etree.HTML(imgpagehtmltext)
        maxpage=imgpagehtml.xpath('//ul[@class="pagination"]/li')
        maxpage=maxpage[-1].xpath('a/text()')[0]
        imgcount=imgpagehtml.xpath('//*[@id="mv-info"]/div[3]/div[3]/div[3]/div[2]/p/span/text()')[0]
        imgindex=1
        for k in range(1,int(maxpage)+1):
            imgpageurl=suburl+str(k)
            imgdatahtmltext=getpagehtml(imgpageurl)
            imgdatahtml=etree.HTML(imgdatahtmltext)
            imgs=imgdatahtml.xpath('//div[@class="galeria_img"]/img/@src')
            for imgurl in imgs:
                imgurl=imgurl.strip()
                imgname = os.path.basename(imgurl)
                imgname = "{}{}".format(imgfolder, "{}{}".format(
                str(imgindex).rjust(3, '0'), os.path.splitext(imgurl)[-1]))
                if(os.path.splitext(imgname)[-1] == ""):
                    imgname+=".jpg"
                if(imgindex>1):
                    if getmaxfileNo(imgfolder)<imgindex-1:

                    # preimgname = "{}{}".format(imgfolder, "{}{}".format(
                    #     str(imgindex-1).rjust(3, '0'), os.path.splitext(imgname)[-1]))
                    # if(not os.path.exists(preimgname)):
                        print("page:【{}/{}】,items:【{}/{}】,subpage:【{}/{}】,imgs:【{}/{}】-{}跳过".format(pageno, totalpage, finisheditem, totalitems, k, maxpage,
                                                                                                      imgindex, imgcount,  imgname))
                        imgindex += 1
                        continue
                if(not os.path.exists(imgname)):
                    downloadpic(imgname, imgurl)   
                else:
                    if(checkfilesize(imgname)):
                        os.remove(imgname)
                        downloadpic(imgname, imgurl)
                print("page:【{}/{}】,items:【{}/{}】,subpage:【{}/{}】,imgs:【{}/{}】-{}下载完毕".format(pageno, totalpage, finisheditem, totalitems,k,maxpage,
                                                                        imgindex, imgcount,  imgname))
                imgindex += 1
        #if(not os.path.dirname(imgfolder)[-2:] == "P]"):  
        tempf = os.path.dirname(imgfolder).split('[')
        tempf = os.path.dirname(imgfolder).replace(
            "[{}".format(tempf[len(tempf)-1]), "")
        newpicfolder = "{}[{}P]".format(tempf, imgindex-1)
        if(imgfolder!=newpicfolder):
            os.rename(imgfolder, newpicfolder)    
        finisheditem += 1
        print("page:【{}/{}】,items:【{}/{}】_{}_下载完毕".format(pageno,totalpage,finisheditem,totalitems, title))
        

totalpage=1648
pageindex = int(sys.argv[1]) #1635
GroupNum=2
totalitems=0
finisheditem=0
for i in range(pageindex, 0, -1):
    print("page：【{}/{}】开始下载".format(i,totalpage))
    starturl=urltemplate.format(i)
    htmltext=getpagehtml(starturl)
    htmls=etree.HTML(htmltext)
    items = htmls.xpath('//div[@class="ml-item"]')
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