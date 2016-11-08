import os
import pandas as pd
import spacy
from multiprocessing import Pool, cpu_count
from string import punctuation
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
STOPLIST = set(["n't", "'s", "'m", "ca", "'", "'re", "i've", 'poor', '-',
                'worst', 'place', 'make', 'thing', 'hour', 'low', 'high', 'bos',
                'good', 'great', 'awesome', 'excellent', 'job', 'best', 'lot',
                'wonderful', 'awful', 'work', 'amazing', 'suck', 'nice',
                'really', 'free', 'like', 'love', 'bad', 'terrible', 'care',
                'horrible', 'company', 'employee', 'staff', 'time', 'day',
                'week', 'month', 'year', 'need', 'better', 'just', 'decent'] +
                list(ENGLISH_STOP_WORDS))
KEEP_POS = {'ADJ','ADP','ADV','NOUN','VERB'}
nlp = spacy.load('en')


def clean_text(reviews):
    '''
    Function to clean up text in dataframe

    INPUT: pandas DataFrame column containing review texts

    OUTPUT: pandas DataFrame column with cleaned texts
    '''
    lemmatized = []
    cpus = cpu_count() - 1
    pool = Pool(processes=cpus)
    lemmatized = pool.map(lemmatize_text, reviews)
    return lemmatized


def lemmatize_text(text, stop_words=STOPLIST, keep_pos=KEEP_POS):
    # STOPLIST = set(["n't", "'s", "'m", "ca", "'", "'re", "i've", 'poor', '-',
    #                 'worst', 'place', 'make', 'thing', 'hour', 'low', 'high',
    #                 'good', 'great', 'awesome', 'excellent', 'job', 'best',
    #                 'work', 'amazing', 'suck', 'decent', 'lot', 'time',
    #                 'bad', 'terrible', 'horrible', 'company', 'employee'] +
    #                 list(ENGLISH_STOP_WORDS))
    # KEEP_POS = {'ADJ','ADP','ADV','AUX','NOUN','VERB','X','PROPN'}
    x = nlp(text)
    words = [tok.lemma_.strip(punctuation) for tok in x if (tok.pos_ in keep_pos) and (tok.lemma_.strip(punctuation) not in STOPLIST)]
    words.extend(['boss' for tok in x if tok.lemma_ == 'bos'])
    return ' '.join(words)


if __name__ == '__main__':
    ratings_df = pd.read_pickle(os.path.join('data', 'ratings_df_all.pkl'))
    ratings_df['lemmatized_text'] = clean_text(ratings_df['review_text'])
    pros_df = ratings_df[ratings_df['pro_or_con'] == 'pro']
    cons_df = ratings_df[ratings_df['pro_or_con'] == 'con']
    pros_df.to_pickle(os.path.join('data', 'pros_df.pkl'))
    cons_df.to_pickle(os.path.join('data', 'cons_df.pkl'))
