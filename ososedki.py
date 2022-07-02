import shutil
import requests
from lxml import etree
import math
import os
import time
picpath = "E:\ososedki\{}\{}\{}"
url="https://ososedki.com/top?page={}"
suburl = "https://ososedki.com{}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type":"text/html;charset=UTF-8"}
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
def downloadpic(fname, furl):
    global RETRYTIME
    try:
        RETRYTIME = 0
        res = requests.get(furl, headers=headers, proxies=proxy)
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


def checkfolderexist(classname,subdic, title):
    pardic = "E:\\ososedki\\{}\\".format(classname)
    if not os.path.exists(pardic):
        os.makedirs(pardic)
    dirs = os.listdir(pardic)
    for dic in dirs:
        checkdic = "E:\\ososedki\\{}\\{}\\{}".format(classname, dic, title)
        if(os.path.exists(checkdic) and subdic != dic):
            shutil.move(checkdic, "E:\\ososedki\\{}\\{}\\{}".format(classname,subdic, title))
            return

pageindex=18
totalpage=4000

while pageindex<totalpage:
    print("开始下载第{}页...".format(pageindex))
    starturl = url.format(pageindex)
    resp = requests.get(url=starturl, headers=headers, proxies=proxy)
    html = etree.HTML(resp.text)
    items = html.xpath('//div[@class="grid-item"]')
    itemindex=1
    for item in items:        
        title = item.xpath('div[1]/a/text()')[0]         
        imgurl = item.xpath('div[1]/a/@href')[0]
        day = item.xpath('div[2]/span/text()')[0]
        if len(item.xpath('div[2]/a/span/text()'))==0:
            classname = "no"
        else:
            classname = item.xpath('div[2]/a/span/text()')[0]
        imgcount = item.xpath('div[3]/span/text()')[0]
        favcount = item.xpath('div[4]/span/text()')[0]
        print("开始下载{}".format(title))
        if(int(favcount) > 100):
            max = math.ceil(int(favcount)/100)*100
            min = max-100
        else:
            max = math.ceil(int(favcount)/10)*10
            min = max-10
        subdic = "{}-{}".format(str(min).rjust(6,'0'), str(max).rjust(6,'0'))

        getVals = list([val for val in title
                        if val.isalpha() or val.isnumeric()])
        title = "".join(getVals)

        targetdic = "{}_{}[{}P]".format(day, title, int(imgcount))
        checkfolderexist(classname,subdic,targetdic)
        fulldic = picpath.format(classname, subdic, targetdic)
        if(not os.path.exists(fulldic)):
            os.makedirs(fulldic)
        detailpage = suburl.format(imgurl)
        subresp = requests.get(url=detailpage, headers=headers, proxies=proxy)
        subhtml = etree.HTML(subresp.text)
        imgitems = subhtml.xpath('//div[@class="grid-item"]')
        imgindex=1
        for img in imgitems:
            temp = img.xpath('a[@data-fancybox="gallery"]')
            if(len(temp) == 0):
                continue
            imgurl = img.xpath('a/@href')[0]
            imgname = os.path.basename(imgurl).split('?')[0]
            imgfullname = "{}\{}".format(fulldic, imgname)
            nofullnmae = "{}\{}".format(fulldic, "{}{}".format(
                str(imgindex).rjust(4, '0'), os.path.splitext(imgname)[-1]))
            if(not os.path.exists(imgfullname)):
                if(not os.path.exists(nofullnmae)):
                    downloadpic(nofullnmae, imgurl)
            else:
                os.rename(imgfullname, nofullnmae)
            print("page:{}【{}/{}】_{}_{}【{}/{}】-{}下载完毕".format(pageindex, itemindex,
                  len(items), classname, title, imgindex, len(imgitems), nofullnmae))
            imgindex+=1
        print("page:{}【{}/{}】_{}_{}下载完毕".format(pageindex,
              itemindex, len(items), classname, title))
        itemindex+=1
        time.sleep(3)

    print("page:{}_{}下载完毕".format(pageindex,title))
    pageindex += 1
    time.sleep(3)