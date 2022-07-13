import asyncio
import aiohttp
import time



class ImgNameUrl:
    def __init__(self, ImgFileName, ImgDownLoadUrl):
        self.ImgFileName = ImgFileName
        self.ImgDownLoadUrl = ImgDownLoadUrl

async def fetch(session,url):
    async with session.get(url.ImgDownLoadUrl, verify_ssl=False) as response:
        with open(url.ImgFileName, 'ab') as f:
            while True:
                chunk = await response.content.read(1024)
                if not chunk:
                    break
                f.write(chunk)

async def main(urlList):
    async with aiohttp.ClientSession() as session:
        task = [ asyncio.create_task( fetch(session,url)) for url in urlList ]
        done,pending = await asyncio.wait(task)

if __name__ == '__main__':
    # 设置异步任务数
    numbers_of_async = 50
    lastTime = time.time()    
    urlList = []
    img1 = ImgNameUrl(
        "E:\\001.jpg", "https://www.mlito.com/wp-content/uploads/2017/03/21-1.jpg")
    img2 = ImgNameUrl(
        "E:\\002.jpg", "https://www.mlito.com/wp-content/uploads/2017/03/25-1.jpg")
    urlList.append(img1)
    urlList.append(img2)
    numbers_of_times = int(len(urlList)/numbers_of_async) if not len(urlList)%numbers_of_async else int(len(urlList)/numbers_of_async) + 1
    for number in range(numbers_of_times):
        asyncio.run(main(urlList[number*numbers_of_async:number*numbers_of_async+numbers_of_async]))
    print("耗时 %.5f s"%(time.time() - lastTime))