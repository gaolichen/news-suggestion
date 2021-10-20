import os
import sqlite3
import unicodedata
from shutil import copyfile
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from urllib.parse import unquote, urlparse

@dataclass
class HistoryRecord(object):
    url: str
    title: str
    timestamp: int

    def __str__(self):
        return f'({self.url}, {self.title}, {datetime.fromtimestamp(self.timestamp)})'
    
    def __repr__(self):
        return self.__str__()

def normalize_url(url):
    parts = urlparse(url)
    url = f'{parts.scheme}://{parts.netloc}{parts.path}'
    return unquote(url)

class ChromeHistory(object):
    def __init__(self):
        self.history_path = '\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History'
        self.name = 'chrome'
    
    @staticmethod
    def _to_python_timestamp(ts):
        return ts//1000000-11644473600
    
    @staticmethod
    def _to_sqlite_timestamp(ts):
        return (ts+11644473600) * 1000000
    
    def get_records(self, since = None):
        # copy history file to temp directory.
        temp_path = os.path.join(os.environ.get('TEMP'), self.name + '_history')

        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        src_path = str(Path.home()) + self.history_path

        copyfile(src_path, temp_path)
        con = sqlite3.connect(temp_path)
        cursor = con.cursor()
        ts = self._to_sqlite_timestamp(int(since.timestamp())) if since is not None else 0 
        query = "SELECT url, title, last_visit_time FROM urls where urls.last_visit_time > " + str(ts)
        try:
            cursor.execute(query)
            records = [HistoryRecord(url = normalize_url(url),
                    title = unicodedata.normalize('NFKC', title),
                    timestamp = self._to_python_timestamp(timestamp)) \
                for url, title, timestamp in cursor.fetchall()]
            return records
        finally:
            con.close()

class EdgeHistory(ChromeHistory):
    def __init__(self):
        self.history_path = '\\AppData\\Local\\Microsoft\Edge\\User Data\\Default\\History'
        self.name = 'edge'

if __name__ == '__main__':
    history = EdgeHistory()
    ts = datetime(2021, 10, 1, 0, 0)
    print(ts)
    records = history.get_records(since = ts)
    print(len(records))
    print(records[0:6])