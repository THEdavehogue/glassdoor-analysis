import os
import sys
import numpy as np
import pandas as pd
import spacy
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS


def stop_words():
    STOPLIST = set(["n't", "'s", "'m", "ca", "'", "'re", "i've", 'poor', '-',
                    'worst', 'place', 'make', 'thing', 'hour', 'low', 'high',
                    'good', 'great', 'awesome', 'excellent', 'job', 'best',
                    'work', 'amazing', 'suck',
                    'bad', 'terrible', 'horrible', 'company', 'employee'] +
                    list(ENGLISH_STOP_WORDS))
    return STOPLIST


class NMFCluster(object):

    def __init__(self, num_topics, tfidf_max_features=5000, tfidf_max_df=0.9, tfidf_min_df=1000, nmf_alpha=0.1, nmf_l1_ratio=0.25, random_state=None):
        self.num_topics = int(num_topics)
        self.tfidf_max_features = tfidf_max_features
        self.tfidf_max_df = tfidf_max_df
        self.tfidf_min_df = tfidf_min_df
        self.nmf_alpha = nmf_alpha
        self.nmf_l1_ratio = nmf_l1_ratio
        self.random_state = random_state
        self.stop_words = stop_words()


    def fit_nmf(self, df):
        self.fit_tfidf(df)
        self.nmf = NMF(n_components=self.num_topics, alpha=self.nmf_alpha, l1_ratio=self.nmf_l1_ratio, random_state=self.random_state).fit(self.tfidf_matrix)
        self.W_matrix = self.nmf.transform(self.tfidf_matrix)
        sums = self.W_matrix.sum(axis=1)
        self.W_pct = self.W_matrix / sums[:, None]
        self.labels = self.W_pct >= 0.05


    def fit_tfidf(self, df):
        self.tfidf = TfidfVectorizer(input='content', use_idf=True, lowercase=True, max_features=self.tfidf_max_features, max_df=self.tfidf_max_features, min_df=self.tfidf_min_df)
        self.tfidf_matrix = self.tfidf.fit_transform(df['lemmatized_text']).toarray()
        self.tfidf_features = np.array(self.tfidf.get_feature_names())
        self.tfidf_reverse_lookup = {word: idx for idx, word in enumerate(self.tfidf_features)}


    def top_words_by_topic(self, n_top_words, topic=None):
        if topic != None:
            idx = np.argsort(self.nmf.components_[topic])[-n_top_words:][::-1]
            return self.tfidf_features[idx]
        else:
            idxs = [np.argsort(topic)[-n_top_words:][::-1] for topic in self.nmf.components_]
            return np.array([self.tfidf_features[idx] for idx in idxs])


    def topic_attribution_by_document(self, document_idx):

        idxs = np.where(self.labels[document_idx] == 1)[0]
        idxs = idxs[np.argsort(self.W_pct[document_idx, idxs])[::-1]]
        return np.array([(idx, pct) for idx, pct in zip(idxs, self.W_pct[document_idx, idxs])])


    def print_topic_summary(self, df, topic_num, num_words=20):
        num_reviews = self.labels[:, topic_num].sum()
        print 'Summary of Topic {}:'.format(topic_num)
        print 'Number of reviews in topic: {}'.format(num_reviews)
        print 'Top {} words in topic:'.format(num_words)
        print self.top_words_by_topic(num_words, topic_num)
        if not num_reviews:
            return None
        # reviews_by_source = [float(len(df.loc[(self.labels[:, topic_num]) & (df['source'] == outlet)])) / num_articles for outlet in zip(*self.outlets)[0]]
        # print 'Breakdown by source:'
        # print '\t'.join(['{0}: {1:.2f}%'.format(outlet, percent*100) for outlet, percent in zip(zip(*self.outlets)[1], articles_by_source)])
        #
        # normalized = [percent / len(df.loc[df['source'] == outlet]) for outlet, percent in zip(zip(*self.outlets)[0], articles_by_source)]
        # normalized = [percent / np.sum(normalized) for percent in normalized]
        #
        # print 'Breakdown normalized by number of articles published by source:'
        # print '\t'.join(['{0}: {1:.2f}%'.format(outlet, percent*100) for outlet, percent in zip(zip(*self.outlets)[1], normalized)])


    def topic_word_frequency(self, topic_idx):
        ''' Return (word, frequency) tuples for creating word cloud
        INPUT:
            topic_idx: int
        '''
        freq_sum = np.sum(self.nmf.components_[topic_idx])
        frequencies = [val / freq_sum for val in self.nmf.components_[topic_idx]]
        return zip(self.tfidf_features, frequencies)


if __name__ == '__main__':
    ratings_df = pd.read_pickle(sys.argv[1])

    topics = 10
    nmf = NMFCluster(topics)
    nmf.fit_nmf(ratings_df)

    for i in range(topics):
        nmf.print_topic_summary(ratings_df, i)
        print ''
