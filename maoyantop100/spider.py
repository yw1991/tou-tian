import requests

import re
from requests.exceptions import ConnectionError
import json
from multiprocessing import Pool
import pymongo
from config import  *

headers = {
           'cookie': 'uuid=1A6E888B4A4B29B16FBA1299108DBE9CCB7E95989D83F621A85DAF6BDB9CCEB5;'
                     ' _csrf=7ffff1bd9809f52e486b783b4a2ed950487f2e9c40ad6c84c66136fa990c0c5c;'
                     ' _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; '
                     '_lxsdk_cuid=1644be632edc8-0c464bd5fff117-16396952-13c680-1644be632edc8;'
                     ' _lxsdk=1A6E888B4A4B29B16FBA1299108DBE9CCB7E95989D83F621A85DAF6BDB9CCEB5;'
                     ' __mta=153900551.1530281735292.1530281740953.1530282581043.3;'
                     ' _lxsdk_s=1644be632ee-4c8-f29-e2d%7C%7C42',
           'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

client = pymongo.MongoClient(MONGOURL)
db = client[MONGODB]


def get_one_page(url):
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:

            return response.text
        else:
            print("请求失败")
    except ConnectionError:
        return None


def parse_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a'
                         +'.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
                         +'.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>',re.S)

    items = re.findall(pattern,html)
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'star': item[3].strip()[3:],
            'releasetime': item[4].strip()[5:],
            'score': item[5]+item[6]
        }


def save_to_file(content):
    with open('result.txt','a',encoding='utf-8') as f:
        f.write(json.dumps(content,ensure_ascii=False) + '\n')


def save_to_mongo(content):
    try:
        if db[MONGOTABLE].insert(content):
            print("save to mongo",content)
    except Exception:
            print("failed save to mongo", content)


def main(page):
    url = 'https://maoyan.com/board/4?offset=' + str(page)
    html = get_one_page(url)
    for item in parse_page(html):
        print(item)
        save_to_file(item)
        save_to_mongo(item)


if __name__ == '__main__':
    for i in range(1,10):
        main(i)
    # pool = Pool()
    # pool.map(main,[x*10 for x in range(10)])
    # pool.close()
    # pool.join()
