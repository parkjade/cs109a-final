import pandas as pd
import requests
import sys
from xml.etree import ElementTree

house_parameters = ['zpid', 'price', 'homeDescription', 'neighborhood', 'schoolDistrict', 'elementarySchool', 'middleSchool']
address_parameters = ['street', 'zipcode', 'city', 'state', 'latitude', 'longitude']
house_details_parameters = ['useCode', 'bedrooms', 'bathrooms', 'finishedSqft', 'lotSizeSqFt', 'yearBuilt', 'yearUpdated', 'numFloors', 'basement', 'roof', 'view', 'parkingType', 'heatingSources', 'heatingSystem', 'appliances', 'floorCovering', 'rooms']


def retrieve_individual_house_data(house_data_object, house_parameters, address_parameters, house_details_parameters):
    house_data = [] 
    for element in house_parameters:
        field = house_data_object.find(element)
        field_value = None if field is None else field.text
        house_data.append(field_value)
    for element in address_parameters:
        field = house_data_object.find('address').find(element)
        field_value = None if field is None else field.text
        house_data.append(field_value)
    for element in house_details_parameters:
        field = house_data_object.find('editedFacts').find(element)
        field_value = None if field is None else field.text
        house_data.append(field_value)
    return house_data

def get_housing_data(api_key, ids_filepath, housing_data_filepath, house_parameters, address_parameters, house_details_parameters):
    ids = pd.read_csv(ids_filepath)
    ids = ids.drop_duplicates(subset=['id'], keep='last')
    uncompleted_ids = ids[ids['id_api_message'] != ids['id_api_message']]
    zpids_list = [int(id) for id in uncompleted_ids['id'].values.tolist()]
    latitude_list = [latitude for latitude in uncompleted_ids['latitude'].values.tolist()]
    longitude_list = [longitude for longitude in uncompleted_ids['longitude'].values.tolist()]
    ids_completed = ids[ids['id_api_message'] == ids['id_api_message']].shape[0]
    for zpid in zpids_list:
        zillow_url = 'http://www.zillow.com/webservice/GetUpdatedPropertyDetails.htm?zws-id={0}&zpid={1}'.format(api_key, zpid)
        print zillow_url
        response = requests.get(zillow_url)
        tree = ElementTree.fromstring(response.content)
        message = tree.find('message').find('text').text
        print message, zpid
        code = int(tree.find('message').find('code').text)
        if code == 0:
            house_data = retrieve_individual_house_data(tree, house_parameters, address_parameters, house_details_parameters)
            housing_dataframe = pd.DataFrame(housing_data, columns = house_parameters + address_parameters + house_details_parameters)
            if ids_completed > 0:
                housing_dataframe.to_csv(housing_data_filepath, mode='a', header=False)
            else:
                housing_dataframe.to_csv(housing_data_filepath, mode='w', header=True)
                ids_completed +=1
        ids.loc[ids['id'] == zpid, 'id_api_message'] = message
        ids.to_csv(ids_filepath)
    print 'Completed'

api_key = sys.argv[1]
id_filepath = sys.argv[2]
housing_data_filepath = sys.argv[3]
get_housing_data(api_key, id_filepath, housing_data_filepath, house_parameters, address_parameters, house_details_parameters)