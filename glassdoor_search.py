import os
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
    if response.status_code != 200:
        print 'Error {}: {}'.format(response.status_code, response.reason)
        print '30 Second timeout . . .'
        sleep(30)
        data = glassdoor_search(action, page)
    else:
        data = json.loads(response.text)
    return data


def empty_df():
    df = pd.DataFrame(columns=['company_id',
                               'company_name',
                               'num_ratings',
                               'overall_rating',
                               'recommend_pct',
                               'culture_rating',
                               'comp_rating',
                               'opportunity_rating',
                               'leader_rating',
                               'work_life_rating',
                               'industry'])
    return df


def parse_record(rec):
    row = pd.Series({'company_id': rec.get('id', None),
                     'company_name': rec.get('name', None),
                     'num_ratings': rec.get('numberOfRatings', None),
                     'overall_rating': rec.get('overallRating', None),
                     'recommend_pct': rec.get('recommendToFriendRating', None),
                     'culture_rating': rec.get('cultureAndValuesRating', None),
                     'comp_rating': rec.get('compensationAndBenefitsRating', None),
                     'opportunity_rating': rec.get('careerOpportunitiesRating', None),
                     'leader_rating': rec.get('seniorLeadershipRating', None),
                     'work_life_rating': rec.get('workLifeBalanceRating', None),
                     'industry': rec.get('industryName', None)})
    return row


def mongo_to_pandas(db_table):
    df = empty_df()
    df_2 = empty_df()
    c = db_table.find()
    lst = list(c)
    i = 0
    for rec in lst:
        i += 1
        if i % 2500 == 0:
            df = df.append(df_2)
            df_2 = empty_df()
        print 'Row {} of {}'.format(i, len(lst))
        row = parse_record(rec)
        df_2 = df_2.append(row, ignore_index=True)
    df['company_id'] = df['company_id'].astype(int)
    df['num_ratings'] = df['num_ratings'].astype(int)
    return df


if __name__ == '__main__':
    # init_search = glassdoor_search()
    # num_pages = init_search['response']['totalNumberOfPages']

    db_client = MongoClient()
    db = db_client['glassdoor']
    emp_table = db['employers']

    # for i in xrange(num_pages):
    #     page = glassdoor_search('employers', i + 1)
    #     counter = 1
    #     while not page['success'] and counter < 5:
    #         page = glassdoor_search('employers', i + 1)
    #         counter += 1
    #     else:
    #         emp_table.insert_many(page['response']['employers'])
    #     if (i + 1) % 25 == 0:
    # print 'Loaded {} of {} pages, {} records . . .'.format(i + 1, num_pages,
    # emp_table.count())

    employers_df = mongo_to_pandas(emp_table)
    employers_df.to_pickle('employers.pkl')
