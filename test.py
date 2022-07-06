import requests
url="https://www.kanjiantu.com/images/2021/05/14/7FWuf.jpg"
try:
    resp=requests.get(url)
except Exception as e:
    print (e)