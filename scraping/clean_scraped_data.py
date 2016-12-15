import ast
import pandas as pd
import numpy as np
import sys

features_dict = {}
features_set = set()
tags_dict = {}
tags = set()

def get_features(row):
    features = ast.literal_eval(row['features'])
    global features_dict
    features_dict[row['zpid']] = features
    global features_set
    features_set = set(features.keys()) | features_set

def apply_features(zpid, feature):
    global features_dict
    try:
        return features_dict[zpid][feature]
    except:
        return np.nan

def get_tags(zpid, row,  features_set):
    global tags
    global tags_dict
    individual_dict = {}
    for features in features_set:
	        for feature in row[features]:
	            if ':' in feature:
	                individual_dict.update({feature[:feature.find(':')] : feature[feature.find(':') + 1:]})
	                tags = tags | set([feature[:feature.find(':')]])
    tags_dict[zpid] = individual_dict

def apply_tags(zpid, tag):
    global tags_dict
    try:
        return tags_dict[zpid][tag]
    except:
        return np.nan

def format_features(features):
    new_features = []
    if (features == features) & (features is not None):
        for feature in features:
            if feature is not None:
                new_features.append(u''.join(feature).encode('utf-8').strip())
    return new_features

def format_dataframe(housing_data_filepath, altered_housing_data_filepath, row_threshold):
    df = pd.read_csv(housing_data_filepath)
    df.apply(lambda row: get_features(row), axis = 1)
    global features_set
    for feature in features_set:
        df[feature] = df['zpid'].apply(lambda zpid: apply_features(zpid, feature))
        df[feature] = df[feature].apply(lambda features: format_features(features))
    df.apply(lambda row: get_tags(row['zpid'], row, features_set), axis = 1)
    for tag in tags:
        df[tag] = df['zpid'].apply(lambda zpid: apply_tags(zpid, tag))
    df['features_string'] = df['features'].apply(lambda features: str(features))
    df = df.dropna(thresh=df.shape[0] * float(row_threshold), axis=1)
    df.to_csv(altered_housing_data_filepath)
    print 'Complete'

housing_data_filepath = sys.argv[1]
altered_housing_data_filepath = sys.argv[2]
row_threshold = sys.argv[3]

format_dataframe(housing_data_filepath, altered_housing_data_filepath, row_threshold)
