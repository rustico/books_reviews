import csv
import requests
import MySQLdb
import time
import os

URL_BOOK = 'http://openlibrary.org/search.json?title={0}&author={1}'
URL_COVER = 'http://covers.openlibrary.org/b/id/{0}-L.jpg'

conn = MySQLdb.connect(host = 'localhost', 
                       db = 'dadsbooks',
                       user = 'root', 
                       passwd = 'nicolas1983', 
                       charset = "utf8", 
                       use_unicode = True)

cursor = conn.cursor()

with open('books.csv', 'r') as b:
    with open('error', 'a') as e:
        with open('not_found', 'a') as n:
            books = csv.reader(b, delimiter=',', quotechar='"')
            for book in books:
                csv = ';'.join(book) + '\n\r'

                # Check if it's ok 
                if len(book) != 4 or not book[3]:
                    e.write(csv)
                    continue

                title = book[0]
                author = book[1]
                url_book = URL_BOOK.format(title, author)
                print 'Buscando el libro...'
                print url_book
                r = requests.get(url_book)
                try:
                    json = r.json()
                except:
                    print 'No se encontro'
                    n.write(';'.join(book) + ';' + url_book + '\n\r')
                    continue

                if not len(json['docs']):
                    print 'No se encontro'
                    n.write(';'.join(book) + ';' + url_book + '\n\r')
                    continue

                print 'Se encontro'
                doc = json['docs'][0]

                # COVER
                print 'COVER'
                cover = ''
                if doc.has_key('cover_i'):
                    print 'Tiene cover'
                    cover = doc['cover_i']
                    filepath = 'covers/{0}.jpg'.format(cover)
                    if not os.path.exists(filepath):
                        print 'Buscando y guardando cover'
                        url_cover = URL_COVER.format(cover)
                        r = requests.get(url_cover)
                        cover_f = open(filepath, 'w')
                        cover_f.write(r.content)
                        cover_f.close()

                # BOOK
                print 'BOOK'
                if doc.has_key('author_name') and len(doc['author_name']):
                    author = doc['author_name'][0]

                publish_year = 0
                if doc.has_key('publish_year') and len(doc['publish_year']):
                    publish_year = doc['publish_year'][0]

                title = doc['title_suggest']
                q = 'INSERT INTO books (author, title, publish_year, cover) VALUES (%s, %s, %s, %s)'
                cursor.execute(q, (author, title, publish_year, cover))
                book_id = cursor.lastrowid
                print 'Se guardo el libro ', book_id

                # SUBJECTS
                print 'SUBJECT'
                if doc.has_key('subject'):
                    for subject in doc['subject']:
                        print subject
                        subject = subject.strip().lower()
                        q = 'SELECT id FROM subjects WHERE title = %s'
                        cursor.execute(q, subject)
                        response = cursor.fetchone()
                        if response:
                            print 'Ya existia el subject'
                            subject_id = response[0]
                        else:
                            q = 'INSERT INTO subjects (title) VALUES (%s)'
                            cursor.execute(q, subject)
                            subject_id = cursor.lastrowid
                            print 'Nuevo Subject ', subject_id

                        # SUBJECTS & BOOKS
                        q = 'INSERT INTO books_subjects (id_book, id_subject) VALUES (%s, %s)'
                        cursor.execute(q, (book_id, subject_id))
                        print 'Guardamos Subjects - Libros'

                # REVIEW
                print 'REVIEW'
                date = book[2].split('--')[0].split('/')
                if len(date) > 1:
                    prefix = '20' if date[1][0] in '01' else '19'
                    date[1] = prefix + date[1]
                    date = "{0}-{1}-01".format(date[1], date[0])
                else:
                    date = ''

                q = 'INSERT INTO reviews (id_book, rating, date, json, csv) VALUES (%s, %s, %s, %s, %s)'
                cursor.execute(q, (book_id, book[3], date, json.__str__(), csv))
                print 'Guardamos Review'

                conn.commit()
                print 'COMMIT'
                time.sleep(2)

cursor.close()
conn.close()
