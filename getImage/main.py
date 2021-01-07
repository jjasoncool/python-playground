import MySQLdb
import time
import mimetypes
import requests
import os

# 資料庫連線
savePath = os.path.dirname(os.path.realpath(__file__)) + "/images"
db = MySQLdb.connect(host="192.168.55.200", user="jason",
                    passwd="123456", db="dcs", charset='utf8')
# 使用 cursor 物件
c = db.cursor()
# SQL Query 字串
dbQuery = """
    SELECT * FROM dcs.files WHERE path like 'https://lh3.googleusercontent.com/%'
"""
# 執行查詢，並將查詢結果存入 result
c.execute(dbQuery)
result = c.fetchall()
# 取得連結網址
allFiles = {}
for row in result:
    allFiles[row[0]] = row[7]

for index, rowid in enumerate(allFiles):
    print(rowid)
    print(allFiles[rowid])
    # 利用 request 抓取檔案，並從 header 判斷附檔名
    response = requests.get(allFiles[rowid])
    content_type = response.headers['content-type']
    extension = mimetypes.guess_extension(content_type)
    # 不知道為什麼 linux 判斷 jpeg 副檔名變成 jpe
    if extension == '.jpe':
        extension = '.jpeg'
    # 要存的檔案名稱
    filename = str(rowid) + extension
    if not os.path.exists(savePath):
        os.makedirs(savePath)

    with open(savePath + '/' + filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            # If you have chunk encoded response uncomment if
            # and set chunk_size parameter to None.
            #if chunk:
            file.write(chunk)
    time.sleep(2)
