import requests
import MySQLdb
import time
import os
import re

URL_BOOK = 'http://openlibrary.org/search.json?title={0}&author={1}'
URL_COVER = 'http://covers.openlibrary.org/b/id/{0}-L.jpg'

conn = MySQLdb.connect(host = 'localhost', 
                       db = 'dadsbooks',
                       user = 'root', 
                       passwd = '', 
                       charset = "utf8", 
                       use_unicode = True)

cursor = conn.cursor()
q = "select id_book, json from reviews where id_book in (select id from books where cover = '') and json like '%cover_i%';"
cursor.execute(q)
sin_cover = 0

for book_id, json in cursor.fetchall():
    book = cursor.fetchone()
    m = re.match(".*'cover_i': (\d+),", json)
    try:
        cover = m.group(1)
        print 'COVER', cover
        filepath = 'covers/{0}.jpg'.format(cover)
        if not os.path.exists(filepath):
            print 'Buscando y guardando cover'
            url_cover = URL_COVER.format(cover)
            r = requests.get(url_cover)
            cover_f = open(filepath, 'w')
            cover_f.write(r.content)
            cover_f.close()
        else:
            print 'Existe cover'

        print 'Actualizando Libro', book_id
        q = 'UPDATE books SET cover = %s WHERE id = %s '
        cursor.execute(q, (cover, book_id))

        conn.commit()
        print 'COMMIT'
    except:
        sin_cover += 1

    time.sleep(2)

print "Sin Cover:",sin_cover
cursor.close()
conn.close()
