from sklearn.preprocessing import (StandardScaler, MinMaxScaler)
from sklearn.preprocessing import (LabelEncoder, OneHotEncoder)
from sklearn.neighbors import NearestNeighbors
import random
import csv
#import numpy as np
import pandas as pd
from surprise import Reader, Dataset, SVD 
from surprise.prediction_algorithms.predictions import Prediction



def remove_targets(df, targets):
    if isinstance(targets, list):
        target_df = df[df['id'].isin(targets)]
        try:
            df.drop(target_df.index, inplace=True)
            return (df, target_df)
        except (ValueError or KeyError) as e:
            return f'removing target failed: {e}'


class BaseRecommender:

    def __init__(self, file_name, algo=None):
        data_dict = self.read_csv(file_name)
        self.__df = self.create_dataframes(data_dict)
        if algo:
            self.__algo = algo
    
    def read_csv(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            data_dict = list(reader)
        return data_dict


    def create_dataframes(self, data_dict, product_type='cloth'):
        if product_type == 'cloth':
            df = pd.DataFrame(data_dict)
            return df

    def encode_df(self, df):
        encode_columns = ['brand', 'type', 'material', 'style', 'occassion']
        onehot_encoder = OneHotEncoder(sparse=False)
        encoded_columns = onehot_encoder.fit_transform(df[encode_columns])
        encoded_dfs = pd.DataFrame(encoded_columns, columns=onehot_encoder.get_feature_names_out(encode_columns))
        return pd.concat([df.drop(columns=encode_columns), encoded_dfs], axis=1)


    def normalize(self, df, columns):
        normalizer = MinMaxScaler(feature_range=(0, 1))
        normalized_column = normalizer.fit_transform(columns)
        normalized_col_df = pd.DataFrame(normalized_column, columns=columns)
        normalized_df = pd.concat([df.drop('price'), normalized_col_df], axis=1)
        return normalized_df


class ContentBasedRecommender:

    def knn_CBF(self, feature_matrix, product_id, k):
        knn = NearestNeighbors(n_neighbors=k, metric='cosine')
        knn.fit(feature_matrix)
        index = feature_matrix[feature_matrix['product_id'] == '5'].index[0]
        k_neighbors = knn.kneighbors(feature_matrix.loc[index].values.reshape(-1, 36))
        neighbors = k_neighbors[1][0]



class UserBasedRecommender:


    def fit_into_recommender(self):
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(self.df[['user_id', 'product_id', 'rating']], reader)
        self.algo = SVD()
        self.algo.fit(data.build_full_trainset())


    def user_preference_CF(self, user_id, product_ids):
        predictions = product_ids.apply(lambda x: self.algo.predict(user_id, x))
        top_k = sorted(predictions, key=lambda x: x.est, reverse=True)[:k]
        return predictions


def random_rating(amount):
    user_ratings = []
    for i in range(amount):
        user_ratings.append({'user_id': random.randrange(1, 10, step=1),
            'product_id': random.randrange(1, 15, step=1),
            'rating': random.randrange(1, 5, step=1)
        })
    return user_ratings


def main_CF(product_id, **kwargs):
    filtering =  kwargs.get('filtering', None)
    if filtering and filtering == 'cbf':
        purchases = read_csv('purchase_data.csv')
        if filtering == 'cbf':
            purchases = [{k: data[k] for k in data if k != 'user_id'} for data in purchases]
        data_frames = create_dataframes(purchases)
        encoded_df = encode_df(data_frames)
        if filtering == 'cbf':
            product_id = kwargs.get('product_id')
            knn_CBF(encoded_df, product_id, 6)
    else:
        ratings = random_rating(100)
        for rating in ratings:
            if rating['user_id'] == 5:
                print(rating['product_id'], ': ', rating['rating'])
        recc = UserBasedRecommender('purchase_data.csv')
        recc.fit_into_recommender()
        df = create_dataframes(ratings)
        user_id = kwargs.get('user_id')
        recommended = recc.user_preference_CF(user_id, df['product_id'])
        #print(neighbors)
    #user_id_surprise = target_df.loc[user_id, 'id']

main_CF(3, filtering='cf', user_id=5)
