import numpy as np
import pandas as pd
import cPickle as pickle
from pymongo import MongoClient
from scrape_ratings_threaded import threaded_scrape, mongo_to_pandas


def drop_junk(ratings_df):
    '''
    Function to get rid of junk reviews.

    INPUT: pandas DataFrame (combined with all rating data)

    OUTPUT: pandas DataFrame, free of garbage
    '''
    ratings_df = ratings_df[ratings_df['review_text'] != 'Pros']
    ratings_df.drop_duplicates(inplace=True)

    return ratings_df


def combine_data(paths):
    '''
    Function to combine dataframes from pickled form.

    INPUT: Iterable of filepaths for pickled DataFrames

    OUTPUT: Single pandas DataFrame with all ratings
    '''
    ratings_df = pd.read_pickle(paths[0])
    for path in paths[1:]:
        ratings_df = ratings_df.append(pd.read_pickle(path))
    return ratings_df


def check_review_counts(ratings_df):
    clean_df = pd.read_pickle('clean_employers.pkl')
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
    pickle.dump(good_er_ids, open('rescrape_pros.pkl', 'wb'))
    pickle.dump(bad_er_ids, open('rescrape_cons.pkl', 'wb'))
    return good_er_ids, bad_er_ids


if __name__ == '__main__':
    paths = ['ratings_df_1.pkl', 'ratings_df_2.pkl', 'ratings_df_3.pkl',
             'ratings_df_4.pkl', 'ratings_df_5.pkl']
    ratings_df = drop_junk(combine_data(paths))
    good_er_ids, bad_er_ids = check_review_counts(ratings_df)
    db_client = MongoClient()
    db = db_client['glassdoor']
    tab = db['ratings_rescrape']
    threaded_scrape(good_er_ids, 'pro', tab)
    threaded_scrape(bad_er_ids, 'con', tab)
    rescrape_df = mongo_to_pandas(tab)
    rescrape_df.to_pickle('rescrape_df.pkl')
