import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')


def scrub_employers(df):
    '''
    Function to refine the original collection of employers to the ones I will
    analyze later.

    INPUT: df: Pandas DataFrame object.

    OUTPUT: Pandas DataFrame object with only useful rows.
    '''
    mask = df['num_ratings'] >= 100
    df = df[mask]
    plot_hist(df['overall_rating'], 'Employers with at least 100 Reviews')
    low_cutoff = round(df['overall_rating'].quantile(0.05), 1)
    hi_cutoff = round(df['overall_rating'].quantile(0.95), 1)
    low_rating_mask = df['overall_rating'] <= low_cutoff
    hi_rating_mask = df['overall_rating'] >= hi_cutoff
    selected_ers = df[low_rating_mask | hi_rating_mask]
    middle_ers = df[~low_rating_mask & ~hi_rating_mask]
    plot_segmented_hist(df['overall_rating'], selected_ers['overall_rating'])
    return df


def plot_hist(arr, title):
    '''
    Function to plot a histogram of scores for employers

    INPUT:
        arr: Array-like, scores
        title: String, title for plot

    OUTPUT: Histogram plot (saved in directory)
    '''
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    ax.set_title(title, fontsize=14)
    ax.set_xlabel('Overall Score', fontsize=10)
    ax.set_ylabel('Observations', fontsize=10)
    ax.hist(arr, bins=(len(arr) / 180))
    plt.tight_layout()
    plt.savefig('images/{}.png'.format(title.replace(' ', '_').lower()))
    return


def plot_segmented_hist(arr_middle, arr_tails):
    '''
    Function to plot a histogram of scores, color coded tails to visualize
    sections of employers to be analyzed

    INPUT:
        arr_middle: Array-like, scores of employers not being analyzed
        (middle 90%)
        arr_tails: Array-like, scores of employers to be analyzed (>95%, <5%)

    OUTPUT: Histogram plot (saved in directory)
    '''

    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    ax.set_title('Employers with Significant Scores', fontsize=14)
    ax.set_xlabel('Overall Score', fontsize=10)
    ax.set_ylabel('Observations', fontsize=10)
    ax.hist(arr_middle, bins=34, label='Middle 90%')
    ax.hist(arr_tails, bins=34, label='Outer 5% Tails')
    plt.legend(loc='best', fontsize=10)
    plt.tight_layout()
    plt.savefig('images/sig_scores.png')


if __name__ == '__main__':
    df = pd.read_pickle('employers.pkl')
    clean_df = scrub_employers(df)
    clean_df.to_pickle('clean_employers.pkl')
