#!/usr/bin/env python
# coding: utf-8

import time
from bs4 import BeautifulSoup
import sys, io
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.proxy import *
from joblib import load, dump 
import pandas as pd
from decimal import Decimal

# Scrapes data off of each individual hotel page
def scrape_hotel_data(driver):
    page = driver.page_source
    soup_expansion = BeautifulSoup(page, 'html.parser')
    address = soup_expansion.find('span', class_='public-business-listing-ContactInfo__ui_link--1_7Zp public-business-listing-ContactInfo__level_4--3JgmI')
    hotel_address = address.get_text() if address != None else 'Not Found'
    hotel_name = driver.title.split('$')[0].title()
    price_tag = soup_expansion.find('span', class_='hotels-hotel-offers-DetailTextOffer__price--2gYdd')
    price = 0
    if price_tag != None:
        try:
            price = int(re.sub(r'[^\d.]', '', re.search('\$(\d+)', driver.title).group(0)))
        except AttributeError:
            try:
                price = int(re.sub(r'[^\d.]', '', re.search('\$(\d+)', price_tag.get_text()).group(0)))
            except:
                price = 0
    print(price)
    num_reviews_tag = soup_expansion.find('span', class_='hotels-hotel-review-about-with-photos-Reviews__seeAllReviews--3PpLR')
    num_reviews = 0
    if num_reviews_tag != None:
        try:
            num_reviews_string = num_reviews_tag.get_text()
            num_reviews = int(num_reviews_string.split(' ')[0].replace(',', ''))
            print(num_reviews)
        except:
            print('unable to get num_reviews: ', num_reviews_string)
    primary_rating_tag = soup_expansion.find('span', class_='hotels-hotel-review-about-with-photos-Reviews__overallRating--vElGA')
    primary_rating = Decimal(primary_rating_tag.get_text()) if primary_rating_tag != None else 0
    ui_bubble_ratings = {}
    for i in range(0, 55, 5):
        ui_bubble_ratings['bubble_' + str(i)] = i * 0.1
    secondary_ratings = soup_expansion.find_all('div', class_='hotels-hotel-review-about-with-photos-Reviews__subratingRow--2u0CJ')
    metrics = [None, None, None, None]
    for i, rating in enumerate(secondary_ratings):
        result = re.search('bubble_(\d\d)', str(rating))
        metrics[i] = Decimal(ui_bubble_ratings[result.group(0)])
    amenities_tag = soup_expansion.find_all('div', class_='hotels-hr-about-amenities-Amenity__amenity--3fbBj')
    amenities = []
    for amenity in amenities_tag:
        amenities.append(amenity.get_text())
    return {'Hotel_Name': hotel_name,
            'Price': price,
            'Primary_Rating': primary_rating,
            'Location_Rating': metrics[0],
            'Cleanliness_Rating': metrics[1],
            'Service_Rating': metrics[2],
            'Value_Rating': metrics[3],
            'Num_Reviews': num_reviews,
            'Address': hotel_address,
            'Amenities': amenities}
    
if name == '__main__':
    driver = webdriver.Chrome('./chromedriver')
    wait = WebDriverWait( driver, 10 )
    URL = "https://www.tripadvisor.com/Hotels-g60763-New_York_City_New_York-Hotels.html"

    driver.get(URL)
    # click off screen so that the calendar does not get in the way
    time.sleep(2)
    df = pd.DataFrame(columns=['Hotel_Name',
                            'Price',
                            'Primary_Rating',
                            'Location_Rating',
                             'Cleanliness_Rating',
                             'Service_Rating',
                             'Value_Rating',
                             'Amenities'])
    next_button = driver.find_element_by_class_name('next')
    home_tab = driver.window_handles[0]
    while(next_button != None):
        time.sleep(2)
        hotel_listings = driver.find_elements_by_class_name('respListingPhoto')
        time.sleep(2)
        for hotel in hotel_listings:
            time.sleep(2)
            # stale element reference: https://stackoverflow.com/questions/44724185/element-myelement-is-not-clickable-at-point-x-y-other-element-would-receiv
            driver.execute_script("arguments[0].click();", hotel);
            tabs = driver.window_handles
            tabs.remove(home_tab)
            opened_tab = tabs[-1]
            driver.switch_to.window(opened_tab)
            time.sleep(2)
            df = df.append(scrape_hotel_data(driver), ignore_index=True)
            time.sleep(2)
            driver.close()
            driver.switch_to.window(home_tab)
        time.sleep(2)
        # How to select multiple classes: http://makeseleniumeasy.com/2017/09/26/how-to-locate-web-element-which-has-multiple-class-names/
        next_button = driver.find_element_by_css_selector("a.nav.next")
        driver.execute_script("arguments[0].scrollIntoView()", next_button);
        driver.execute_script("arguments[0].click();", next_button);
        hotel_listings = []

    dump(df, 'tripadvisor_dataframe.pkl', compress=True)
    df.to_csv('tripadvisor_hotels.csv')
