import shutil
import requests
from lxml import etree
import os
import time
import operator
import math
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
        return furl+"下载失败"
       

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

totalpage=381

currentpage = 29
currentitem = 9

for i in range(currentpage, totalpage+1):
    starturl=urltemplate.format(i)
    resp = requests.get(url=starturl, headers=headers, proxies=proxy)
    html=etree.HTML(resp.text)
    items = html.xpath(
        '//div[@class="thumb-view post blish andard has-post-thumbnail hentry asian"]')
    itemindex=1
    for item in items:
        if(i == currentpage and itemindex < currentitem):
            itemindex+=1
            continue
        suburl=item.xpath('div/ins/a[1]/@href')[0]
        suburl = "https://hitxhot.com{}".format(suburl)
        title = item.xpath('div/a[1]/text()')[0]
        title = title.replace("/", "").replace("*", " ").replace(":", " ")
        favcount = item.xpath('div/ins/a[1]/span/span/text()')[0]
        favcount=favcount.replace("Views","")
        foldername =title
        if(int(favcount) > 100):
            max = math.ceil(int(favcount)/100)*100
            min = max-100
        else:
            max = math.ceil(int(favcount)/10)*10
            min = max-10
        subdic = "{}-{}".format(str(min).rjust(5, '0'), str(max).rjust(5, '0'))
        foldername = checkfolderexist(foldername)
        picfolder=picpath.format(subdic,foldername)        
        if(not os.path.exists(picfolder)):
            os.makedirs(picfolder)
        subresp = requests.get(url=suburl, headers=headers, proxies=proxy)
        subhtml=etree.HTML(subresp.text)
        subpagecount = subhtml.xpath(
            '/html/body/div[1]/div[2]/div[4]/div[2]/div/div[1]/div/h2/text()')
        if (len(subpagecount)==0):
            subpagecount = ""
        else:
            subpagecount=subpagecount[0]
        subpagecountarray=subpagecount.split('/')
        
        if(len(subpagecountarray)<2):
            subpagecount=1
        else:
             subpagecount=subpagecount.split('/')[1]
        if(not str(subpagecount).isdigit()):
            subpagecount=1
        imgindex=1
        for j in range(1,int(subpagecount)+1):
            pageurl="{}?page={}".format(suburl,j)
            pageresp = requests.get(
                url=pageurl, headers=headers, proxies=proxy)
            pagehtml=etree.HTML(pageresp.text)
            imgs = pagehtml.xpath('//div[@class="contentme"]/img')
            for img in imgs:
                imgurl=img.xpath('@src')[0]
                imgname=os.path.basename(imgurl)
                nofullnmae = "{}{}".format(picfolder, "{}{}".format(
                    str(imgindex).rjust(3, '0'), os.path.splitext(imgname)[-1]))
                if(not os.path.exists(nofullnmae)):
                    downloadpic(nofullnmae,imgurl)
                print("page:【{}/{}】Item:【{}/{}】_{}_{}_imgpage:【{}/{}_{}】-{}下载完毕".format(i,totalpage, itemindex, len(items),
                    subdic, title, j, int(subpagecount), imgindex, nofullnmae))
                imgindex+=1
        
        if(not os.path.dirname(picfolder)[-2:]=="P]"):
            newpicfolder = "{}[{}P]".format(os.path.dirname(picfolder), imgindex-1)
            if(not os.path.exists(newpicfolder)):
                os.rename(picfolder,newpicfolder)
        itemindex+=1
        time.sleep(3)    
    time.sleep(3)