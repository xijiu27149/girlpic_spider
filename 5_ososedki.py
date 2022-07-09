import shutil
import requests
from lxml import etree
import math
import os
import time
from threading import Thread

picpath = "H:\\folder\\ososedki\\{}\\"
picpathtemplate = "H:\\folder\\ososedki\\{}\\{}\\{}"

#picpath="/Users/dujingwei/Movies/folder/ososedki/{}/"
#picpathtemplate="/Users/dujingwei/Movies/folder/ososedki/{}/{}/{}"

#picpath="/Volumes/ExtremePro/folder/ososedki/{}/"
#picpathtemplate="/Volumes/ExtremePro/folder/ososedki/{}/{}/{}"
fileformate="{}/{}"
url="https://ososedki.com/top?page={}"
suburl = "https://ososedki.com{}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type":"text/html;charset=UTF-8"}
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}

RETRYTIME=0
def downloadpic(fname, furl):
    global RETRYTIME
    try:
        RETRYTIME = 0
        res = requests.get(furl, headers=headers, proxies=proxy)
        with open(fname, 'wb')as f:
            f.write(res.content)        
        return furl
    except:
        if(RETRYTIME == 5):
            RETRYTIME = 0
            return "failed"
        RETRYTIME += 1
        time.sleep(20)
        downloadpic(fname, furl)


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

def checkfolderexist(classname,subdic, title):
    pardic = picpath.format(classname)
    if not os.path.exists(pardic):
        os.makedirs(pardic)
    dirs = os.listdir(pardic)
    for dic in dirs:
        checkdic = picpathtemplate.format(classname, dic, title)
        if(os.path.exists(checkdic) and subdic != dic):
            shutil.move(checkdic, picpathtemplate.format(classname,subdic, title))
            return


def docrawler(pageindex, imgitems):
    global totalitems
    global finisheditem
    if(pageindex < currentpage):
        return 
    for item in imgitems:
        N = 4
        if(len(item.xpath('div')) == 5):
            N = 5
        title = item.xpath('div[{}]/a/text()'.format(N-3))[0]
        imgurl = item.xpath('div[{}]/a/@href'.format(N-3))[0]
        day = item.xpath('div[{}]/span/text()'.format(N-2))[0]
        if len(item.xpath('div[{}]/a/span/text()'.format(N-2))) == 0:
            classname = "no"
        else:
            classname = item.xpath('div[{}]/a/span/text()'.format(N-2))[0]
        imgcount = item.xpath('div[{}]/span/text()'.format(N-1))[0]
        favcount = item.xpath('div[{}]/span/text()'.format(N))[0]
        print("开始下载{}".format(title))
        if(int(favcount) > 100):
            max = math.ceil(int(favcount)/100)*100
            min = max-100
        else:
            max = math.ceil(int(favcount)/10)*10
            min = max-10
        subdic = "{}-{}".format(str(min).rjust(6, '0'), str(max).rjust(6, '0'))

        getVals = list([val for val in title
                        if val.isalpha() or val.isnumeric()])
        title = "".join(getVals)

        targetdic = "{}_{}[{}P]".format(day, title, int(imgcount))
        checkfolderexist(classname, subdic, targetdic)
        fulldic = picpathtemplate.format(classname, subdic, targetdic)
        if(not os.path.exists(fulldic)):
            os.makedirs(fulldic)
        detailpage = suburl.format(imgurl)
        subresp = requests.get(url=detailpage, headers=headers, proxies=proxy)
        subhtml = etree.HTML(subresp.text)
        imgitems = subhtml.xpath('//div[@class="grid-item"]')
        imgindex = 1
        for img in imgitems:
            temp = img.xpath('a[@data-fancybox="gallery"]')
            if(len(temp) == 0):
                continue
            imgurl = img.xpath('a/@href')[0]
            imgname = os.path.basename(imgurl).split('?')[0]
            imgfullname = fileformate.format(fulldic, imgname)
            nofullnmae = fileformate.format(fulldic, "{}{}".format(
                str(imgindex).rjust(4, '0'), os.path.splitext(imgname)[-1]))
            if(not os.path.exists(imgfullname)):
                if(not os.path.exists(nofullnmae)):
                    downloadpic(nofullnmae, imgurl)
            else:
                if(os.path.exists(nofullnmae)):
                    os.remove(imgfullname)
                else:
                    os.rename(imgfullname, nofullnmae)
            print("page:【{}/{}】,items:【{}/{}】,【{}/{}】_{}-{}下载完毕".format(pageindex, totalpage,finisheditem,totalitems,
                                                         imgindex, len(imgitems), classname, nofullnmae))
            imgindex += 1
        finisheditem += 1
        print("page:【{}/{}】,items:【{}/{}】_{}_{}下载完毕".format(pageindex, totalpage, finisheditem, totalitems,
               classname, title))
        
        

totalpage=4000

currentpage=382
currentitem=10
totalitems = 0
finisheditem = 0
pageindex = currentpage

GroupNum=2
while pageindex<totalpage:
    print("开始下载第{}页...".format(pageindex))
    starturl = url.format(pageindex)
    resp = requests.get(url=starturl, headers=headers, proxies=proxy)
    html = etree.HTML(resp.text)
    items = html.xpath('//div[@class="grid-item"]')
    totalitems = len(items)
    finisheditem = 0
    #创建多线程
    t_list = []
    for t in range(0, len(items), GroupNum):
        th = Thread(target=docrawler, args=(
            pageindex, items[t:t+GroupNum]))
        t_list.append(th)
        th.start()
    for t in t_list:
        t.join()
    print("第{}页下载完毕".format(pageindex))
    time.sleep(3)
    pageindex += 1  
print("Done")  