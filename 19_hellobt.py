from threading import Thread
import requests
from lxml import etree
import os
import time
import sys
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type": "text/html;charset=UTF-8"}

ppfolder = "G:\\folder\\hellobeauty\\"
dictemp = "G:\\folder\\hellobeauty\\{}\\"

urltemplate="https://www.timeleap.net/index.php/page/{}/"

RETRYTIME=0


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


def checkfolderexist(title):
    dirs = os.listdir(ppfolder)
    for dir in dirs:
        temp = dir.split('[')
        temp = dir.replace("[{}".format(temp[len(temp)-1]), "")
        if(temp == title):
            return dir
    return title

def docrawler(pageindex, items):
    for item in items:
        suburl = item.xpath('div/div/div/a/@href')[0]
        title=item.xpath('div/div/div/a/text()')[1].replace('\n', '').strip()
        title=checkfolderexist(title)
        subfolder = dictemp.format(title)
        if(not os.path.exists(subfolder)):
            os.makedirs(subfolder)
        subhtmltext = getpagehtml(suburl)
        if(subhtmltext == "failed"):
            print("请求超时")
            sys.exit()
        subhtml = etree.HTML(subhtmltext)
        imgs = subhtml.xpath('//div[@class="blog-post"]/p/img')
        imgindex = 1
        for img in imgs:
            imgurl = img.xpath('@src')[0]
           
            imgname = "{}{}".format(subfolder, "{}{}".format(
                   str(imgindex).rjust(3, '0'), os.path.splitext(imgurl)[-1]))
            if(not os.path.exists(imgname)):
                downloadpic(imgname, imgurl)
            print("page:【{}/{}】_总【{}/{}】-{}下载完毕".format(pageindex, totalpage,
                                                        imgindex, len(imgs), imgname))
            imgindex += 1
        tempf = os.path.dirname(subfolder).split('[')
        tempf = os.path.dirname(subfolder).replace(
            "[{}".format(tempf[len(tempf)-1]), "")
        newpicfolder = "{}[{}P]".format(tempf, imgindex-1)
        if(subfolder != newpicfolder):
            os.rename(subfolder, newpicfolder)

totalpage = 375
pageindex =1# int(sys.argv[1]) 
GroupNum = 2
totalitems = 0
finisheditem = 0
for i in range(pageindex, totalpage+1):
    print("page：【{}/{}】开始下载".format(i, totalpage))
    starturl = urltemplate.format(i)
    htmltext = getpagehtml(starturl)
    htmls = etree.HTML(htmltext)
    items = htmls.xpath('//div[@class="portfolio-item "]')
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
