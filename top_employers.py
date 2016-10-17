import os
import numpy as np
import pandas as pd
from pymongo import MongoClient


def find_five_stars(db_table):
    '''
    Short function to populate a list of 5.0 star rated employers from the
    employers table.

    INPUT: db_table: PyMongo table object.

    OUTPUT: Set of company names that are 5 star employers.
    '''
    c = db_table.find({'$and': [{'overallRating': {'$in': ['4.5', '4.6', '4.7', '4.8', '4.9', '5.0']}},
                                {'numberOfRatings': {'$exists': True}},
                                {'numberOfRatings': {'$gt': 50}}]})
    names = set([next(c)['name'] for i in xrange(c.count())])
    return names


def key_info_dict(db_table, er_names):
    '''
    Grab key info for 5.0 star rated employers.

    INPUT: db_table: PyMongo table object, er_names: iterable of employer names.

    OUTPUT: Dictionary containing employer names and key data points.
    '''
    info_dict = {}
    i = 1
    for employer in er_names:
        print 'Employer {} of {}: {}'.format(i, len(er_names), employer.encode('ascii', 'ignore'))
        c = db_table.find({'name': employer})
        record = next(c)
        info_dict[record['name']] = {'num_ratings': record.get('numberOfRatings', None),
                                     'feature': record.get('featuredReview', None),
                                     'industry': record.get('industryName', None),
                                     'website': record.get('website', None)}
        i += 1
    return info_dict


if __name__ == '__main__':

    db_client = MongoClient()
    db = db_client['glassdoor']
    emp_table = db['employers']

    names = find_five_stars(emp_table)
    top_employers = key_info_dict(emp_table, names)
