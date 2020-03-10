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

# Scrapes data off of each individual hotel page
def scrape_hotel_data(df, driver):
    page = driver.page_source
    soup_expansion = BeautifulSoup(page, 'html.parser')
    address_tag = soup_expansion.find('span', class_='public-business-listing-ContactInfo__ui_link--1_7Zp public-business-listing-ContactInfo__level_4--3JgmI')
    hotel_address = address_tag.get_text()
    hotel_name = driver.title.split('$')[0].title()
    price = re.search('\$(\d+)', driver.title).group(0) 
    primary_rating_tag = soup_expansion.find('span', class_='hotels-hotel-review-about-with-photos-Reviews__overallRating--vElGA')
    primary_rating = primary_rating_tag.get_text()
    ui_bubble_ratings = {}
    for i in range(0, 50, 5):
        ui_bubble_ratings['bubble_' + str(i)] = i * 0.1
    secondary_ratings = soup_expansion.find_all('div', class_='hotels-hotel-review-about-with-photos-Reviews__subratingRow--2u0CJ')
    metrics = []
    for rating in secondary_ratings:
        result = re.search('bubble_(\d\d)', str(rating))
        metrics.append(int(ui_bubble_ratings[result.group(0)]))

    amenities_tag = soup_expansion.find_all('div', class_='hotels-hr-about-amenities-Amenity__amenity--3fbBj')
    amenities = []
    for amenity in amenities_tag:
        amenities.append(amenity.get_text())
    df = df.append({'Hotel_Name': hotel_name, 
                    'Price': int(re.sub(r'[^\d.]', '', price)), 
                    'Primary_Rating': primary_rating, 
                    'Location_Rating': metrics[0],
                    'Cleanliness_Rating': metrics[1],
                    'Service_Rating': metrics[2],
                    'Value_Rating': metrics[3],
                    'Amenities': amenities})
    
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
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight*0.8);')
        time.sleep(2)
        for hotel in hotel_listings:
            hotel.click()
            tabs = driver.window_handles
            tabs.remove(home_tab)
            opened_tab = tabs[0]
            driver.switch_to.window(opened_tab)
            scrape_data(df, driver)
            time.sleep(2)
            driver.close()
            driver.switch_to.window(home_tab)
        next_button = driver.find_element_by_class_name('next')
        next_button.click()

    dump(df, 'tripadvisor_dataframe.pkl', compress=True)
    df.to_csv('tripadvisor_hotels.csv')
