import shutil
from urllib import request
from lxml import etree
import os
import time
import operator
import math
from requests_html import HTMLSession
import ssl
urltemplate="https://xchina.co/photos/kind-1/{}.html"
#urltemplate="https://xchina.co/photos/kind-2/{}.html" 171页
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type": "text/html;charset=UTF-8"}
ssl._create_default_https_context = ssl._create_unverified_context
httpproxy_handler = request.ProxyHandler(
    {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    },
)
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}

#pdictemplate = "H:\\folder\\xchina\\{}\\"
#pdictemplate="/Users/dujingwei/Movies/folder/xchina/{}/"
pdictemplate="/Volumes/ExtremePro/folder/xchina/{}/"
openner = request.build_opener(httpproxy_handler)

def downloadpic(fname, furl):
    try:
        req=request.Request(furl,headers=headers)
        res=openner.open(req)     
        with open(fname, 'wb')as f:
            f.write(res.read())
        return furl
    except:
        return "no"


for i in range(4,351):
    starturl=urltemplate.format(i)
    req = request.Request(starturl, headers=headers)
    resp = openner.open(req)
    resphtml=etree.HTML(resp.read())
    items=resphtml.xpath('//div[@class="item"]')
    itemindex=1
    for item in items:
        if(i==4 and itemindex<14):
            itemindex+=1
            continue
        suburl = "https://xchina.co{}".format(item.xpath('a/@href')[0])
        platname=item.xpath('div[1]/div[1]/a/text()')[0]
        modelname = item.xpath('div[1]/div[2]/a/text()')
        if(len(modelname)==0):
            modelname="无名"
        else:
            modelname=modelname[0]
        title = item.xpath('div[2]/a/text()')[0]
        piccountstr = item.xpath('div[4]/div[1]/text()')[0]
        piccount = piccountstr.split("P")[0]
        subfolder = pdictemplate.format("{}_{}_{}[{}]".format(
            modelname.strip(), platname.strip(), title.strip(), piccountstr))
        if(not os.path.exists(subfolder)):
            os.makedirs(subfolder)
        subreq = request.Request(suburl, headers=headers)
        subresp=openner.open(subreq)
        subhtml = etree.HTML(subresp.read())
        pages=subhtml.xpath('//div[@class="pager"]/div/a')
        totalpage=pages[len(pages)-2].xpath('text()')[0]
        imgindex=1
        for j in range(1,int(totalpage)+1):
            imgpageurl = suburl.replace(os.path.splitext(suburl)[-1],"")
            imgpageurl=imgpageurl+"/{}.html"
            imgpageurl = imgpageurl.format(j)
            imgpagereq = request.Request(imgpageurl, headers=headers)
            imgpageresp = openner.open(imgpagereq) 
            imgpagehtml = etree.HTML(imgpageresp.read())
            videos=imgpagehtml.xpath('//video[@class="player"]/source/@src')
            if(len(videos)>0):
                videourl=videos[0]
                videoname = "{}{}".format(subfolder,os.path.basename(videourl))
                downloadpic(videoname,videourl)
                print("page:{}【{}/{}】_{}-{}下载完毕".format(i, itemindex, len(items),
                                                        title,  videoname))
            imgs = imgpagehtml.xpath('//div[@class="photos"]/a')
            if(len(imgs)==0):
                continue
            for img in imgs:
                imgurl=img.xpath('figure/img/@src')[0]
                imgurl = imgurl.replace("_600x0","")
                imgname = "{}{}".format(subfolder, "{}{}".format(
                    str(imgindex).rjust(3, '0'), os.path.splitext(imgurl)[-1]))
                if(not os.path.exists(imgname)):
                    downloadpic(imgname,imgurl)
                print("page:{}【{}/{}】_{}_第【{}/{}】页_总【{}/{}】-{}下载完毕".format(i, itemindex, len(items),
                    title, j, int(totalpage), imgindex,piccount, imgname))
                imgindex+=1
            time.sleep(3)
        itemindex+=1
print("Done")