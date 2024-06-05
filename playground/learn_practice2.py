from sklearn import (LabelEncoding, OneHotEncoding)
from sklearn.preprocessing import (StandardScaler, MinMaxScaler)
import csv
import numpy as np
import pandas as pd
from surprise import Reader, Dataset,  

def read_csv(file_name):
    with open(file_name, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        data_dict = list(reader)
    return data_dict

def encode_product_data(data):
    type, df = data
    encode_columns = ['brand', 'type', 'material', 'style', 'occasion']
    onehot_encoder = OneHotEncoder(sparse=False)
    encoded_columns = onehot_encoder.fit_transform(df[encode_columns])
    encoded_dfs = pd.DataFrame(encoded_columns, columns=onehot_encoder.get_feature_name_out(encode_columns))
    return pd.concat([df.drop(columns=encode_columns), encoded_columns], axis=1)


def create_dataframes(product_type):
    if product_type == 'cloth':
        data_dict = read_csv(product_type)
    df = pd.DataFrame(data_dict)
    return df


def remove_targets(df, targets):
    if isinstance(targets, list):
        target_df = df[df['id'].isin(targets)]
        try:
            df.drop(target_df.index, inplace=True)
            return (df, target_df)
        except (ValueError or KeyError) as e:
            return f'removing target failed: {e}'

def normalize(df, columns):
    def standardize(df):
        standardizer = StandardScaler()
        scaled_data = scaler.fit_transform(df)
        return scaled_data
    if column == 'other':
        return standrdize(df['price'])
    else:
        normalizer = MinMaxScaler(feature_range=(0, 1))
        return normalizer.fit_transform(df)


def fit_into_recommender(main_df):
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[['id', 'purchase_history', 'rating', 'brand'
        'type', 'material', 'style', 'occassion']], reader)
    algo = SVD()
    algo.fit(main_df)
    return algo


def knn_CBF(feture_matrix, index, k):
    knn = NearestNeighbors(n_neihbors=k, metric='cosine')
    knn.fit(feature_matrix)
    k_neighbors = knn.kneighbors(feature_matrix[index].reshape(-1, 1))
    neighbors = k_neighbors[1][0]
    neighbor_indices = df[neighbors]
    return neighbor_indices


#apply price filtering after CBF 
def user_preference_CF(algo, user_id, k=10):
    predictions = algo.predict(user_id, target_df['id'])
    top_k = sorted(predictions, key=lambda x: x.est, reverse=True)[:k]
    recommended = [pred.iid for pred in top_k]
    return recommeded
    
    
class Recommender:

    def __init__(self):
        pass

    def 

def main():
    user_id_surprise = target_df.loc[user_id, 'id']

