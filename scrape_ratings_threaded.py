import os
import requests
import numpy as np
import pandas as pd
import threading
from time import sleep
from multiprocessing import Pool, cpu_count
from unidecode import unidecode
from selenium import webdriver
from bs4 import BeautifulSoup
from pymongo import MongoClient
# Import Glassdoor credentials from zsh profile
USER_ID = os.environ['GLASSDOOR_USERID']
PASSWORD = os.environ['GLASSDOOR_PASSWORD']


def load_pkl():
    df = pd.read_pickle('clean_employers.pkl')
    df['company_id'] = df['company_id'].astype(int)
    df['num_ratings'] = df['num_ratings'].astype(int)
    split = df['overall_rating'].mean()
    return df, split


def glassdoor_login():
    url = 'https://www.glassdoor.com/profile/login_input.htm'
    driver = webdriver.Chrome()
    driver.get(url)
    sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    while soup.find('h1') != None:
        # captcha = soup.find('img', id='recaptcha_challenge_image')['src']
        # img_text = requests.get(captcha).content
        # with open('captchas/captcha.tif', 'w') as f:
        #     f.write(img_text)
        # path = 'captchas/captcha.tif'
        # solved = solve_captcha(path)
        # print solved
        # captcha = driver.find_element_by_id('recaptcha_response_field')
        # captcha.click()
        # captcha.send_keys(solved)
        # complete = driver.find_element_by_id('dCF_input_complete')
        # complete.click()
        raw_input('Press Enter after solving the CAPTCHA...')
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        # print soup.find('img', id='recaptcha_challenge_image')
    else:
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
    # sleep(np.random.randint(5, 11))
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('h1').text == 'Pardon Our Interruption...':
        raw_input('Press Enter after solving the CAPTCHA...')
        soup = get_soup(driver, url)
    return soup


def parse_page(c_id, c_name, soup, pro_or_con):
    rows = []
    if pro_or_con == 'pro':
        idx = 2
    else:
        idx = 4
    reviews = soup.findAll('div', class_='cell reviewBodyCell')
    for review in reviews:
        text = review.findChildren('p')[idx].text
        row = {'company_id': c_id,
               'pro_or_con': pro_or_con,
               'company_name': c_name,
               'review_text': text}
        rows.append(row)
    return rows


def scrape_ratings(driver, company, pro_or_con, db_table):
    '''
    Scrape ratings for target companies. Insert text from 'Pros' into pros table.
    Insert text from 'Cons' into cons table.

    INPUT: Iterable of employer name/id combinations.

    OUTPUT: Pros or Cons, in a pandas DataFrame object.
    '''
    num_ratings = {}
    name, c_id = company
    url = 'https://www.glassdoor.com/Reviews/{}-Reviews-E{}.htm?filter.defaultEmploymentStatuses=false&filter.defaultLocation=false&filter.resetFilters=true'.format(name, c_id)
    soup = get_soup(driver, url)
    ratings = int(soup.findChild('h2').text.split()[0].replace(',', ''))
    p1_reviews = soup.findAll('div', class_='cell reviewBodyCell')
    pages = ratings / len(p1_reviews) + 1
    num_ratings[name] = ratings
    rows = parse_page(c_id, name, soup, pro_or_con)
    db_table.insert_many(rows)
    for i in xrange(1, pages):
        url = 'https://www.glassdoor.com/Reviews/{}-Reviews-E{}_P{}.htm?filter.defaultEmploymentStatuses=false&filter.defaultLocation=false&filter.resetFilters=true'.format(name, c_id, i + 1)
        soup = get_soup(driver, url)
        rows = parse_page(c_id, name, soup, pro_or_con)
        db_table.insert_many(rows)


def threaded_scrape(er_ids, pro_or_con, db_table):
    chunk_size = 5
    num_chunks = len(er_ids) / chunk_size + 1
    chunks = []
    for i in range(num_chunks):
        start = i * chunk_size
        stop = start + chunk_size
        if stop > len(er_ids) + 1:
            stop = len(er_ids) + 1
        chunks.append(er_ids[start:stop])
    for chunk in chunks:
        threads = []
        drivers = [glassdoor_login() for i in range(len(chunk))]
        for idx, company in enumerate(chunk):
            thread = threading.Thread(target=scrape_ratings,
                                      args=(drivers[idx], company, pro_or_con, db_table))
            threads.append(thread)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        for driver in drivers:
            driver.close()


def mongo_to_pandas(db_table):
    df = empty_df()
    df_2 = empty_df()
    c = db_table.find()
    lst = list(c)
    i = 0
    for rec in lst:
        i += 1
        if i % 2500 == 0:
            df = df.append(df_2)
            df_2 = empty_df()
        print 'Row {} of {}'.format(i, len(lst))
        row = parse_record(rec)
        df_2 = df_2.append(row, ignore_index=True)
    df = df.append(df_2)
    df['company_id'] = df['company_id'].astype(int)
    return df


def empty_df():
    '''
    Function to create an empty pandas DataFrame object (used in mongo_to_pandas)

    INPUT: None

    OUTPUT: empty pandas DataFrame object
    '''
    df = pd.DataFrame(columns=['company_id',
                               'company_name',
                               'pro_or_con',
                               'review_text'])
    return df


def parse_record(rec):
    row = pd.Series({'company_id': rec.get('company_id', None),
                     'company_name': rec.get('company_name', None),
                     'pro_or_con': rec.get('pro_or_con', None),
                     'review_text': rec.get('review_text', None)})
    return row


if __name__ == '__main__':
    clean_df, split = load_pkl()
    clean_df.sort_values('num_ratings', axis=0, inplace=True)
    good_ers = clean_df[clean_df['overall_rating'] >= split]
    bad_ers = clean_df[clean_df['overall_rating'] <= split]
    good_er_ids = zip(good_ers['company_name'], good_ers['company_id'])
    bad_er_ids = zip(bad_ers['company_name'], bad_ers['company_id'])
    db_client = MongoClient()
    db = db_client['glassdoor']
    ratings_table = db['ratings']
    threaded_scrape(good_er_ids, 'pro', ratings_table)
    threaded_scrape(bad_er_ids, 'con', ratings_table)
    ratings_df = mongo_to_pandas(ratings_table)
