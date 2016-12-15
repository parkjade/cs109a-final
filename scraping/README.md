# Housing Information Data Collection

By [Ihsaan Patel](https://github.com/pateli18)

## Description
**get_zipcodes** is a command line program which gets all of the zipcodes for a city through zillow.

**get_ids** is a command line program which gathers all zillow ids and latitude/longitude coordinates for all the zipcodes in your zipcode file.

**scrape_housing_data** is a command line program that gets individual house data for all the house ids in your id file. It does not use the zillow api

**api_housing_data** is a command line program that gets individual house data for all the house ids in your id file. It does use the zillow api. Note that the api has a limit of 1000 calls/day and does not return info for many of the houses

**clean_scraped_data** is a command line program that cleans the data from the scrape_housing_data to be more useful for analysis

## Getting Zip Codes

**Please be sure** to sign up for an API key with Zillow

Enter the following command in command line prompt to run the program.

```console
python get_zipcodes.py <zillow_api_key> <city_name> <save_filepath.csv> 
```

## Getting Zillow IDs

**Be sure to download** the google chrome driver [here](https://sites.google.com/a/chromium.org/chromedriver/downloads) and save it into the same folder as the python file.

For buy_or_rent just enter buy or rent.

Enter the following command in command line prompt to run the program.

```console
python get_ids.py <zip_code_filepath.csv> <save_filepath.csv> <chromedriver_filepath.exe> <buy_or_rent> 
```
## Getting House Data

If you want to using the api do the following:

**Please be sure** to sign up for an API key with Zillow

Enter the following command in command line prompt to run the program.

```console
python api_housing_data.py <zillow_api_key> <ids_filepath.csv> <save_filepath.csv> 
```
If you do not want to using the api do the following:

Enter the following command in command line prompt to run the program.

```console
python scrape_housing_data.py <ids_filepath.csv> <save_filepath.csv> 
```
Then clean the data by entering the following command into the command line.
Row threshold is the minimum number of houses that have to show data for a certain tag, as a % of the total # of rows

```console
python clean_scraped_data.py <scraped_housing_data_filepath.csv> <save_filepath.csv> <row_threshold> 
```