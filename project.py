import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup as BS
import json

# 五個社會局 (台北、桃園、台中、台南、高雄)
getAddress = (
    'https://dosw.gov.taipei/News.aspx?n=80C7D4753D325D9A&sms=842A26926D5B58DF&page=1&PageSize=200',
    'https://sab.tycg.gov.tw/home.jsp?id=30522&parentpath=0,30480&page=1&pagesize=29',
    'https://www.society.taichung.gov.tw/13710/13714/13717',
    'http://social.tainan.gov.tw/social/newslist.asp?nsub=__A000',
    'https://socbu.kcg.gov.tw/index.php?html=news_show.php'
)

headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
base_url = ''
writeFiles = []

def insertList(city, title, link, date):
    global writeFiles
    writeFiles.append({
        'location': city,
        'title': "".join(title.split()),
        'link': link,
        'date': date
    })

def getSoup(urlStr):
    global base_url
    response = requests.get(urlStr, headers=headers)
    base_url = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(response.url))
    result = response.content.decode('utf8')
    soup = BS(result, 'lxml')
    return soup

for index,mainLink in enumerate(getAddress):
    soup = getSoup(mainLink)

    if index == 0:
        getData = soup.select('tbody tr')
        city = 'Taipei'
        for text in getData:
            title = text.select('.CCMS_jGridView_td_Class_1')[0].getText()
            link = base_url + text.select('.CCMS_jGridView_td_Class_1 a')[0].get('href')
            date = text.select('.CCMS_jGridView_td_Class_2')[0].getText()
            insertList(city, title, link, date)

    elif index == 1:
        getData = soup.select('#messageform .css_tr.list_list')
        city = 'Taoyuan'
        for text in getData:
            title = text.select('.list_title')[0].getText()
            link = base_url + text.find_all('a')[0].get('href')
            date = text.select('.list_date')[0].getText()
            insertList(city, title, link, date)

    elif index == 2:
        for delElem in soup.select('section.list li .numb'):
            # 刪掉不要的元素
            delElem.decompose()

        getData = soup.select('section.list li')
        city = 'Taichung'

        for text in getData:
            title = text.select('a')[0].getText()
            link = base_url + text.select('a')[0].get('href')
            date = text.select('a span.date')[0].getText()
            insertList(city, title, link, date)

    elif index == 3:
        nextUrl = ''
        nextVal = '下一頁'
        city = 'Tainan'
        while True:
            # 條件若已不是下一頁
            if nextVal != '下一頁':
                break

            if nextUrl != '':
                soup = getSoup(nextUrl)

            getData = soup.select('table.toptable tr')
            # 第一個tr跟最後一個不要
            for text in getData[1:-2]:
                title = text.select('a')[0].getText()
                link = base_url + 'social/' + text.select('a')[0].get('href')
                date = text.select('td:nth-child(1)')[0].getText()
                insertList(city, title, link, date)

            # 抓下一頁
            nextPage = getData[-1].select('a')[-2]
            nextUrl = base_url + 'social/' + nextPage.get('href')
            nextVal = nextPage.getText()

    elif index == 4:
        nextUrl = ''
        nextVal = '下一頁'
        city = 'Kaohsiung'
        while True:
            # 條件若已不是下一頁
            if nextVal != '下一頁':
                break

            if nextUrl != '':
                soup = getSoup(nextUrl)

            getData = soup.select('div.t_list div.row')
            for text in getData:
                title = text.select('div.h_line a')[0].getText()
                link = base_url + 'index.php' + text.select('div.h_line a')[0].get('href')
                date = text.select('div.date')[0].getText()
                insertList(city, title, link, date)

            # 抓下一頁
            nextPage = soup.select('div.page a')[-1]
            nextUrl = base_url + 'index.php' + nextPage.get('href')
            nextVal = nextPage.getText()


print(writeFiles)

with open('socialData.txt', 'w', encoding='utf8') as newFile:
    for d in writeFiles:
        newFile.writelines(f"\"{d['location']}\",\"{d['date']}\",\"{d['title']}\",\"{d['link']}\"\n")
