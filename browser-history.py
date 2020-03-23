import os
import json
import sys
import csv
import shutil
import sqlite3
import itertools
import unicodedata

BASE_DIR = os.environ.get('HOME')

platform_table = {
    'linux': '',
    'darwin': {
        'browser': {
            'google_chrome': 'Library/Application Support/Google/Chrome/Default/History',
            'safari': 'Library/Safari/History.db',
            'firefox': 'Library/Application Support/Firefox/Profiles',
        }
    },
    'win32': '',
}


class BrowserHistorySQL:
    google_chrome = """SELECT 
	url, case when title is not null then title else 'not found title' end as title,
	datetime((last_visit_time/1000000)-11644473600, 'unixepoch', 'localtime') as last_visit_time
	FROM urls ORDER BY last_visit_time DESC"""
    firefox = """SELECT 
    	url, case when title is not null then title else 'not found title' end as title, 
        datetime((visit_date/1000000), 'unixepoch', 'localtime') as last_visit_time 
	FROM moz_places as mp INNER JOIN moz_historyvisits as mh on mh.place_id = mp.id 
	ORDER BY last_visit_time DESC"""
    safari = """SELECT 
    	url, case when title is not null then title else 'not found title' end as title, 
        datetime(visit_time + 978307200, 'unixepoch', 'localtime') as last_visit_time
	FROM history_visits hv INNER JOIN history_items hi ON hi.id = hv.history_item 
	ORDER BY last_visit_time DESC"""


class BrowserHistory:
    _History_Data = []

    def generate_history_data(self, browser_name, url, title, date, *args, **kwargs):
        title = unicodedata.normalize('NFKD', title).encode('ascii','ignore')
        self._History_Data.append(
            {
                'url': url,
                'title': title,
                'date': date,
                'browser_name': browser_name
            }
        )

    @staticmethod
    def check_and_generate_path():
        paths = platform_table.get(sys.platform)['browser']
        exists_browser = {}

        for key, value in paths.items():
            path_ = os.path.join(BASE_DIR, value)
            if os.path.exists(path_):
                new_path = '/tmp/{}-{}'.format(key, value.split('/')[-1])
                shutil.copy(path_, new_path)
                exists_browser[key] = new_path
        return exists_browser


    def generate_csv(self):
        exists_browser_history = self.check_and_generate_path()
        for browser_name, file_path in exists_browser_history.items():
            export_file = '/tmp/{}-history.csv'.format(browser_name)
            conn = sqlite3.connect(file_path)
            cur = conn.cursor()
            sql_query = getattr(BrowserHistorySQL, browser_name)
            c = cur.execute(sql_query)

            for item in c.fetchall():
                self.generate_history_data(browser_name, *item)
            with open(export_file, 'wb') as output_file:
                dict_writer = csv.DictWriter(output_file, self._History_Data[0].keys())
                dict_writer.writeheader()
                dict_writer.writerows(self._History_Data)
 