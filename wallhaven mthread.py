from __future__ import annotations
from retry import retry
import signal
import multitasking
from asyncio import futures
import os
import requests
import time
import math
from tqdm import tqdm, trange

picurl = "https://w.wallhaven.cc/full/{0}/wallhaven-{1}.jpg"
RETRYTIME = 0
count = 0
total = len(open("E:\\wallhaven_sfw\\wallhaven_sfw.txt", 'r').readlines())
ff = open('E:\\wallhaven_sfw\\wallhaven_sfw.txt', "r", encoding='utf-8')

RETRYTIME = 0

# 用于多线程操作
# 导入 retry 库以方便进行下载出错重试
signal.signal(signal.SIGINT, multitasking.killall)

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}
# 定义 1 MB 多少为 B
MB = 1024**2


def split(start: int, end: int, step: int) -> list[tuple[int, int]]:
    # 分多块
    parts = [(start, min(start+step, end))
             for start in range(0, end, step)]
    return parts


def get_file_size(url: str, raise_error: bool = False) -> int:
    '''
    获取文件大小

    Parameters
    ----------
    url : 文件直链
    raise_error : 如果无法获取文件大小，是否引发错误

    Return
    ------
    文件大小（B为单位）
    如果不支持则会报错

    '''
    response = requests.head(url)
    file_size = response.headers.get('Content-Length')
    if file_size is None:
        if raise_error is True:
            raise ValueError('该文件不支持多线程分段下载！')
        return file_size
    return int(file_size)


def download(url: str, file_name: str, retry_times: int = 3, each_size=10*MB) -> None:
    '''
    根据文件直链和文件名下载文件

    Parameters
    ----------
    url : 文件直链
    file_name : 文件名
    retry_times: 可选的，每次连接失败重试次数
    Return
    ------
    None

    '''
    global RETRYTIME
    try:        
        head=requests.head(url,headers=headers)
        if(head.status_code==404):
            url=url.replace(".jpg",".png")
            file_name = file_name.replace(".jpg", ".png")
            head=requests.head(url,headers=headers)
            if(head.status_code==404):
                return "已删除"

        f = open(file_name, 'wb')
        file_size = get_file_size(url)

        @retry(tries=retry_times)
        @multitasking.task
        def start_download(start: int, end: int) -> None:
            '''
            根据文件起止位置下载文件

            Parameters
            ----------
            start : 开始位置
            end : 结束位置
            '''
            _headers = headers.copy()
            # 分段下载的核心
            _headers['Range'] = f'bytes={start}-{end}'
            # 发起请求并获取响应（流式）
            response = session.get(url, headers=_headers, stream=True)
            # 每次读取的流式响应大小
            chunk_size = 128
            # 暂存已获取的响应，后续循环写入
            chunks = []
            for chunk in response.iter_content(chunk_size=chunk_size):
                # 暂存获取的响应
                chunks.append(chunk)
                # 更新进度条
                bar.update(chunk_size)
            f.seek(start)
            for chunk in chunks:
                f.write(chunk)
            # 释放已写入的资源
            del chunks

        session = requests.Session()
        # 分块文件如果比文件大，就取文件大小为分块大小
        each_size = min(each_size, file_size)

        # 分块
        parts = split(0, file_size, each_size)
        print(f'分块数：{len(parts)}')
        # 创建进度条
        bar = tqdm(total=file_size, desc=f'下载文件：{file_name}')
        for part in parts:
            start, end = part
            start_download(start, end)
        # 等待全部线程结束
        multitasking.wait_for_tasks()
        f.close()
        bar.close()
    except:
        if(RETRYTIME == 10):
            RETRYTIME = 0
            return "no"
        RETRYTIME += 1
        time.sleep(20)
        download(url, file_name)       
def downloadpic(fname,furl):
    global RETRYTIME
    try:
        RETRYTIME=0
        res = requests.get(furl)
        with open(fname, 'wb')as f:
            f.write(res.content)
        if(os.path.getsize(fname) < 1000):
            os.remove(fname)
            furl = furl.replace(".jpg", ".png")
            fname = fname.replace(".jpg", ".png")        
            res = requests.get(furl)
            with open(fname, 'wb') as pf:
                pf.write(res.content)
        return furl
    except:
        if(RETRYTIME==10):
            RETRYTIME=0
            return "no"
        RETRYTIME+=1
        time.sleep(20)
        downloadpic(fname,furl)
        return furl+"下载失败"


for line in ff:
    count=count+1
    imgurl = line.strip().split("_")[0]
    favcount = line.strip().split("_")[1]
    pid = imgurl.strip().split("/")[4]   
    url = picurl.format(pid[:2],pid)
    fname=os.path.basename(url)
    if(int(favcount) > 100):
        max_i = math.ceil(int(favcount)/100)*100
        min_i = max_i-100
    else:
        max_i = math.ceil(int(favcount)/10)*10
        min_i = max_i-10
    subdic = "E:\\wallhaven_sfw\\"+"{}-{}".format(min_i, max_i)
    if(not os.path.exists(subdic)):
        os.mkdir(subdic)
    fullname = subdic+"\\"+fname
    if(os.path.exists(fullname) and os.path.getsize(fullname)>30):
        print("【{}/{}】{}已下载".format(count, total, url))
        continue
    if(os.path.exists(fullname.replace(".jpg", ".png")) and os.path.getsize(fullname.replace(".jpg", ".png")) > 30):
        print("【{}/{}】{}已下载".format(count, total, url.replace(".jpg", ".png")))
        continue
    ##download
    msg = download(url,fullname)
    print("【{}/{}】{}下载成功".format(count, total,"{}-{}".format(min_i,max_i)))
    ##time.sleep(0.5)  