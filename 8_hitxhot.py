import shutil
import requests
from lxml import etree
import os
import time
import operator
import math
from threading import Thread
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type": "text/html;charset=UTF-8"}
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
urltemplate="https://hitxhot.com/hot?page={}"

pfolder="H:\\folder\\hitxhot\\"
picpath = "H:\\folder\\hitxhot\\{}\\{}\\"
#pfolder="/Users/dujingwei/Movies/folder/hitxhot/"
#picpath="/Users/dujingwei/Movies/folder/hitxhot/{}/{}/"
#pfolder="/Volumes/ExtremePro/folder/hitxhot/"
#picpath="/Volumes/ExtremePro/folder/hitxhot/{}/{}/"

RETRYTIME = 0
def downloadpic(fname, furl):
    global RETRYTIME
    try:
        res = requests.get(furl, headers=headers,proxies=proxy)
        with open(fname, 'wb')as f:
            f.write(res.content)
        return furl
    except:
        if(RETRYTIME == 2):
            RETRYTIME = 0
            return "no"
        RETRYTIME += 1
        time.sleep(20)
        downloadpic(fname, furl)
       

def checkfolderexist( title):    
    dirs = os.listdir(pfolder)
    for dic in dirs:
        if(dic[0]=="."):
            continue
        sondic=os.listdir(pfolder+dic)
        for son in sondic:
            if(son.split('[')[0]==title):
                return son
    return title


def getpagehtml(pageurl):
    global RETRYTIME
    try:
        resp=requests.get(url=pageurl,headers=headers,proxies=proxy)
        return resp.text
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
        if(pageindex < currentpage):            
            continue
        suburl = item.xpath('div/ins/a[1]/@href')[0]
        suburl = "https://hitxhot.com{}".format(suburl)
        title = item.xpath('div/a[1]/text()')[0]
        if(operator.contains(title, '国模') or operator.contains(title, '台模')):
            continue
        title = title.replace("/", "").replace("*",
                                               " ").replace(":", " ").replace("|", " ").replace("?", " ")
        print("page:{},开始下载:{}".format(pageindex,title))
        favcount = item.xpath('div/ins/a[1]/span/span/text()')[0]
        favcount = favcount.replace("Views", "")
        foldername = title
        if(int(favcount) > 100):
            max = math.ceil(int(favcount)/100)*100
            min = max-100
        else:
            max = math.ceil(int(favcount)/10)*10
            min = max-10
        subdic = "{}-{}".format(str(min).rjust(5, '0'), str(max).rjust(5, '0'))
        foldername = checkfolderexist(foldername)
        picfolder = picpath.format(subdic, foldername)
        if(not os.path.exists(picfolder)):
            os.makedirs(picfolder)

        subhtmltext = getpagehtml(suburl)
        subhtml = etree.HTML(subhtmltext)
        subpagecount = subhtml.xpath(
            '/html/body/div[1]/div[2]/div[4]/div[2]/div/div[1]/div/h2/text()')
        if (len(subpagecount) == 0):
            subpagecount = ""
        else:
            subpagecount = subpagecount[0]
        subpagecountarray = subpagecount.split('/')

        if(len(subpagecountarray) < 2):
            subpagecount = 1
        else:
            subpagecount = subpagecount.split('/')[1]
        if(not str(subpagecount).isdigit()):
            subpagecount = 1
        imgindex = 1
        filenamelength=3
        if(8*int(subpagecount)>1000):
            filenamelength=4
        for j in range(1, int(subpagecount)+1):
            pageurl = "{}?page={}".format(suburl, j)
            pagehtmltext = getpagehtml(pageurl)
            pagehtml = etree.HTML(pagehtmltext)
            imgs = pagehtml.xpath('//div[@class="contentme"]/img')
            for img in imgs:
                imgurl = img.xpath('@src')[0]
                imgname = os.path.basename(imgurl)
                nofullnmae = "{}{}".format(picfolder, "{}{}".format(
                    str(imgindex).rjust(filenamelength, '0'), os.path.splitext(imgname)[-1]))
                if(not os.path.exists(nofullnmae)):
                    downloadpic(nofullnmae, imgurl)
                print("page:【{}/{}】,items:【{}/{}】,imgpage:【{}/{}_{}】-{}下载完毕".format(i, totalpage, finisheditem, totalitems,
                                                                         j, int(subpagecount), imgindex,  nofullnmae))
                imgindex +=1

        if(not os.path.dirname(picfolder)[-2:] == "P]"):
            newpicfolder = "{}[{}P]".format(
                os.path.dirname(picfolder), imgindex-1)
            if(not os.path.exists(newpicfolder)):
                os.rename(picfolder, newpicfolder)
        finisheditem += 1
        print("page:【{}/{}】,items:【{}/{}】_{}_下载完毕".format(pageindex,
              totalpage, finisheditem, totalitems, title))

totalpage=387
currentpage = 342
currentitem = 11
totalitems = 0
finisheditem = 0
GroupNum=2
for i in range(currentpage, totalpage+1):
    if(i<currentpage):
        continue
    starturl=urltemplate.format(i)
    htmltext=getpagehtml(starturl)  
    html = etree.HTML(htmltext)
    items = html.xpath(
        '//div[@class="thumb-view post blish andard has-post-thumbnail hentry asian"]')
    totalitems = len(items)
    finisheditem = 0
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