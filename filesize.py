from email.iterators import body_line_iterator
from operator import mod
from pymouse import PyMouse
import schedule
import time
import requests
import os
from PIL import Image
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44",
    "Content-Type": "text/html;charset=UTF-8"}
proxy = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
def download():
    usrl="https://i.ibb.co/FmB82GV/Nan-Catch-Me-plz-1.jpg"
    res = requests.get(usrl, headers=headers, proxies=proxy)
    with open("D:\\ff.jpg", 'wb')as f:
        f.write(res.content)
def checkImgSize():
    file_handle=open('D:\\filesize.txt',mode='a+',encoding='utf-8')
    dic="H:\\folder\\hotgirl\\"
    dirs=os.listdir(dic)
    imgindex=1
    for dir in dirs:
        imgfolder = dic+dir
        files=os.listdir(imgfolder)
        for file in files:
            # if(imgindex<1060000):
            #     imgindex+=1
            #     continue           
            filename=imgfolder+"\\"+file
            if(os.path.splitext(filename)[-1] == ".mp4"):
                imgindex += 1
                continue
            try:
                imgsize=Image.open(filename).size
            except:
                imgsize="Wrong File"
                imgindex+=1
                continue
            if(imgindex%10000==0):
                print("【{}】{}_{}".format(imgindex, filename, imgsize))
            if(int(imgsize[0]) == 180 and int(imgsize[1]) == 180):
                file_handle.write("【{}】{}_{}\n".format(imgindex, filename, imgsize))
            imgindex+=1
    file_handle.close()
    print("Done")


def checkImgSize1():
    file_handle = open('E:\\filesize1.txt', mode='a+', encoding='utf-8')
    f = open("E:\\filesize.txt", encoding='utf-8')
    files = f.readlines()
    f.close()
    imgindex = 1
    for filename in files:
        filename=filename.strip()
        if(os.path.splitext(filename)[-1] == ".mp4"):
            imgindex += 1
            continue
        try:
            imgsize = Image.open(filename).size
        except:
            imgsize = "Wrong File"
            imgindex += 1
            continue
        print("【{}】{}_{}".format(imgindex, filename, imgsize))
            
        if(int(imgsize[0]) == 180 and int(imgsize[1]) == 180):
            file_handle.write("【{}】{}_{}\n".format(
                imgindex, filename, imgsize))
        imgindex += 1

    file_handle.close()
checkImgSize1()
