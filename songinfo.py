import urllib.request   #python3
import json

def getSongInfo(url):
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)      #注意：返回字节串而不是字符串
    responseJson = json.loads(response.read().decode("utf-8")) #应用byte的decode方法解码 
    songList = responseJson["song"]
    for s in songList:
        yield s
