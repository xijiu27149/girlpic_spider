import imp
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

def downloadpicnopro(fname, furl):    
    try: 
        #ssl._create_default_https_context = ssl._create_unverified_context
        res = requests.get(furl, headers=headers,verify=False)        
        with open(fname, 'wb')as f:
            f.write(res.content)
        return 1
    except Exception as e:
        return 0

RETRYTIME=0
def downloadpic(fname, furl):
    global RETRYTIME
    try:
        res = requests.get(furl, headers=headers, proxies=proxy,allow_redirects=False)
        with open(fname, 'wb')as f:
            f.write(res.content)
        return furl
    except:
        if(downloadpicnopro(fname,furl)==1):
            return furl
        if(RETRYTIME == 2):
            RETRYTIME = 0
            return "no"
        RETRYTIME += 1
        time.sleep(20)
        downloadpic(fname, furl)
        return furl+"下载失败"

def checkfolderexist(subdic,title):
    dirs=os.listdir(pardic)
    for dic in dirs:
        checkdic = picpathtemplate.format(dic, title)
        if(os.path.exists(checkdic) and subdic!=dic):
            shutil.move(checkdic, picpathtemplate.format(subdic, title))
            return 


def downloadNofigure(subdic,items):   
    foldername = "{}[{}P]".format(title, len(imgitems))
    checkfolderexist(subdic, foldername)
    fulldic = picpathtemplate.format(subdic, foldername)
    if(not os.path.exists(fulldic)):
        os.makedirs(fulldic)
    imgindex = 1
    for imgurl in imgitems:  
        imgname = os.path.basename(imgurl)
        imgfullname = "{}{}".format(fulldic, imgname)
        nofullnmae = "{}{}".format(fulldic, "{}{}".format(str(imgindex).rjust(3, '0'), os.path.splitext(imgname)[-1]))
        if(not os.path.exists(imgfullname)):
            if(not os.path.exists(nofullnmae)):
                downloadpic(nofullnmae, imgurl)
        else:
            os.rename(imgfullname, nofullnmae)
        # 转换jpg
        jpgname = nofullnmae.replace("webp", "jpg")
        im=Image.open(nofullnmae)
        im.load()        
        im.save(jpgname)
        os.remove(nofullnmae)
        print("page:{}_{}_{}_【{}/{}】-{}下载完毕".format(pageindex,
                  subdic, title, imgindex, len(imgitems), nofullnmae))
        imgindex += 1
    print("page:{}_{}_{}下载完毕".format(pageindex, subdic, title))
    time.sleep(3)
        

pageindex = 92 #36
totalpage = 652
session=HTMLSession()
while pageindex < totalpage:    
    print("开始下载第{}页...".format(pageindex))    
    starturl = url.format(pageindex)
    page = session.get(starturl)
    page.encoding='utf-8'        
    html = etree.HTML(page.text)
    items = html.xpath('//div[@class="col-md-4 col-sm-6 col-xs-6 ajax-post"]')
    itemindex=1
    for item in items:
        if(pageindex==92 and itemindex<2):
            itemindex+=1
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
        subdic = "{}-{}".format(str(min).rjust(5,'0'), str(max).rjust(5,'0'))
    
        getVals = list([val for val in title
                        if val.isalpha() or val.isnumeric()])
        title = "".join(getVals)
        #if(not operator.contains(title, "大屁股")):
        #    continue
        subresp = session.get(imgurl)
        subresp.encoding='utf-8'
        subhtml = etree.HTML(subresp.text)
        imgitems = subhtml.xpath('//article[@class="single-article"]/figure')
        if(len(imgitems)==0):
            imgitems = subhtml.xpath('//img[@class="lazy"]/@data-original')
            downloadNofigure(subdic, items)
            continue

        foldername = "{}[{}P]".format(title, len(imgitems))
        checkfolderexist(subdic,foldername)

        fulldic = picpathtemplate.format(subdic, foldername)

        if(not os.path.exists(fulldic)):
            os.makedirs(fulldic)
        imgindex=1
        for img in imgitems:
            imgarray = img.xpath('a/@href')
            if len(imgarray)>0:
                imgurl = imgarray[0]
                imgname = os.path.basename(imgurl)
            else:
                imgarray=img.xpath('video/@src')
                if(len(imgarray)==0):
                    continue
                imgurl = "https://www.x6o.com{}".format(imgarray[0])
                imgname = os.path.basename(imgurl)
            imgfullname = "{}{}".format(fulldic, imgname)
            nofullnmae = "{}{}".format(fulldic, "{}{}".format(str(imgindex).rjust(3,'0'), os.path.splitext(imgname)[-1]))
            if(not os.path.exists(imgfullname)):
                if(not os.path.exists(nofullnmae)):
                    downloadpic(nofullnmae, imgurl)
            else:
                os.rename(imgfullname,nofullnmae)
            print("page:{}【{}/{}】_{}_{}_【{}/{}】-{}下载完毕".format(pageindex, itemindex, len(items),
                  subdic, title, imgindex, len(imgitems), nofullnmae))
            imgindex+=1
        
        print("page:{}【{}/{}】_{}_{}下载完毕".format(pageindex,itemindex,len(items), subdic, title))
        itemindex+=1
        time.sleep(3)

    print("page:{}_{}下载完毕".format(pageindex, title))
    time.sleep(3)
    pageindex += 1