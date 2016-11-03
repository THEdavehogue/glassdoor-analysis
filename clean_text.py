import os
import pandas as pd
import spacy
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
nlp = spacy.load('en')


def clean_text(reviews):
    '''
    Function to clean up text in dataframe

    INPUT: pandas DataFrame column containing review texts

    OUTPUT: pandas DataFrame column with cleaned texts
    '''
    STOPLIST = set(["n't", "'s", "'m", "ca", "'", "'re", "i've", 'poor',
                    'good', 'great', 'awesome', 'excellent', 'job',
                    'bad', 'terrible', 'horrible', 'company', 'employee'] +
                    list(ENGLISH_STOP_WORDS))
    keep_pos = ['NOUN', 'VERB', 'ADJ', 'ADV']
    lemmatized = []
    for review in reviews:
        x = nlp(review)
        words = [tok.lemma_ for tok in x if (tok.pos_ in keep_pos)
                                         and (tok.lemma_ not in STOPLIST)]
        lemmatized.append(' '.join(words))
    return lemmatized


def run_tfidf(lemm_column):

    STOPLIST = set(["n't", "'s", "'m", "ca", "'", "'re", "i've", 'poor',
                    'worst', 'place', 'make', 'thing', 'hour',
                    'good', 'great', 'awesome', 'excellent', 'job', 'best',
                    'bad', 'terrible', 'horrible', 'company', 'employee'] +
                    list(ENGLISH_STOP_WORDS))
    tfidf = TfidfVectorizer(input='content', stop_words=STOPLIST, use_idf=True, lowercase=True, max_features=5000, max_df=0.9, min_df=50, ngram_range=(1,3))
    tfidf_matrix = tfidf.fit_transform(lemm_column).toarray()
    tfidf_features = tfidf.get_feature_names()
    tfidf_reverse_lookup = {word: idx for idx, word in enumerate(tfidf_features)}
    tfidf_sum = tfidf_matrix.sum(axis=0)
    word_freq = []
    for word, idx in tfidf_reverse_lookup.iteritems():
        word_freq.append((word, tfidf_sum[idx]))

    wc = WordCloud(background_color='white')
    wc.fit_words(word_freq)
    plt.imshow(wc)
    plt.show()




if __name__ == '__main__':
    ratings_df = pd.read_pickle(os.path.join('data', 'ratings_df_all.pkl'))
    ratings_df['clean_text'] = clean_text(ratings_df['review_text'])
