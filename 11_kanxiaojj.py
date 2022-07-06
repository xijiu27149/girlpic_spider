import requests
from lxml import etree
import time
import os

urltemplate="https://www.kanxiaojiejie.com/page/{}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type": "text/html;charset=UTF-8"}
pdictemplate = "H:\\folder\\kanxiaojj\\{}\\"
ppfolder = "H:\\folder\\kanxiaojj\\"
RETRYTIME = 0


def checkfolderexist(title):
    dirs = os.listdir(ppfolder)
    for dir in dirs:
        temp = dir.split('[')
        temp = dir.replace("[{}".format(temp[len(temp)-1]), "")
        if(temp == title):
            return dir
    return title
def downloadpic(fname, furl):
    global RETRYTIME
    try:
        res = requests.get(furl, headers=headers)
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


alltotalpage = 131
currentpage = 129
currentitem = 16

for i in range(currentpage,alltotalpage+1):
    starturl=urltemplate.format(i)
    resp=requests.get(url=starturl,headers=headers)
    resphtml=etree.HTML(resp.text)
    items = resphtml.xpath('//div[@class="masonry-inner"]')
    itemindex=1
    for item in items:
        if(i == currentpage and itemindex < currentitem):
            itemindex += 1
            continue
        suburl=item.xpath('div/a/@href')[0]
        id=suburl.split("/")[-1]
        title=item.xpath('h2/a/text()')
        if(len(title)==0):
            title=""
        else:
            title=title[0]
        folder = id+"_"+title.strip()
        folder = checkfolderexist(folder)
        picdic = pdictemplate.format(folder)
        if(not os.path.exists(picdic)):
            os.makedirs(picdic)
        subresp=requests.get(url=suburl,headers=headers)
        subresphtml=etree.HTML(subresp.text)
        imgs = subresphtml.xpath('//div[@class="entry themeform"]/p/img')
        imgindex=1
        for img in imgs:
            imgurl=img.xpath('@src')[0]
            imgname=os.path.basename(imgurl)
            imgname = "{}{}".format(picdic, "{}{}".format(
                str(imgindex).rjust(3, '0'), os.path.splitext(imgurl)[-1]))
            if(not os.path.exists(imgname)):
                downloadpic(imgname,imgurl)
            print("page:【{}/{}】item:【{}/{}】_{}_总【{}/{}】-{}下载完毕".format(i, alltotalpage, itemindex, len(items),
                    title,  imgindex, len(imgs), imgname))
            imgindex+=1
        if(not os.path.dirname(picdic)[-2:] == "P]"):
            newpicfolder = "{}[{}P]".format(
                os.path.dirname(picdic), imgindex-1)
            os.rename(picdic, newpicfolder)
        time.sleep(3)
        itemindex+=1
print("Done")