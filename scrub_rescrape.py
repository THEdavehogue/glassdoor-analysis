import os
import numpy as np
import pandas as pd
import cPickle as pickle
from pymongo import MongoClient
from scrape_ratings_threaded import threaded_scrape, mongo_to_pandas


def load_filepaths():
    '''
    Function to load in data that has previously been pickled and stored

    INPUT: None

    OUTPUT: List of filepaths
    '''
    paths = [os.path.join('data','ratings_df_{}.pkl'.format(i+1)) for i in range(5)]
    if os.path.exists(os.path.join('data', 'rescrape_df.pkl')):
        paths.append(os.path.join('data', 'rescrape_df.pkl'))
    return paths


def init_mongo(coll_name):
    '''
    Function to initialize pymongo db connection.

    INPUT: coll_name: string, name of mongo collection to connect

    OUTPUT: pymongo collection object
    '''
    client = MongoClient()
    db = client['glassdoor']
    coll = db[coll_name]
    return coll


def drop_junk(ratings_df):
    '''
    Function to get rid of junk reviews

    INPUT: pandas DataFrame (combined with all rating data)

    OUTPUT: pandas DataFrame, free of garbage
    '''
    ratings_df = ratings_df[ratings_df['review_text'] != 'Pros']
    ratings_df.drop_duplicates(inplace=True)
    ratings_df.reset_index(drop=True)
    return ratings_df


def combine_data(paths):
    '''
    Function to combine dataframes from pickled form

    INPUT: Iterable of filepaths for pickled DataFrames

    OUTPUT: Single pandas DataFrame with all ratings
    '''
    ratings_df = pd.read_pickle(paths[0])
    for path in paths[1:]:
        ratings_df = ratings_df.append(pd.read_pickle(path))
    return ratings_df


def check_review_counts(ratings_df):
    '''
    Function to check that enough data was collected. Compares number of reviews
    for each target employer with the number of reviews collected

    INPUT: ratings_df: Pandas DataFrame containing scraped review text

    OUTPUT: good_er_ids, bad_er_ids: Lists of tuples to rescrape from glassdoor
    '''
    clean_df = pd.read_pickle('data/clean_employers.pkl')
    target_ratings = clean_df[['company_name', 'company_id',
                               'num_ratings', 'overall_rating']]
    company_ratings = ratings_df['company_name'].value_counts()
    company_ratings = company_ratings.to_frame(name='ratings_collected')
    company_ratings.reset_index(inplace=True)
    check_df = target_ratings.merge(company_ratings,
                                    how='left',
                                    left_on='company_name',
                                    right_on='index')
    check_df['company_id'] = check_df['company_id'].astype(int)
    check_df.drop('index', axis=1, inplace=True)
    check_df['delta'] = check_df['num_ratings'] - check_df['ratings_collected']
    check_df['delta_pct'] = check_df['delta'] / check_df['num_ratings']
    rescrape = check_df[check_df['delta_pct'] > 0.5]
    good_rescrape = rescrape[rescrape['overall_rating'] > 3.5]
    bad_rescrape = rescrape[rescrape['overall_rating'] < 3.5]
    good_er_ids = zip(good_rescrape['company_name'], good_rescrape['company_id'])
    bad_er_ids = zip(bad_rescrape['company_name'], bad_rescrape['company_id'])
    pickle.dump(good_er_ids, open('data/rescrape_pros.pkl', 'wb'))
    pickle.dump(bad_er_ids, open('data/rescrape_cons.pkl', 'wb'))
    return good_er_ids, bad_er_ids


def rescrape(ratings_df, good_er_ids, bad_er_ids):
    '''
    Function to go back and scrape stuff that we missed the first time

    INPUT: original pandas DataFrame containing all review text; good_er_ids,
           bad_er_ids from check_review_counts. Employers that need to be
           rescraped

    OUTPUT: new pandas DataFrame with rescraped reviews added and scrubbed
    '''
    if (len(good_er_ids) > 0) or (len(bad_er_ids) > 0):
        threaded_scrape(good_er_ids, 'pro', coll)
        threaded_scrape(bad_er_ids, 'con', coll)
        rescrape_df = mongo_to_pandas(coll)
        rescrape_df.to_pickle('data/rescrape_df.pkl')
        ratings_df = drop_junk(ratings_df.append(rescrape_df))
    return ratings_df


if __name__ == '__main__':
    paths = load_filepaths()
    ratings_df = drop_junk(combine_data(paths))
    coll = init_mongo('ratings_rescrape')
    good_er_ids, bad_er_ids = check_review_counts(ratings_df)
    ratings_df = rescrape(ratings_df, good_er_ids, bad_er_ids)
    ratings_df.to_pickle('data/ratings_df_all.pkl')
