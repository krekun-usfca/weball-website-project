#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 18:05:15 2020

@author: srikarmurali
"""

import requests
import json
import pandas as pd

api_key = '-OpfKVtyZujAAjn7oCwGKaVwsXuo0Nr5uwDInNIVQK5NYr74uqvbbVO7eIOfDr9bUMuuHKpRQtDEoqKfOqNyNPh4R-6eSDDaxWpdqzox5FWp4IUBCaRYsL-wsVaGXnYx'
headers = {'Authorization': 'Bearer %s' % api_key}


def get_court_reviews():
    """Retrieve basketball court reviews."""
    court_information = pd.read_csv(
        "court_information.csv", error_bad_lines=False)

    #
    url = "https://api.yelp.com/v3/businesses/{0}/reviews"
    court_reviews = []
    for idx, row in court_information.iterrows():
        url_id = url.format(row["court_id"])
        req = requests.get(url_id, headers=headers)
        parsed = json.loads(req.text)
        if "reviews" in parsed.keys():
            court_review = []
            for review in parsed['reviews']:
                court_id = row['court_id']
                review_id = review['id']
                review_text = review['text']
                rating = review['rating']
                user_id = review['user']['id']
                user_name = review['user']['name']
                time = review['time_created']
                date = time.split(' ')[0].split('-')
                day = date[2].strip('-')
                month = date[1].strip('-')
                year = date[0].strip('-')
                court_review.append(
                    [court_id, review_id, review_text, rating, user_id, user_name, day, month, year])
            court_reviews.append(court_review)
    court_reviews = [item for sublist in court_reviews for item in sublist]
    return court_reviews


if __name__ == "__main__":
    court_reviews = get_court_reviews()
    court_reviews = pd.DataFrame(court_reviews, columns=['court_id', 'review_id', 'review_text', 'rating', 'user_id', 'user_name',
                                                         'day', 'month', 'year'])

    court_reviews.to_csv("court_reviews.csv", encoding='utf-8', index=False)