import os
import sqlite3

from browser_history import ChromeHistory
from news_sites import all_news_sites

current = os.path.dirname(os.path.realpath(__file__))

def news_record(href, title, last_visited, created):
    return {'href': href, 'title': title, 'last_visited': last_visited, 'created': created}

def record_from_browser_history(brower_history):
    visited_news = []
    for record in brower_history.get_records():
        for news_site in all_news_sites:
            if news_site.is_news_page(record.url):
                title = news_site.clean_title(record.title, record.url)
                visited_news.append(news_record(record.url, title, record.timestamp, record.timestamp))
                break

    return visited_news

class LocalStorage(object):
    def __init__(self, db_name, table_name):
        self.db_name = db_name
        self.table_name = table_name

        self.insert_query = f'''INSERT OR IGNORE INTO {self.table_name} (href, title, last_visited) VALUES (:href, :title, :last_visited)'''
        self.update_query = f'''INSERT OR REPLACE INTO {self.table_name} (ID, href, title, last_visited) values (
                                (select ID from news_record where href=:href), :href, :title, :last_visited)'''
    
    def _get_sqlite_conn(self):
        cnx = sqlite3.connect(os.path.join(current, self.db_name))
        return cnx, cnx.cursor()

    def init_db(self):
        cnx, cursor = self._get_sqlite_conn()

        try:
            create_table_query = f'''CREATE TABLE IF NOT EXISTS {self.table_name} (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                href text UNIQUE,
                title text,
                last_visited INTEGER DEFAULT 0,
                created INTEGER DEFAULT 0)'''

            cursor.execute(create_table_query)
            cnx.commit()
        finally:
            cnx.close()
    
    def import_from_browser_history(self):
        print('importing news from history...')
        browers = [ChromeHistory()]
        for browser in browers:
            try:
                records = record_from_browser_history(browser)
                self.save(records, ignore_if_exists = False)
            except sqlite3.OperationalError:
                print('Cannot ')
    
    def import_from_backup(self, backup_db):
        print('importing news from backup...')
        cnx = sqlite3.connect(backup_db)
        cursor = cnx.cursor()

        query_str = f"SELECT href, title FROM news WHERE read = 0"
        cursor.execute(query_str)

        unvisited_news = []
        for url, title in cursor.fetchall():
            unvisited_news.append(news_record(url, title, 0, 0))
        print('unvisited pages', len(unvisited_news))

        self.save(unvisited_news, ignore_if_exists = True)

    def save(self, news_infos, ignore_if_exists):
        if ignore_if_exists == 1:
            query_str = self.insert_query
        else:
            query_str = self.update_query
        
        cnx, cursor = self._get_sqlite_conn()

        try:
            cursor.executemany(query_str, news_infos)
            cnx.commit()
        finally:
            cnx.close()
    
    def retrieve(self, visited = None, topk = 500):
        rows = []
        cnx, cursor = self._get_sqlite_conn()
        try:
            if visited is None or visited:
                query_str = f"SELECT href, title, last_visited, created FROM {self.table_name} WHERE last_visited > 0 LIMIT {topk}"
                cursor.execute(query_str)
                rows = cursor.fetchall()

            if visited is None or not visited:
                query_str = f"SELECT href, title, last_visited, createdFROM {self.table_name} WHERE last_visited = 0 LIMIT {topk}"
                cursor.execute(query_str)
                rows.extend(rows)

            ret = []
            for row in rows:
                ret.append(news_record(row[0], row[1], row[2], row[3]))

            return ret
        finally:
            cnx.close()
    
    def get_unvisited(self, site, topk = 100):
        ret = []
        cnx, cursor = self._get_sqlite_conn()
        try:
            query_str = f'''SELECT ID, href, title, created FROM {self.table_name}
            WHERE last_visited = 0 AND href like \'%{site}%\' ORDER BY ID DESC LIMIT {topk}'''

            print('sqlite query:' + query_str)
            cursor.execute(query_str)
            for id, href, title, created in cursor.fetchall():
                ret.append(news_record(href, title, 0, created))

            return ret
        finally:
            cnx.close()
    
    def count_pages(self):
        cnx, cursor = self._get_sqlite_conn()
        try:
            query_str = f"SELECT COUNT(*) FROM {self.table_name} WHERE last_visited > 0"
            cursor.execute(query_str)

            visited = cursor.fetchone()[0]

            query_str = f"SELECT COUNT(*) FROM {self.table_name} WHERE last_visited = 0"
            cursor.execute(query_str)
            unvisited = cursor.fetchone()[0]

            return visited, unvisited
        finally:
            cnx.close()
    
    def print_head(self, entries = 10):
        records = self.retrieve()
        if entries >= 0:
            print(records[0:entries])
        else:
            print(records[entries:])

if __name__ == '__main__':
    pass