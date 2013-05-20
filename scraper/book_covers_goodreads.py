import time
import os
import re
import json
import xml.etree.ElementTree as ET
import MySQLdb
import requests

URL_OPENLIBRARY = u'http://openlibrary.org/search.json?title={0}&author={1}'
URL_GOODREADS = u'http://www.goodreads.com/search.xml?key=hfsPBv7aPkMbVJEjrpnA9A&q={0}'

conn = MySQLdb.connect(host = 'localhost', 
                       db = 'books_reviews',
                       user = '', 
                       passwd = '', 
                       charset = "utf8", 
                       use_unicode = True)

cursor = conn.cursor()
q = "select id, author, title from books where cover = '';"
cursor.execute(q)

for book_id, book_author, book_title in cursor.fetchall():
    url_openlibrary = URL_OPENLIBRARY.format(book_title, book_author)
    r = requests.get(url_openlibrary)
    print 'Libro OpenLibrary:', url_openlibrary
    try:
        book_json = r.json()
    except:
        print 'No se encontro'
        continue
    docs = book_json['docs']
    if not docs or not docs[0].has_key('isbn'):
        print 'No se encontro libro'
        continue
    isbns = docs[0]['isbn']
    for isbn in isbns:
        print 'Book: ', book_id, 'ISBN: ', isbn
        url_goodreads = URL_GOODREADS.format(isbn)
        time.sleep(1)
        r = requests.get(url_goodreads)
        print url_goodreads
        book_xml_str = r.content
        try:
            book_xml = ET.fromstring(book_xml_str)
            url_cover = book_xml.find('search').find('results').find('work').find('best_book').find('image_url').text
        except:
            print 'No se encontro el Libro'
            continue

        if 'nocover/111x148.png' in url_cover:
            print' No existe cover'
            continue

        print 'Titulo:', book_title, 'Cover:', url_cover
        cover = 'goodread_' + url_cover.split('/')[-1]
        filepath = 'covers/{0}.jpg'.format(cover)
        if not os.path.exists(filepath):
            r = requests.get(url_cover)
            cover_f = open(filepath, 'w')
            cover_f.write(r.content)
            cover_f.close()

        print 'Book:', book_id, 'Updating'
        q = 'UPDATE books SET cover = %s WHERE id = %s '
        cursor.execute(q, (cover, book_id))
        conn.commit()
        print 'Book:', book_id, 'Saved'
        break;
