import os
import pandas as pd
from string import maketrans, punctuation
from unidecode import unidecode


def clean_text(text_col):
    '''
    Function to clean up text in dataframe

    INPUT: pandas DataFrame column containing review texts

    OUTPUT: pandas DataFrame column with cleaned texts
    '''
    text_col = text_col.apply(lambda x: unidecode(x).lower())
    text_col = text_col.apply(lambda x: x.translate(maketrans('',''),
                                                    punctuation))
    return text_col



if __name__ == '__main__':
    ratings_df = pd.read_pickle(os.path.join('data', 'ratings_df_all.pkl'))
    ratings_df['clean_text'] = clean_text(ratings_df['review_text'])
