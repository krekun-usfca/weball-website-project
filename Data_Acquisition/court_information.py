#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 14:50:14 2020

@author: srikarmurali
"""

import requests
import json
import pandas as pd

api_key = '-OpfKVtyZujAAjn7oCwGKaVwsXuo0Nr5uwDInNIVQK5NYr74uqvbbVO7eIOfDr9bUMuuHKpRQtDEoqKfOqNyNPh4R-6eSDDaxWpdqzox5FWp4IUBCaRYsL-wsVaGXnYx'
headers = {'Authorization': 'Bearer %s' % api_key}


def get_court_information(search_term, location, limit):
  """Retrieve business information using Yelp API."""
  court_information = []
   for offset in range(1, 1000, 50):
        url = 'https://api.yelp.com/v3/businesses/search'
        if offset == 1:
            params = {'term': search_term,
                'location': location, 'limit': limit}
        else:
            params = {'term': 'Basketball Court',
                'location': 'San Francisco', 'limit': 50, "offset": offset}

        req = requests.get(url, params=params, headers=headers)
        parsed = json.loads(req.text)
        if 'businesses' in parsed.keys():
            court_data = []
            for business in parsed["businesses"]:
                court_id = business['id']
                name = business['name']
                rating = business['rating']
                review_count = business['review_count']
                latitude = business['coordinates']['latitude']
                longitude = business['coordinates']['longitude']
                address = business['location']['address1']
                city = business['location']['city']
                zip_code = business['location']['zip_code']
                country = business['location']['country']
                state = business['location']['state']
                display_address = ','.join(
                    business['location']['display_address'])
                court_data.append([court_id, name, rating, review_count, latitude, longitude, address,
                                   city, zip_code, country, state, display_address])
            court_information.append(court_data)

    court_information = [
       item for sublist in court_information for item in sublist]
    return court_information

if __name__ == '__main__':
    court_information = get_court_information(
       'Basketball Court', 'San Francisco', 50)
    court_information = pd.DataFrame(court_information, columns=['court_id', 'name', 'rating', 'review_count', 'latitude', 'longitude',
                                                                 'address', 'city', 'zip_code', 'country', 'state',
                                                                 'display_address'])
    print(court_information.head())
    court_information.to_csv("court_information.csv",
                             encoding='utf-8', index=False)