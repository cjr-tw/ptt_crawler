import time
import requests
import json
import re
from bs4 import BeautifulSoup
import os
import urllib.request

MAX_PUSH = 50

def parse(dom):
    soup = BeautifulSoup(dom, 'html.parser')
    links = soup.find(id='main-content').find_all('a')
    img_urls = []
    for link in links:
        if re.match(r'^https?://(i.)?(m.)?imgur.com', link['href']):
            img_urls.append(link['href'])
    return img_urls

def get_web_content(url):
    resp = requests.get(url=url, cookies={'over18': '1'})
    if resp.status_code != 200:
        print('Invalid url: ' + resp.url)
        return None
    else:
        return resp.text

def get_resource(url):
    """ 這個函式負責送出HTTP請求，並可使用自訂標頭、內容的分級的Cookie以及傳遞URL網址的參數
    Args:
        url ( example. https://www.ptt.cc/bbs/Beauty/index.html )
    """
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" 
                             "AppleWebKit/537.36 (KHTML, like Gecko)"
                             "Chrome/63.0.3239.132 Safari/537.36"}

    return requests.get(url,headers=headers,cookies={"over18":"1"}) #


def parse_html(r):
    """ 使用BeautifulSoup來剖析HTML網頁的資料，宣告 parse_html()函數負責判斷請求的Response是否成功 ，
        指定utf-8編碼，並回傳BeautifulSoup物件
    Args:
        r ( Get this http status and encoding )
    Return:
        soup ( this http )
    """
    if r.status_code == requests.codes.ok: # 如果狀態碼為200 OK
        r.encoding ="utf-8"
        soup = BeautifulSoup(r.text,"lxml")
    else:
        print("HTTP請求錯誤")
        soup = None

    return soup

def get_articles(soup, date):
    """ 取得文章清單的資料，並找出上一頁的URL網址
    Args:
       date ( 今天的日期 ）
       soup ( 此版面轉出來的源碼 )
    Return:
       articles ( 取得到的文章 ）
       prev_url ( 上一頁的網址 ）
    """

    articles = []
    # 取得上一頁的超連結
    paging_div = soup.find("div", class_="btn-group btn-group-paging")
    paging_a = paging_div.find_all("a", class_="btn")
    prev_url = paging_a[1]["href"]
    # 取得文章清單
    tag_divs = soup.find_all("div", class_="r-ent")
    # 逐一取出每一篇文章的<div>標籤
    for tag in tag_divs:
        # 判斷文章的日期
        if tag.find("div",class_="date").text.strip() == date:
             push_count = 0 # 取得推文數
             push_str = tag.find("div", class_="nrec").text
             if push_str:
                try:
                    push_count = int(push_str) # 轉換成數􏰀
                    # 只限當天
                except ValueError: # 轉換失敗，可能是'爆'或 'X1','X2' #
                 if push_str == '爆':
                    push_count = 99
                 elif push_str.startswith('X'):
                    push_count = -10
                # 取得貼章的超連結和標題文􏰀
                if tag.find("a"): # 有超連結，表示文章􏰁在
                    href = tag.find("a")["href"]
                    title = tag.find("a").text
                    author = tag.find("div", class_="author").string
                    articles.append({
                    "title": title,
                    "href": href,
                    "push_count": push_count,
                    "author": author
                    })

    return articles, prev_url



def web_scraping_bot(url):
    """ 建立爬蟲函數進行文章的資料擷取 """

    articles =[]
    print("抓取網路資料中...")
    soup = parse_html(get_resource(url))
    if soup :
        # 取得今天日期,去掉開頭'0'符合PPT的日期格式
        today = time.strftime("%m/%d").lstrip('0')
        # 取得目前頁面的今日文章清單
        current_articles,prev_url = get_articles(soup,today)
        # 取得前一頁文章，直到沒有今天的文章為止
        while current_articles :
            articles += current_articles
            print("等待2秒鐘..")
            # time.sleep(2)
            # 剖析上一頁繼續尋找是否有今日的文章
            soup = parse_html(get_resource( URL + prev_url) )
            current_articles, prev_url = get_articles(soup, today)
    return articles


def save_to_json( articles, file):
    """ articles to JSON
    Args:
        articles( a list )
        file ( output )
    """
    # print("今天總共有: " + str(len(articles)) + " 篇文章")
    # threshold = MAX_PUSH
    # print("熱門文章(> %d 推): " % (threshold))
    #for item in articles: # 顯示熱門文章清單
        # if int(item["push_count"]) > threshold: print(item["title"], item["href"], item["author"])
    #寫入JSON檔案
    with open(file, "w", encoding="utf-8") as fp:
        json.dump(articles,fp,indent=2,sort_keys=True,ensure_ascii=False)



def printList(list_):
    """ Print all articles """
    for i,item in enumerate(list_):
        title = item.get('title', '')
        href = item.get('href', '')
        push_count = item.get('push_count', '')
        author= item.get('author', '')
        print('標題: {}\n網址: {}\n推數: {}\n作者: {}'.format(title,
                                              href, push_count, author))
        print()


def printTop3( list_) :
    """ 印出所有文章推數最高的前三名 """
    if len(SortedData) > 3:
        for i in range(0,3):
            title = SortedData[i].get('title', '')
            href = SortedData[i].get('href', '')
            push_count = SortedData[i].get('push_count', '')
            author= SortedData[i].get('author', '')
            print('熱度排行: {}\n標題: {}\n網址: {}\n推數: {}\n作者: {}'.format(i+1,title,
                                                                href, push_count, author))
            print()
    else :
        print("!!!本日" + TOPIC + "版發布的新貼文還未超過3篇哦!!!")


def save(img_urls, title):
    if img_urls:
        try:
            folder_name = title.strip()
            os.makedirs(folder_name)
            for img_url in img_urls:
                # e.g. 'http://imgur.com/9487qqq.jpg'.split('//') -> ['http:', 'imgur.com/9487qqq.jpg']
                if img_url.split('//')[1].startswith('m.'):
                    img_url = img_url.replace('//m.', '//i.')
                if not img_url.split('//')[1].startswith('i.'):
                    img_url = img_url.split('//')[0] + '//i.' + img_url.split('//')[1]
                if not img_url.endswith('.jpg'):
                    img_url += '.jpg'
                file_name = img_url.split('/')[-1]
                urllib.request.urlretrieve(img_url, os.path.join(folder_name, file_name))
        except Exception as e:
            print(e)


TOPIC = "Beauty"
URL = "https://www.ptt.cc"
url = URL + "/bbs/" + TOPIC + "/index.html"



if __name__ == '__main__':
    today = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(url)
    # 擷取文章資料
    articles = web_scraping_bot(url)

    # 排序得到的資料
    SortedData = sorted(articles,key=lambda key:key['push_count'],reverse=True)
    total = 0

    # 顯示擷取到的文章清單
    for item in articles:
        total = total + 1
        # print(item)
    # 將資料儲􏰁成JSON檔案
    print( "資料轉存為JSON檔案" )
    save_to_json(SortedData, "articles.json")
    # printList(SortedData)
    print('=============='+today+'=================')
    print('\t\t\t'+ TOPIC + '版本日共有' + str(total) + '篇新文章')
    print('=======================TOP3=======================')
    printTop3(SortedData)

    for article in articles:
        print('Collecting beauty from:', article)
        page = get_web_content( URL + article['href'])
        if page:
            img_urls = parse(page)
            save(img_urls, article['title'])
            article['num_image'] = len(img_urls)











