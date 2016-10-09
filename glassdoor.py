import os
import numpy as np
import pandas as pd
from urllib2 import Request, urlopen
import socket
import requests
from pymongo import MongoClient
import json


# glassdoor API documentation = https://www.glassdoor.com/developer/index.htm
def glassdoor_search(action='employers', page=1):
    url = 'http://api.glassdoor.com/api/api.htm?'
    params = {'v': '1',
              't.p': os.environ['glassdoor_id'],
              't.k': os.environ['glassdoor_key'],
              'userip': socket.gethostbyname(socket.gethostname()),
              'useragent': 'Mozilla/5.0',
              'action': action,
              'pn': page}
    url = url + \
        't.p={}&t.k={}&userip={}&useragent={}&format=json&v={}&action={}&pn={}'.format(
            params['t.p'],
            params['t.k'],
            params['userip'],
            params['useragent'],
            params['v'],
            params['action'],
            params['pn'])
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    content = urlopen(req)
    data = json.loads(content.read())
    return data


if __name__ == '__main__':
    r = glassdoor_search()
    num_pages = r['response']['totalNumberOfPages']

    db_client = MongoClient()
    db = db_client['glassdoor']
    emp_table = db['employers']

    for i in xrange(num_pages):
        page = glassdoor_search('employers', i + 1)
        print 'Page {}:'.format(i + 1), len(page['response']['employers'])
        for employer in page['response']['employers']:
            emp_table.insert_one(employer)
