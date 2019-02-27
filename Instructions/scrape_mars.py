import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
from splinter import Browser
import pandas as pd
from splinter.exceptions import ElementDoesNotExist

##########################################

def scrape_info():
    #####first thing####
    url="https://mars.nasa.gov/news/"

    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    list_title=soup.find_all(class_="slide")

    list_help=list_title[0]

    news_p=list_help.div.div.div.text

    news_title=soup.find_all(class_="content_title")[0].a.text
    ####This is the section for the splinter####
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    mars_visit_url="https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(mars_visit_url)

    html = browser.html
    mars_soup = BeautifulSoup(html, 'html.parser')
    help_space=mars_soup.find('a',class_='button fancybox')['data-fancybox-href']
    featured_image_url ="https://www.jpl.nasa.gov"+help_space

    #### Mars Weather Tweet ####
    mars_w_twitter="https://twitter.com/marswxreport?lang=en"
    browser.visit(mars_w_twitter)
    html_tweet=browser.html
    mars_tweet_soup=BeautifulSoup(html_tweet,'html.parser')
    help_weather=mars_tweet_soup.find('ol',class_="stream-items js-navigable-stream")
    helper_location=help_weather.li.div.p.text.find('pic.')
    mars_weather=help_weather.li.div.p.text[:helper_location]


    ####Mars Facts####
    mars_facts_url="https://space-facts.com/mars/"
    mars_facts_table=pd.read_html(mars_facts_url)
    mars_facts_html=mars_facts_table[0].to_html()


    ####Mars Hemispheres####
    hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemisphere_url)

    hemisphere_html = browser.html
    soup = BeautifulSoup(hemisphere_html, 'html.parser')

    search_results = soup.find_all('div', class_='item')

    hemisphere_image_urls=[]
    hemisphere_titles_list=[]
    url_list=[]

    for result in search_results:
        url_list.append(result.div.a['href'])
        hemisphere_titles_list.append(result.h3.text)#.split()[0]+" "+test_link.h3.text.split()[1])

    hemisphere_url_list = ['https://astrogeology.usgs.gov' + url for url in url_list]

    titles_and_urls = zip(hemisphere_titles_list, hemisphere_url_list)
    counter=0


    try:
        for title_url in titles_and_urls:
            browser.click_link_by_partial_text(hemisphere_titles_list[counter])
            temp_soup=BeautifulSoup(browser.html,'html.parser')
            test_find=temp_soup.find_all('ul')
            hemisphere_image_urls.append({'title':hemisphere_titles_list[counter],'img_url':test_find[-2].li.a['href']})
            browser.visit(hemisphere_url)
            counter+=1
    except ElementDoesNotExist:
        print("Scraping Complete")
    
    ###completed getting the dictionary###
    final_dict={'news_p':news_p,"news_title":news_title,
    "featured_image_url":featured_image_url,
    "mars_weather":mars_weather,
    "mars_facts_html":mars_facts_html,
    "hemisphere_image_urls":hemisphere_image_urls}
    browser.quit()
    return final_dict