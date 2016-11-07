import os
import sys
import numpy as np
import pandas as pd
import spacy
import matplotlib.pyplot as plt
from PIL import Image
from wordcloud import WordCloud
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
plt.style.use('ggplot')


def stop_words():
    STOPLIST = set(["n't", "'s", "'m", "ca", "'", "'re", "i've", 'poor', '-',
                    'worst', 'place', 'make', 'thing', 'hour', 'low', 'high',
                    'good', 'great', 'awesome', 'excellent', 'job', 'best',
                    'work', 'amazing', 'suck',
                    'bad', 'terrible', 'horrible', 'company', 'employee'] +
                    list(ENGLISH_STOP_WORDS))
    return STOPLIST


class NMFCluster(object):

    def __init__(self, pro_or_con, num_topics, tfidf_max_features=5000, tfidf_max_df=0.9, tfidf_min_df=1000, nmf_alpha=0.1, nmf_l1_ratio=0.25, random_state=None):
        self.pro_or_con = pro_or_con
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


    def topic_word_frequency(self, topic_idx):
        ''' Return (word, frequency) tuples for creating word cloud
        INPUT:
            topic_idx: int
        '''
        freq_sum = np.sum(self.nmf.components_[topic_idx])
        frequencies = [val / freq_sum for val in self.nmf.components_[topic_idx]]
        return zip(self.tfidf_features, frequencies)


    def plot_topic(self, topic_idx):
        word_freq = self.topic_word_frequency(topic_idx)
        wc = WordCloud(background_color='white')
        wc.fit_words(word_freq)
        fig = plt.figure(figsize=(12,6))
        ax = fig.add_subplot(111)
        ax.axis('off')
        ax.imshow(wc)
        plt.show()


    def visualize_topics(self, df):
        for i in range(self.num_topics):
            self.print_topic_summary(df, i)
            self.plot_topic(i)
            print ''


if __name__ == '__main__':
    pros_df = pd.read_pickle(os.path.join('data', 'pros_df.pkl'))
    cons_df = pd.read_pickle(os.path.join('data', 'cons_df.pkl'))

    topics = 10
    nmf_pros = NMFCluster('pro', topics, random_state=42)
    nmf_cons = NMFCluster('con', topics, random_state=42)
    nmf_pros.fit_nmf(pros_df)
    nmf_cons.fit_nmf(cons_df)

    nmf_pros.visualize_topics(pros_df)
    nmf_cons.visualize_topics(cons_df)
