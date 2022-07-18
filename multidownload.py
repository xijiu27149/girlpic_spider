import asyncio
import aiohttp
import time
import os
import requests
from lxml import etree
from tkinter import *

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type": "text/html;charset=UTF-8"}
myproxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
root = Tk()

class ImgNameUrl:
    def __init__(self, ImgFileName, ImgDownLoadUrl):
        self.ImgFileName = ImgFileName
        self.ImgDownLoadUrl = ImgDownLoadUrl

async def fetch(session,url):
    if(os.path.exists(url.ImgFileName)):
        return 
    async with session.get(url.ImgDownLoadUrl, verify_ssl=False, proxy="http://127.0.0.1:7890") as response:
        with open(url.ImgFileName, 'ab') as f:
            while True:
                chunk = await response.content.read(1024)
                if not chunk:
                    break
                f.write(chunk)
                #print(url.ImgFileName+"__下载完成")

async def main(urlList):
    async with aiohttp.ClientSession() as session:
        task = [ asyncio.create_task( fetch(session,url)) for url in urlList ]
        done,pending = await asyncio.wait(task)


def dodownload(imgpageurl, dicname):
    try:
        urlList = downloadimgurl(imgpageurl, dicname)
        numbers_of_async = 50
        numbers_of_times = int(len(urlList)/numbers_of_async) if not len(
            urlList) % numbers_of_async else int(len(urlList)/numbers_of_async) + 1
        for number in range(numbers_of_times):
            asyncio.get_event_loop().run_until_complete(
                main(urlList[number*numbers_of_async:number*numbers_of_async+numbers_of_async]))
        return "下载完成{}".format(dicname)
    except Exception as e:
        return e.args


def downloadimgurl(pageurl, fulldic):
    i=0
    while i<3:
        try:
            subresp = requests.get(url=pageurl, headers=headers, proxies=myproxy,timeout=5)
            subhtml = etree.HTML(subresp.text)
            imgitems = subhtml.xpath('//div[@class="grid-item"]')
            imgindex = 1
            img_lst=[]
            for img in imgitems:
                temp = img.xpath('a[@data-fancybox="gallery"]')
                if(len(temp) == 0):
                    continue
                imgurl = img.xpath('a/@href')[0]
                imgname = os.path.basename(imgurl).split('?')[0]
                nofullname = fulldic+"\\{}{}".format(
                    str(imgindex).rjust(4, '0'), os.path.splitext(imgname)[-1])
                img_lst.append(ImgNameUrl(nofullname,imgurl))
                imgindex += 1
            return img_lst
        except:
            i+=1


def confirmclick():
    dicname = txt_dic.get(1.0, "end").strip()
    imgpageurl = txt_url.get(1.0, "end").strip()
    # 设置异步任务数
    numbers_of_async = 50

    urlList = downloadimgurl(imgpageurl, dicname)

    numbers_of_times = int(len(urlList)/numbers_of_async) if not len(
        urlList) % numbers_of_async else int(len(urlList)/numbers_of_async) + 1
    for number in range(numbers_of_times):
        asyncio.get_event_loop().run_until_complete(
            main(urlList[number*numbers_of_async:number*numbers_of_async+numbers_of_async]))

if __name__ == '__main__':
    txt_dic = Text(root)
    txt_url = Text(root)

    btn_ok = Button(root, text="确定", command=confirmclick)

    txt_url.pack()
    txt_dic.pack()
    btn_ok.pack()
    txt_dic.insert("insert", "路径")
    txt_url.insert("insert", "链接")

    root.mainloop()
    