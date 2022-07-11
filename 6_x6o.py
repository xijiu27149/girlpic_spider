from distutils.file_util import move_file
from logging import exception
import shutil
import requests
from lxml import etree
import math
import os
import time
from requests_html import HTMLSession
import operator
from PIL import Image
import ssl
import urllib3
from threading import Thread
urllib3.disable_warnings()

pardic = "H:\\folder\\x6o"
picpathtemplate = "H:\\folder\\x6o\\{}\\{}\\"

#pardic="/Users/dujingwei/Movies/folder/x6o"
#picpathtemplate="/Users/dujingwei/Movies/folder/x6o/{}/{}/"

#pardic="/Volumes/ExtremePro/folder/x6o"
#picpathtemplate="/Volumes/ExtremePro/folder/x6o/{}/{}/"
url = "https://www.x6o.com/picture/page/{}"

cookie = "cf_clearance=OeOPbDmnHs53DT0wczJbVPSF6CUBdCYKdFzvw9fWhbQ-1655294502-0-150; tt_ref=; _gid=GA1.2.501791040.1656424510; __cf_bm=Q5wDbGQr97sLtur1oJIh4OQ9218RKoNez57jFgVMlGw-1656476733-0-ARM1D7AdhW/d1sL/diyiMTO5YdS9G5Hhu0xIx+GuA1OTqKQh/Z7ijqrxWUaCDAtf4+yiUN1JPwPbbosQj4vU+Tki6U3UkoAGHcvvUzmDCsPzzgljo3up5xzxNKNHywT1/Q==; _ga_CHK7JCB72Z=GS1.1.1656476733.5.1.1656476790.0; _ga=GA1.2.266745953.1655294489"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37",
    "Content-Type": "text/html;charset=UTF-8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept":"*/*"}
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
session = HTMLSession()

def downloadpicnopro(fname, furl):    
    try: 
        #ssl._create_default_https_context = ssl._create_unverified_context
        res = requests.get(furl, headers=headers,verify=False)        
        with open(fname, 'wb')as f:
            f.write(res.content)
        return 1
    except Exception as e:
        if(operator.contains(str(e.args[0]), "Max retries exceeded with url")):
            return 1
        return 0

RETRYTIME=0
def downloadpic(fname, furl):
    global RETRYTIME
    try:
        res = requests.get(furl, headers=headers, proxies=proxy,allow_redirects=False)
        with open(fname, 'wb')as f:
            f.write(res.content)
        return furl
    except Exception as  e:                
        if(downloadpicnopro(fname,furl)==1):
            return furl
        if(RETRYTIME == 2):
            RETRYTIME = 0
            return "no"
        RETRYTIME += 1
        time.sleep(10)
        downloadpic(fname, furl)

def checkfolderexist(subdic,title):
    dirs=os.listdir(pardic)
    for dic in dirs:
        checkdic = picpathtemplate.format(dic, title)
        if(os.path.exists(checkdic) and subdic!=dic):
            shutil.move(
                checkdic, "H:\\folder\\x6o\\{}\\".format(subdic))
            return 


def downloadNofigure(title,subdic,items): 
    global totalitems
    global finisheditem
    foldername = "{}[{}P]".format(title, len(items))
    checkfolderexist(subdic, foldername)
    fulldic = picpathtemplate.format(subdic, foldername)
    if(not os.path.exists(fulldic)):
        os.makedirs(fulldic)
    imgindex = 1
    for imgurl in items:
        imgname = os.path.basename(imgurl)
        imgfullname = "{}{}".format(fulldic, imgname)
        nofullnmae = "{}{}".format(fulldic, "{}{}".format(str(imgindex).rjust(3, '0'), os.path.splitext(imgname)[-1]))
        if(not os.path.exists(imgfullname)):
            if(not os.path.exists(nofullnmae)):
                downloadpic(nofullnmae, imgurl)
        else:
            os.rename(imgfullname, nofullnmae)
        # 转换jpg
        
        # if(os.path.splitext(imgname)[-1] == "webp"):
        #     jpgname = nofullnmae.replace("webp", "jpg")
        #     im=Image.open(nofullnmae)
        #     im.load()        
        #     im.save(jpgname)
        #     os.remove(nofullnmae)
        print("page:【{}/{}】,items:【{}/{}】，【{}/{}】-{}下载完毕".format(pageindex, totalpage,finisheditem,totalitems,
                                                    imgindex, len(items), nofullnmae))
        imgindex += 1
    finisheditem+=1
        
def movefiles(numfolder,olddicname,newdicname,imgcount):
    oldfoldername = "{}[{}P]".format(olddicname, imgcount)
    newfoldername = "{}[{}P]".format(newdicname, imgcount)
    #oldfulldic = picpathtemplate.format(numfolder, oldfoldername)
    newfulldic = picpathtemplate.format(numfolder, newfoldername)
    if(not os.path.exists(newfulldic)):
        os.makedirs(newfulldic)
    dirs = os.listdir(pardic)
    for dic in dirs:
        oldfulldic = picpathtemplate.format(dic, oldfoldername)
        if(os.path.exists(oldfulldic)):
            oldfiles=os.listdir(oldfulldic)
            if(len(oldfiles)>0):
                for ff in oldfiles:
                    shutil.move(oldfulldic+ff,newfulldic+ff)
            #os.remove(oldfulldic)


def getpagehtml(pageurl):
    global RETRYTIME
    try:
        #page = session.get(pageurl,proxies=proxy)
        page = session.get(pageurl)
        page.encoding = 'utf-8'        
        return page.text
    except:
        if(RETRYTIME == 3):
            RETRYTIME = 0
            return "failed"
        RETRYTIME += 1
        print("{}请求超时，20秒后重试第{}次".format(pageurl, RETRYTIME))
        time.sleep(20)
        getpagehtml(pageurl)


def docrawler(pageindex, items):
    global totalitems
    global finisheditem
    for item in items:
        if(pageindex < currentpage ):
            itemindex += 1
            continue
        title = item.xpath('article/div[2]/header/h2/a/text()')[0]
        imgurl = item.xpath('article/div[1]/a/@href')[0]
        favcount = item.xpath('article/div[2]/header/div/span[3]/text()')[0]

        print("开始下载{}".format(title))
        if(int(favcount) > 100):
            max = math.ceil(int(favcount)/100)*100
            min = max-100
        else:
            max = math.ceil(int(favcount)/10)*10
            min = max-10
        subdic = "{}-{}".format(str(min).rjust(5, '0'), str(max).rjust(5, '0'))

        getVals = list([val for val in title
                        if val.isalpha() or val.isnumeric()])
        oldtitle = "".join(getVals)
        title = title.replace(
            "/", "").replace("*", " ").replace(":", " ").replace("|", " ").replace("?", " ").replace("<", " ").replace(">", " ")

        subhtmltext = getpagehtml(imgurl)
        subhtml = etree.HTML(subhtmltext)
        imgitems = subhtml.xpath('//article[@class="single-article"]/figure')
        #movefiles(subdic, oldtitle, title, len(imgitems))

        if(len(imgitems) == 0):
            imgitems = subhtml.xpath('//img[@class="lazy"]/@data-original')
            downloadNofigure(title, subdic, imgitems)
            continue

        foldername = "{}[{}P]".format(title, len(imgitems))
        checkfolderexist(subdic, foldername)
        fulldic = picpathtemplate.format(subdic, foldername)

        if(not os.path.exists(fulldic)):
            os.makedirs(fulldic)
        imgindex = 1
        for img in imgitems:
            imgarray = img.xpath('a/@href')
            if len(imgarray) > 0:
                imgurl = imgarray[0]
                imgname = os.path.basename(imgurl)
            else:
                imgarray = img.xpath('video/@src')
                if(len(imgarray) == 0):
                    continue
                imgurl = "https://www.x6o.com{}".format(imgarray[0])
                imgname = os.path.basename(imgurl)
            imgfullname = "{}{}".format(fulldic, imgname)
            nofullnmae = "{}{}".format(fulldic, "{}{}".format(
                str(imgindex).rjust(3, '0'), os.path.splitext(imgname)[-1]))
            if(not os.path.exists(imgfullname)):
                if(not os.path.exists(nofullnmae)):
                    downloadpic(nofullnmae, imgurl)
            else:
                os.rename(imgfullname, nofullnmae)
            print("page:【{}/{}】,items:【{}/{}】，imgs:【{}/{}】_{}_-{}下载完毕".format(pageindex,
                  totalpage, finisheditem, totalitems,  imgindex, len(imgitems), subdic, nofullnmae))
            imgindex += 1
        finisheditem += 1
        print("page:【{}/{}】,items:【{}/{}】_{}_{}下载完毕".format(pageindex,
              totalpage, finisheditem, totalitems, subdic, title))



totalpage = 652
currentpage = 390
currentitem = 1
totalitems = 0
finisheditem = 0
pageindex = currentpage  

GroupNum=2
while pageindex < totalpage:    
    print("开始下载第{}页...".format(pageindex))    
    starturl = url.format(pageindex)
    htmltext=getpagehtml(starturl)
    html = etree.HTML(htmltext)
    items = html.xpath('//div[@class="col-md-4 col-sm-6 col-xs-6 ajax-post"]')
    totalitems=len(items)
    finisheditem=0
    #创建多线程
    t_list = []
    for t in range(0, len(items), GroupNum):
        th = Thread(target=docrawler, args=(
            pageindex, items[t:t+GroupNum]))
        t_list.append(th)
        th.start()
    for t in t_list:
        t.join()       
    print("page:【{}/{}】下载完毕".format(pageindex, totalpage))
    pageindex += 1
    time.sleep(3)
print("Done")