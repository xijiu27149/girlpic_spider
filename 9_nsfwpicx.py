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

ppfolder="H:\\folder\\nsfwpicx\\"
pfolder="H:\\folder\\nsfwpicx\\{}\\"
#ppfolder="/Volumes/ExtremePro/folder/nsfwpicx/"
#pfolder="/Volumes/ExtremePro/folder/nsfwpicx/{}/"

def downloadpic(fname, furl):    
    try:        
        res = requests.get(furl, headers=headers)
        with open(fname, 'wb')as f:
            f.write(res.content)
        return furl
    except:       
        return "no"
    
def checkfolderexist( title):    
    dirs = os.listdir(ppfolder)
    for dic in dirs:
        if(dic.split('[')[0]==title):
                return dic
    return title  

for i in range(2,304):
    starturl=urltemplate.format(i)
    resp=requests.get(url=starturl,headers=headers)
    resphtml=etree.HTML(resp.text)
    items=resphtml.xpath('//div[@class="featured-content content-area fullwidth-area-blog"]/main/article')
    itemindex=1
    for item in items:
        suburl=item.xpath('a/@href')[0]
        daystr=item.xpath('a/span[2]/span/span/text()')[0]
        titlearray=item.xpath('a/span[2]/span/h2/text()')        
        if(len(titlearray)==0):
            title="{}_{}".format(i,itemindex)
        else:
            title=titlearray[0]
        folder="【{}】{}".format(daystr,title)
        folder = checkfolderexist(folder)
        fulldic=pfolder.format(folder)
        if(not os.path.exists(fulldic)):
            os.makedirs(fulldic)
        suburl="{}#acpwd-{}".format(suburl,os.path.basename(suburl).split(".")[0])
        subresp=requests.get(url=suburl,headers=headers)
        subhtml=etree.HTML(subresp.text)
        imgs=subhtml.xpath('//a[@rel="noopener"]')
        imgindex=1
        for img in imgs:
            imgurl=img.xpath('img/@src')[0]
            imgurl=imgurl.replace("/th/","/i/")
            imgname=os.path.basename(imgurl)
            fullfilename = "{}{}".format(fulldic, "{}{}".format(
                    str(imgindex).rjust(3, '0'), os.path.splitext(imgname)[-1]))
            if(not os.path.exists(fullfilename)):
                downloadpic(fullfilename,imgurl)
            print("page:{}【{}/{}】_{}_【{}/{}】-{}下载完毕".format(i, itemindex, len(items),
                     title, imgindex, len(imgs), fullfilename))
            imgindex+=1
        if(not os.path.dirname(fulldic)[-2:]=="P]"):
            newpicfolder = "{}[{}P]".format(os.path.dirname(fulldic), imgindex-1)
            os.rename(fulldic,newpicfolder)
        itemindex+=1
        time.sleep(3) 
print("done") 