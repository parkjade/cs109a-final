from urllib import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import sys

def get_data(soup, zpid, latitude, longitude):
    print zpid
    features = {}
    for div in soup.select("div[class^=fact-group-container]"):
        features[div.find('h3').string] = [li.string for li in div.findAll('li')]
    address_2 = soup.find("span", { "class" : "zsg-h2 addr_city" }).string.replace(',', '').split(' ')
    city = str(address_2[0])
    try:
        state = str(address_2[1])
    except:
        state = ''
    try:
        zipcode = str(address_2[2])
    except:
        zipcode = np.nan
    street_address = str(soup.find("header", { "class" : "zsg-content-header addr" }).find("h1").strings.next())
    description = u''.join(soup.select("div[class*=hdp-header-description]")[1].find('div', {'class' : 'notranslate zsg-content-item'}).text).encode('utf-8').strip()
    basic_info = [span.string for span in soup.findAll("span", {"class" : "addr_bbs"})]
    try:
        bed = basic_info[0]
    except:
        bed = np.nan
    try:
        bath = basic_info[1]
    except:
        bath = np.nan
    try:
        sqft = basic_info[2]
    except:
        sqft = np.nan        
    try:
        price = str(soup.find('div', {'class' : 'main-row  home-summary-row'}).text)
    except:
        price = np.nan
    data = [zpid, latitude, longitude, price, bed, bath, sqft, description, street_address, city, state, zipcode, features]
    return data

def get_housing_data(ids_filepath, housing_data_filepath):
    ids = pd.read_csv(ids_filepath)
    ids = ids.drop_duplicates(subset=['id'], keep='last')
    uncompleted_ids = ids[ids['id_completed'] != ids['id_completed']]
    zpids_list = [int(id) for id in uncompleted_ids['id'].values.tolist()]
    latitude_list = [latitude for latitude in uncompleted_ids['latitude'].values.tolist()]
    longitude_list = [longitude for longitude in uncompleted_ids['longitude'].values.tolist()]
    ids_completed = ids[ids['id_completed'] == ids['id_completed']].shape[0]
    for i, zpid in enumerate(zpids_list):
        df_data = []
        url = 'http://www.zillow.com/homes/for_sale/{0}_zpid/'.format(zpid)
        html = urlopen(url)
        soup = BeautifulSoup(html, 'lxml')
        print i #soup
        if soup.find('main', {'class' : 'zsg-layout-bc-b'}) != None:
            latitude = latitude_list[i]
            longitude = longitude_list[i]
            df_data.append(get_data(soup, zpid, latitude, longitude))
            df = pd.DataFrame(df_data, columns = ['zpid', 'latitude', 'longitude', 'price', 'bed', 'bath', 'sqft', 'description', 'street_address', 'city', 'state', 'zipcode', 'features'])
            if ids_completed > 0:
                df.to_csv(housing_data_filepath, mode='a', header=False)
            else:
                df.to_csv(housing_data_filepath, mode='w', header=True)
                ids_completed +=1
            ids.loc[ids['id'] == zpid, 'id_completed'] = 0
        else:
            ids.loc[ids['id'] == zpid, 'id_completed'] = 1
        ids.to_csv(ids_filepath)
    print 'Complete'

ids_filepath = sys.argv[1]
housing_data_filepath = sys.argv[2]
get_housing_data(ids_filepath, housing_data_filepath)