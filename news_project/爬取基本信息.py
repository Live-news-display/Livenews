import requests
import hashlib
import redis
import sys

r = redis.Redis(host='localhost', port=6379, db=0)


def get_html():
    html = requests.get(
        'http://v.juhe.cn/toutiao/index?type=top&key=b23af4184e98f0c2f600d159abb556fa',
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.7 Safari/537.36'
        }).json()
    return html


def md5_url(url):
    m = hashlib.md5()
    m.update(url.encode())
    return m.hexdigest()


html = get_html()
for item in html['result']['data']:
    if item['url'][-4:] != 'html':
        continue
    url = item['url'].replace('\\', '').split('%')[-1][0:-5][2:]
    final_url = 'https://mini.eastday.com/a/{}.html'.format(url)
    url_after = md5_url(final_url)
    if r.sadd('news:spider', url_after) == 1:
        result = {
            'title': item['title'],
            'time': item['date'],
            'publisher': item['author_name'],
            'url': final_url
        }
        print(result)
    else:
        sys.exit('更新完成')
