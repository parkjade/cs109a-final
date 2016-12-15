import requests
from xml.etree import ElementTree
import pandas
import sys
import numpy as np

def get_zipcodes(api_key, city, filepath):
	zillow_url = 'http://www.zillow.com/webservice/GetRegionChildren.htm?zws-id={0}&state=newyork&city={1}&childtype=zipcode'.format(api_key, city)
	response = requests.get(zillow_url)
	tree = ElementTree.fromstring(response.content)
	zip_codes = [region.find('name').text for region in tree.find('response').find('list').findall('region')]
	zip_code_data = pandas.DataFrame(zip_codes, columns = ['zips_to_scrape'])
	zip_code_data['zips_scraped'] = np.nan
	zip_code_data['zips_to_rescrape'] = np.nan
	zip_code_data.to_csv(filepath)
	print 'Complete'

api_key = sys.argv[1]
city = sys.argv[2]
filepath = sys.argv[3]

get_zipcodes(api_key, city, filepath)