
from urllib import request

headers = {'User-Agent': 'Mozilla/5.0 3578.98 Safari/537.36'}
url = request.Request(
    "https://frpic.xyz/i/2021/11/07/11d9byl.jpg", headers=headers)
with request.urlopen(url) as file:
    print(file.status)
    print(file.reason)
