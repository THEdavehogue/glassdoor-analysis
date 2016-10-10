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
        't.p={}&t.k={}&userip={}&useragent={}&format=json&v={}&action={}&pn={}&ps=50'.format(
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
    return url, data


def find_five_stars(db_table):
    c = db_table.find({'overallRating': 5.0})
    names = [next(c)['name'] for i in range(c.count())]
    return names


if __name__ == '__main__':
    url, r = glassdoor_search()
    num_pages = r['response']['totalNumberOfPages']

    db_client = MongoClient()
    db = db_client['glassdoor']
    emp_table = db['employers']

    for i in xrange(num_pages):
        url, page = glassdoor_search('employers', i + 1)
        counter = 0
        while (not page['success']) and counter < 5:
            url, page = glassdoor_search('employers', i + 1)
            counter += 1
        else:
            print 'Page {}:'.format(i + 1), len(page['response']['employers'])
            for employer in page['response']['employers']:
                emp_table.insert_one(employer)

    five_star_names = find_five_stars()
