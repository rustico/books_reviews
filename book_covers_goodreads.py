import time
import os
import re
import json
import xml.etree.ElementTree as ET
import MySQLdb
import requests

URL_COVER = 'http://www.goodreads.com/search.xml?key=hfsPBv7aPkMbVJEjrpnA9Aq={0}'

conn = MySQLdb.connect(host = 'localhost', 
                       db = 'books_reviews',
                       user = 'root', 
                       passwd = 'nicolas1983', 
                       charset = "utf8", 
                       use_unicode = True)

cursor = conn.cursor()
q = "select id_book, json from reviews where id_book in (select id from books where cover = '');"
cursor.execute(q)

for book_id, book_json_str in cursor.fetchall():
    book_json = json.loads(book_json_str)
    isbns = book_json['docs'][0]['isbn']
    for isbn in isbns:
        print isbn
        url_cover = URL_COVER.format(isbn)
        r = requests.get(url_cover)
        book_xml = ET.fromstring(r.content)
        image = book.xml.find('image_url')
        print image.text
        break
    break
