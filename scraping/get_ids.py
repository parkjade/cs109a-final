
import time
from re import findall
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import numpy as np
import sys
from bs4 import BeautifulSoup

def init_driver(chromedriver_filepath):
    driver = webdriver.Chrome(executable_path=chromedriver_filepath)
    driver.wait = WebDriverWait(driver, 10)
    return driver

def zillow(driver, search_terms, buy_or_rent):
    if buy_or_rent == 'buy':
    	driver.get("http://www.zillow.com/homes")
    else:
    	driver.get("http://www.zillow.com/homes/for_rent")
    
    try:
        searchBar = driver.wait.until(EC.presence_of_element_located(
            (By.ID, "citystatezip")))
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "zsg-icon-searchglass")))
        searchBar.clear()
        searchBar.send_keys(search_terms)
        time.sleep(5)
        button.click()
        time.sleep(10)
    except TimeoutException:
        print("search failed")
    

    # Pull the HTML from the search, which contains data on all the search results.
    # HTML from Zillow only displays info of the homes that are shown in the 
    # vertical list on the right side of the webpage (26 homes per page). 
    # The code below scrapes the HTML of the first set (26), then checks to see if there is a 
    # "Next" link at the bottom of the list, if so it clicks it and scrapes the HTML of the
    # the next page (again, 26 listings).  It keeps doing this until it no longer sees a 
    # "Next" link at the bottom.
    rawdata = []
    source = driver.page_source
    rawdata.append(source)    
    try:
        test = driver.find_element_by_class_name('zsg-pagination-next').is_displayed()
        while test == True:
            source = []            
            button = driver.wait.until(EC.element_to_be_clickable(
                (By.CLASS_NAME, 'zsg-pagination-next')))
            button.click()
            time.sleep(5)
            source = driver.page_source
            rawdata.append(source)
            try:
                test = driver.find_element_by_class_name('zsg-pagination-next').is_displayed()
            except:
                print(str(len(rawdata))+" pages of listings found")                
                break
    except:
        print(str(len(rawdata))+" page of listings found")
    urlRaw = driver.current_url

    return rawdata

def convert_rawdata(rawdata):
	ids = []
	latitude = []
	longitude = []
	for segment in range(0, len(rawdata)):
		soup = BeautifulSoup(rawdata[segment], 'lxml')
		for article in soup.findAll('article'):
			if article.has_attr('data-photocount'):
				try:
					ids.append(str(int(article['data-zpid'])))
					latitude.append(article['data-latitude'])
					longitude.append(article['data-longitude'])
#					for span in article.findAll('span'):
#						try:
#							if span['class'][0] == 'zsg-photo-card-price':
#									prices.append(span.string)
#						except KeyError:
#							pass
#					if len(ids) != len(prices):
#						prices.append(np.nan)
				except ValueError:
					pass
	df = pd.DataFrame({'id':ids, 'latitude':latitude, 'longitude':longitude})
	df['id_completed'] = np.nan
	df['id_api_message'] = np.nan
	return df

def get_ids(zip_code_filepath, id_filepath, chromedriver_filepath, buy_or_rent):
	zip_codes = pd.read_csv(zip_code_filepath)
	zips_to_scrape = [zip for zip in zip_codes['zips_to_scrape'].values if zip == zip] + [zip for zip in zip_codes['zips_to_rescrape'].values if zip == zip]
	zips_scraped = [zip for zip in zip_codes['zips_scraped'].values if zip == zip]
	zips_to_rescrape = []
	driver = init_driver(chromedriver_filepath)
	while len(zips_to_scrape) > 0:
		zip_code = zips_to_scrape[0]
		rawdata = zillow(driver, str(int(zip_code)), buy_or_rent)
		id_data = convert_rawdata(rawdata)
		if id_data.empty:
			zips_to_scrape.remove(zip_code)
			zips_to_rescrape.append(zip_code)
		else:
			if len(zips_scraped) == 0:
				id_data.to_csv(id_filepath, mode='w', header=True)
			else:
				id_data.to_csv(id_filepath, mode='a', header=False)
			zips_scraped.append(zip_code)
			zips_to_scrape.remove(zip_code)
		zip_code_data = pd.DataFrame.from_dict({'zips_to_scrape': zips_to_scrape, 'zips_scraped': zips_scraped, 'zips_to_rescrape': zips_to_rescrape}, orient = 'index').transpose()
		zip_code_data.to_csv(zip_code_filepath)
	driver.quit()
	print 'Completed'

zip_code_filepath = sys.argv[1]
id_filepath = sys.argv[2]
chromedriver_filepath = sys.argv[3]
buy_or_rent = sys.argv[4]
get_ids(zip_code_filepath, id_filepath, chromedriver_filepath, buy_or_rent)