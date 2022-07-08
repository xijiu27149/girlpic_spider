import requests

try:
    resp=requests.get('https://frpic.xyz/i/2021/11/07/11d8mm9.jpg')
except Exception as e:
    print(e)
