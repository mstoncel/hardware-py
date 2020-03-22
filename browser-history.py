import os
import json
import sys
import csv
import shutil
import sqlite3
import itertools
import unicodedata


platform_table = {
    'linux': 0,
    'linux2': 0,
    'darwin': {
        'browser': {
            'google_chrome': '/tmp/chrome-history-db',
            #'safari': '~/Library/Safari/History.db',
            #'firefox': '~/Library/Application Support/Firefox/Profiles',
            #'opera': ''
        }
    },
    'cygwin': 2,
    'win32': 2,
}


class BrowserHistorySQL:
    google_chrome = """SELECT 
	url, title,
	datetime((last_visit_time/1000000)-11644473600, 'unixepoch', 'localtime') as last_visit_time
	FROM urls ORDER BY last_visit_time DESC"""
    firefox = """SELECT 
    	url, title, datetime((visit_date/1000000), 'unixepoch', 'localtime') as last_visit_time 
	FROM moz_places as mp INNER JOIN moz_historyvisits as mh on mh.place_id = mp.id 
	ORDER BY last_visit_time DESC"""
    safari = """SELECT 
    	url, title, datetime(visit_time + 978307200, 'unixepoch', 'localtime') as last_visit_time
	FROM history_visits hv INNER JOIN history_items hi ON hi.id = hv.history_item 
	ORDER BY last_visit_time DESC"""


class BrowserHistory:
    _History_Data = []

    def generate_dict(self, browser_name, url, title, date, *args, **kwargs):
        title = unicodedata.normalize('NFKD', title).encode('ascii','ignore')
        self._History_Data.append(
            {
                'url': url,
                'title': title,
                'date': date,
                'browser_name': browser_name
            }
        )

    def generate_csv(self):
        shutil.copyfile(
            '~/Library/Application Support/Google/Chrome/Default/History',
            '/tmp/chrome-history-db'
        )
        paths = platform_table.get(sys.platform)['browser']
        exists_browser_history = {key: value for key,
                                  value in paths.items() if os.path.exists(value)}

        for browser_name, file_path in exists_browser_history.items():
            export_file = '/tmp/{}-history.csv'.format(browser_name)
            conn = sqlite3.connect(file_path)
            cur = conn.cursor()
            sql_query = getattr(BrowserHistorySQL, browser_name)
            c = cur.execute(sql_query)

            for item in c.fetchall():
                self.generate_dict(browser_name, *item)
            with open(export_file, 'wb') as output_file:
                dict_writer = csv.DictWriter(output_file, self._History_Data[0].keys())
                dict_writer.writeheader()
                dict_writer.writerows(self._History_Data)
