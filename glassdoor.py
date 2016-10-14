import os
import numpy as np
import pandas as pd
from time import sleep
import socket
import requests
from pymongo import MongoClient
import json


# glassdoor API documentation = https://www.glassdoor.com/developer/index.htm
def glassdoor_search(action='employers', page=1):
    '''
    Function to populate MongoDB with data from Glassdoor API. Currently optimized
    for use in the Employers API, but will be adding functionality to download
    reviews soon.
    INPUT: Action - str, section of API to search. Page - int, page of results.

    OUTPUT: JSON object with employer data (includes overall rating etc.)
    '''

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
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code == 403:
        print '403 Error: {}'.format(response.reason)
        print '30 Second timeout . . .'
        sleep(30)
        data = glassdoor_search(action, page)
    elif response.status_code == 200:
        data = json.loads(response.text)
        return data
    else:
        print 'Page {}:'.format(page)
        print 'Code {}: {}'.format(response.status_code, response.reason)
        return
    data = json.loads(content.read())
    return data


def find_five_stars(db_table):
    '''
    Short function to populate a list of 5.0 star rated employers from the
    employers table.

    INPUT: db_table: PyMongo table object.

    OUTPUT: List of company names that are 5 star employers.
    '''
    c = db_table.find({'overallRating': 5.0})
    names = {next(c)['name']: next(c)['overallRating']
             for i in range(c.count())}
    return names


if __name__ == '__main__':
    init_search = glassdoor_search()
    num_pages = init_search['response']['totalNumberOfPages']

    db_client = MongoClient()
    db = db_client['glassdoor']
    emp_table = db['employers']

    for i in xrange(num_pages):
        page = glassdoor_search('employers', i + 1)
        if not page:
            print 'Skipped page, see above.'
        else:
            emp_table.insert_many(page['response']['employers'])
        if (i + 1) % 25 == 0:
            print 'Loaded {} of {} pages, {} records . . .'.format(i + 1, num_pages, emp_table.count())

    five_star_dict = find_five_stars(emp_table)
