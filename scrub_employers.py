import numpy as np
import pandas as pd


def scrub_employers(df):
    '''
    Function to filter out analytically useless employer records from original collection.

    INPUT: df: Pandas DataFrame object.

    OUTPUT: Pandas DataFrame object with only useful rows.
    '''
    mask = df['num_ratings'] >= 100
    df = df[mask]
    low_rating_mask = df['overall_rating'] <= 2.0
    low_rated_ers = df[low_rating_mask]
    hi_rating_mask = df['overall_rating'] >= 4.0
    hi_rated_ers = df[hi_rating_mask]
    hi_recommend = hi_rated_ers['recommend_pct'] >= 80.0
    hi_rated_ers = hi_rated_ers[hi_recommend]
    df = low_rated_ers.append(hi_rated_ers)
    return df


if __name__ == '__main__':
    df = pd.read_pickle('employers.pkl')
    clean_df = scrub_employers(df)
    clean_df.to_pickle('clean_employers.pkl')
