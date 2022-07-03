import requests
from lxml import etree
import os
import zipfile
import time
import operator

filedic = "H:\\folder\\asiantolick\\{}\\"
#filedic="/Volumes/ExtremePro/folder/asiantolick/{}/"
url="https://asiantolick.com/ajax/buscar_posts.php?index={}"
download = "https://asiantolick.com/ajax/download_post.php?ver=1&dir={}&post_id={}&post_name={}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type": "text/html;charset=UTF-8"}
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}


def downloadfile(fname, furl):
    try:
        if(not os.path.exists(fname)):
            res = requests.get(furl, headers=headers, proxies=proxy)
            with open(fname, 'wb')as f:
                f.write(res.content)
        myzip=zipfile.ZipFile(fname)     
        myzip.extractall(os.path.dirname(fname))
        os.remove(fname)
        return furl
    except:
        return furl+"下载失败"

for i in range(38,39):
    starturl=url.format(i)
    resp = requests.get(starturl, headers=headers, proxies=proxy)
    html = etree.HTML(resp.text)
    items=html.xpath('//a[@class="miniatura"]')
    for item in items:
        title=item.xpath('div[4]/span/text()')[0]
      
        title = title.replace(":", "")
        picpath = filedic.format(title)       
        if(not os.path.exists(picpath)):
            os.makedirs(picpath)
        suburl=item.xpath('@href')[0]
        subresp=requests.get(url=suburl,headers=headers,proxies=proxy)
        subhtml = etree.HTML(subresp.text)
        downurl = subhtml.xpath('//a[@class="download_post"]')[0].xpath('@href')[0]
        downresp = requests.get(
            url=downurl, headers=headers, proxies=proxy, verify=False)
        downhtml=etree.HTML(downresp.text)
        postid = downhtml.xpath('//*[@id="download_post"]/@post_id')[0]
        dir = downhtml.xpath('//*[@id="download_post"]/@dir')[0]
        postname = downhtml.xpath('//*[@id="download_post"]/@post_name')[0]
        download_request=download.format(dir,postid,postname)
        filepath=requests.get(url= download_request,headers=headers,proxies=proxy).text
        fullfilename = "{}{}".format(picpath, os.path.basename(filepath))
        if(not os.path.exists(fullfilename)):
            downloadfile(fullfilename, filepath)
        print("page:{}_{}下载完成".format(i,title))
        time.sleep(5)
print("Done")