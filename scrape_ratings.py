import os
import requests
import pandas as pd
from time import sleep
from selenium import webdriver
from bs4 import BeautifulSoup
# Import Glassdoor credentials from zsh profile
USER_ID = os.environ['GLASSDOOR_USERID']
PASSWORD = os.environ['GLASSDOOR_PASSWORD']


def glassdoor_login():
    url = 'https://www.glassdoor.com/profile/login_input.htm'
    driver = webdriver.Chrome()
    driver.get(url)
    sleep(4)

    user = driver.find_element_by_name('username')
    user.click()
    user.send_keys(USER_ID)

    pwrd = driver.find_element_by_xpath('//*[@id="signInPassword"]')
    pwrd.click()
    pwrd.send_keys(PASSWORD)

    sign_in = driver.find_element_by_id('signInBtn')
    sign_in.click()
    sleep(5)
    return driver


def get_soup(driver, url):
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def scrape_ratings(driver, er_ids, pro_or_con):
    '''
    Scrape ratings for target companies. Insert text from 'Pros' into pros table.
    Insert text from 'Cons' into cons table.

    INPUT: Iterable of employer name/id combinations.

    OUTPUT: Pros or Cons, in a pandas DataFrame object.
    '''
    corpus = pd.DataFrame(columns=['company_id',
                                   'company_name',
                                   'review_text'])
    num_ratings = {}
    for company in er_ids:
        name, c_id = company
        url = 'https://www.glassdoor.com/Reviews/{}-Reviews-E{}.htm?filter.\
        defaultEmploymentStatuses=false&filter.defaultLocation=false\
        &filter.resetFilters=true'.format(name, c_id)
        soup = get_soup(driver, url)
        ratings = int(soup.findChild('h2').text.split()[0].replace(',', ''))
        p1_reviews = soup.findAll('div', class_='cell reviewBodyCell')
        pages = ratings / len(p1_reviews) + 1
        num_ratings[name] = ratings
        for i in xrange(1, pages):
            url = 'https://www.glassdoor.com/Reviews/{}-Reviews-E{}_P{}.htm?filter.\
            defaultEmploymentStatuses=false&filter.defaultLocation=false\
            &filter.resetFilters=true'.format(name, c_id, i + 1)
            soup = get_soup(driver, url)
            reviews = soup.findAll('div', class_='cell reviewBodyCell')
            for review in reviews:
                pros = review.findChildren('p')[2].text
                row = pd.Series({'company_id': c_id,
                                 'company_name': name,
                                 'review_text': pros})
                corpus = corpus.append(row, ignore_index=True)
    return corpus


if __name__ == '__main__':
    clean_df = pd.read_pickle('clean_employers.pkl')
    clean_df['company_id'] = clean_df['company_id'].astype(int)
    good_ers = clean_df[clean_df['overall_rating'] >= 4.0]
    bad_ers = clean_df[clean_df['overall_rating'] <= 2.0]
    good_er_ids = zip(good_ers['company_name'], good_ers['company_id'])
    bad_er_ids = zip(bad_ers['company_name'], bad_ers['company_id'])
    driver = glassdoor_login()
    pos_corpus = scrape_ratings(driver, good_er_ids, 'pro')
    neg_corpus = scrape_ratings(driver, bad_er_ids, 'con')
