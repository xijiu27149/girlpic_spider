import shutil
import requests
from lxml import etree
import os
import time
import operator
import math

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


totalpage = 305
currentpage = 81
currentitem = 8

for i in range(currentpage, totalpage+1):
    starturl=urltemplate.format(i)
    resp = requests.get(url=starturl, headers=headers, proxies=proxy)
    resphtml=etree.HTML(resp.text)
    items=resphtml.xpath('//div[@class="featured-content content-area fullwidth-area-blog"]/main/article')
    itemindex=1
    for item in items:
        if(i == currentpage and itemindex < currentitem):
            itemindex+=1
            continue
        suburl=item.xpath('a/@href')[0]
        daystr=item.xpath('a/span[2]/span/span/text()')
        if(len(daystr)==0):
            daystr = item.xpath('a/span/span/text()')
        daystr=daystr[0]
        titlearray = item.xpath('a/span[2]/span/h2/text()')
        if(len(titlearray)==0):
            title=item.xpath('@id')[0].split('-')[1]
        else:
            title=titlearray[0].strip()
            if(len(title)==0):
                title = item.xpath('@id')[0].split('-')[1]
        folder="【{}】{}".format(daystr,title)
        folder = checkfolderexist(folder)
        fulldic=pfolder.format(folder)
        if(not os.path.exists(fulldic)):
            os.makedirs(fulldic)
        #suburl="{}#acpwd-{}".format(suburl,os.path.basename(suburl).split(".")[0])
        subresp = requests.get(url=suburl, headers=headers, proxies=proxy)
        subhtml=etree.HTML(subresp.text)
        imgs = subhtml.xpath('//div[@class="entry-content"]/p/a/img')
        if(len(imgs)==0):
            imgs = subhtml.xpath('//div[@class="entry-content"]/figure/img')
        imgindex=1
        for img in imgs:
            imgpageurl=img.xpath('@src')[0]
            if(operator.contains(imgpageurl,'imgur')):
                imgurl = "https://i.imgur.com/{}.jpeg".format(
                    os.path.basename(imgpageurl).split('.')[0])
            else:
                imgurl = img.xpath('@src')[0]
                imgurl = imgurl.replace("/th/", "/i/")
            imgname = os.path.basename(imgurl)
            fullfilename = "{}{}".format(fulldic, "{}{}".format(
                    str(imgindex).rjust(3, '0'), os.path.splitext(imgname)[-1]))
            if(not os.path.exists(fullfilename)):
                downloadpic(fullfilename,imgurl)
            print("page:【{}/{}】item:【{}/{}】_{}_【{}/{}】-{}下载完毕".format(i,totalpage, itemindex, len(items),
                     title, imgindex, len(imgs), fullfilename))
            imgindex+=1
        if(not os.path.dirname(fulldic)[-2:]=="P]"):
            newpicfolder = "{}[{}P]".format(os.path.dirname(fulldic), imgindex-1)
            os.rename(fulldic,newpicfolder)
        itemindex+=1
        time.sleep(3) 
print("done") 