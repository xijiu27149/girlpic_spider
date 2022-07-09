import shutil
import requests
from lxml import etree
import os
import time
import operator
import math
from threading import Thread
urltemplate="https://picxx.icu/page/{}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type": "text/html;charset=UTF-8"}
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
ppfolder="H:\\folder\\nsfwpicx\\"
pfolder="H:\\folder\\nsfwpicx\\{}\\"
#ppfolder="/Users/dujingwei/Movies/folder/nsfwpicx/"
#pfolder="/Users/dujingwei/Movies/folder/nsfwpicx/{}/"
#ppfolder="/Volumes/ExtremePro/folder/nsfwpicx/"
#pfolder="/Volumes/ExtremePro/folder/nsfwpicx/{}/"
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
        return furl+"下载失败"
    
def checkfolderexist( title):    
    dirs = os.listdir(ppfolder)
    for dir in dirs:
        temp=dir.split('[')
        temp=dir.replace("[{}".format(temp[len(temp)-1]),"")
        if(temp == title):
            return dir
    return title  


def getpagehtml(pageurl):
    global RETRYTIME
    try:
        resp = requests.get(url=pageurl, headers=headers, proxies=proxy)
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
    for item in items:        
        suburl = item.xpath('a/@href')[0]
        daystr = item.xpath('a/span[2]/span/span/text()')
        if(len(daystr) == 0):
            daystr = item.xpath('a/span/span/text()')
        daystr = daystr[0]
        titlearray = item.xpath('a/span[2]/span/h2/text()')
        if(len(titlearray) == 0):
            title = item.xpath('@id')[0].split('-')[1]
        else:
            title = titlearray[0].strip()
            if(len(title) == 0):
                title = item.xpath('@id')[0].split('-')[1]
        folder = "【{}】{}".format(daystr, title)
        folder = checkfolderexist(folder)
        fulldic = pfolder.format(folder)
        if(not os.path.exists(fulldic)):
            os.makedirs(fulldic)
        #suburl="{}#acpwd-{}".format(suburl,os.path.basename(suburl).split(".")[0])

        subhtmltext = getpagehtml(suburl)
        subhtml = etree.HTML(subhtmltext)
        imgs = subhtml.xpath('//div[@class="entry-content"]/p/a/img')
        if(len(imgs) == 0):
            imgs = subhtml.xpath('//div[@class="entry-content"]/figure/img')
            if(len(imgs) == 0):
                imgs = subhtml.xpath(
                    '//div[@class="entry-content"]/figure/a/img')
        imgindex = 1
        for img in imgs:
            imgpageurl = img.xpath('@src')[0]
            if(operator.contains(imgpageurl, 'imgur')):
                imgurl = "https://i.imgur.com/{}.jpeg".format(
                    os.path.basename(imgpageurl).split('.')[0])
            else:
                imgurl = img.xpath('@src')[0]
                imgurl = imgurl.replace("/th/", "/i/")
            imgname = os.path.basename(imgurl)
            fullfilename = "{}{}".format(fulldic, "{}{}".format(
                str(imgindex).rjust(3, '0'), os.path.splitext(imgname)[-1]))
            if(not os.path.exists(fullfilename)):
                downloadpic(fullfilename, imgurl)
            print("page:【{}/{}】_{}_【{}/{}】-{}下载完毕".format(pageindex, totalpage,
                                                          folder, imgindex, len(imgs), fullfilename))
            imgindex += 1
        if(not os.path.dirname(fulldic)[-2:] == "P]"):
            newpicfolder = "{}[{}P]".format(
                os.path.dirname(fulldic), imgindex-1)
            os.rename(fulldic, newpicfolder)


totalpage = 305
currentpage = 1#251
currentitem = 2
GroupNum=2
for i in range(currentpage, totalpage+1):
    
    starturl=urltemplate.format(i)    
    resphtmltext=getpagehtml(starturl)
    resphtml = etree.HTML(resphtmltext)
    items=resphtml.xpath('//div[@class="featured-content content-area fullwidth-area-blog"]/main/article')
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
print("done") 