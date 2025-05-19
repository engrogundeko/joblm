import os
import pandas as pd
import pprint
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, quote


def get_name(scholarship):
    try:
        return scholarship.select_one('h2 a').text.strip()
    except:
        return None


def get_univ(scholarship):
    try:
        return scholarship.select_one(
            '.entry.clearfix .post_column_1 p').text.strip().splitlines()[0]
    except:
        return None


def get_degree(scholarship):
    try:
        return scholarship.select_one('.post_column_1 p').text.strip().splitlines()[1].replace('Degree', '')
    except:
        return None


def get_deadline(scholarship):
    try:
        return scholarship.select('.post_column_1 p')[1].text.strip().splitlines()[0].replace('Deadline:', '').lstrip()
    except:
        return None


def get_country(scholarship):
    try:
        return scholarship.select('.post_column_1 p')[1].text.strip().splitlines()[1].replace('Study in:', '').lstrip()
    except:
        return None


def get_start(scholarship):
    try:
        start_date = scholarship.select('.post_column_1 p')[
            1].text.strip().splitlines()[2]
        return start_date[start_date.rfind('starts')+len('starts'):].lstrip()
    except:
        return None


pages = [str(i) for i in range(1, 2)]
scholarships_list = []
base_url = "https://www.scholars4dev.com/category/level-of-study/masters-scholarships/"
for page in pages:
    # Properly construct and encode the URL
    page_path = quote(page) + '/'
    URL = urljoin(base_url, page_path)
    print(URL)
    r = requests.get(URL)

    soup = BeautifulSoup(r.content, 'html.parser')

    scholarships = soup.select('.entry.clearfix')

    for scholarship in scholarships:
        scholarship_dict = {}

        scholarship_name = get_name(scholarship)
        scholarship_dict['name'] = scholarship_name
        print(scholarship_dict['name'], page)

        scholarship_univ = get_univ(scholarship)
        scholarship_dict['univ'] = scholarship_univ

        scholarship_degree = get_degree(scholarship)
        scholarship_dict['degree'] = scholarship_degree

        scholarship_deadline = get_deadline(scholarship)
        scholarship_dict['deadline'] = scholarship_deadline

        scholarship_country = get_country(scholarship)
        scholarship_dict['country'] = scholarship_country

        scholarship_start = get_start(scholarship)
        scholarship_dict['start'] = scholarship_start

        scholarships_list.append(scholarship_dict)

# pretty print to console
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(scholarships_list)

# create a dataframe
df = pd.DataFrame(scholarships_list)

# export dataframe to csv
working_dir = os.getcwd()
df.to_csv(working_dir+'/export/scholarship.csv')