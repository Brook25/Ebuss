from PIL import ImageColor
import cv2  # OpenCV for color space conversion
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import (LabelEncoder, OneHotEncoding)
import colorsys
import webcolors


class BaseRecommender:

    @classmethod
    def get_csv_data(cls):

        try:
            file_name = cls.__name__ + ".csv"
            with open('user_purchase_data.csv', 'r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                purchase_data = list(reader)

            features = purchase_data[0].keys()
            data_dict = {f:[] for f in features}
            for k in data_dict:
                for data in purchase_data:
                    data_dict[k] += [data[k]]
            cls.data_frame = pd.DataFrame(data_dict)
        except Exception as e:
            raise Exception("Couldn't create dataframe (Error occured):" + str(e))


    @staticmethod
    def labelize(data):
        encoder = OneHotEncoder(sparse=False)
        encoder.fit(data)
        return encoder

        

class EDeviceRecommender(BaseRecommender):
    
    __X = ['encoded_brand', 'processing_power', 'memory', 'storage_space', 'encoded_storage_type', 'display', 'weight']
    __y = EDeviceRecommender._XX
    BRANDS = ['Samsung', 'Apple', 'Microsoft', 'Acer', 'Toshiba', 'HP', 'Dell', 'Lenovo', 'Huwaei', 'other']
    __ENCODERS_OBJS = {}
    __knn = KNeighborsRegressor(n_neighbors=20)

    def __init__(self, user):
        EDeviceRecommender.get_csv_data()
        # Get user data
        if not (isinstance, user, User):
            raise(ValueError, "user should be an instance of the User class")
        self.user = user
        new_user_data = {att: getattr(att, self.user, None) for att in self.__y}
        self.__new_user_df = pd.DataFrame(new_user_data, index=[0])


    #fit knn with dataframes
    def fit(self):

        #  data to be encoded should be transformed
        cls.__ENCODER_OBJS['brand'] = labelize(cls.BRANDS)
        cls.__ENCODER_OBJS['storage_type'] = labelize(['HDD', 'SSD'])
        cls.data_frame['encoded_brands'] = cls.__ENCODER_OBJS['brand'].transform(cls.data_frame['brand'])
        cls.data_frame['encoded_storage_types'] = cls.__ENCODERS['encoded_brands'].transform(cls.data_frame['storage_types'])
        X = cls.data_frame[cls.__X]
        y = cls.data_frame[cls.__y]
        cls.knn.fit(X, y)
        #+ then start fitting
    
    # use user data and predict
    def predict(self):
        
        if brand_encoder := cls.__ENCODER_OBJS.get('brand', None):
            self.__new_user_df['encoded_brands'] = brand_encoder.transform(self.new_user_df['brand'])
        else:
            raise(ValueError, "No brand label encoder found.")

        if storage_type_encoder := cls.__ENCODER_OBJD.get('storage_type', None):
            self.__new_user_df['encoded_storage_type'] = storage_type_encoder.transform(self.__new_user_df['storage_types'])
        else:
            raise(ValueError, "No storage type encoder found.")
        
        try:
            new_user_X = self.__new_user_df[[cls.__X]]
            predicted_values = self.__knn.predict(new_user_X)
            return predicted_values
        except Exception as e:
            raise Exception("prediction process couldn't complete succefully. Error: " + str(e))


    class __ColorConverter:
        
        def __init__(self, color):
            self.__color = color
        def convert_color_to_hsv(color_str):
            # Convert color string to BGR format (OpenCV uses BGR)
            #rgb_color = ImageColor.getrgb(color_str.lower())
            rgb_color = webcolors.name_to_rgb(color_str)
            r = rgb_color.red / 255.0
            g = rgb_color.green / 255.0
            b = rgb_color.blue / 255.0
            #bgr_color = rgb_color[::-1]

            # Convert BGR to HSV
            #hsv_color = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2HSV)[0][0]
            hsv_color = colorsys.rgb_to_hsv(r, g, b)
            return hsv_color

        #Needs a closer look
        def hsv_to_(hue, saturation, value):

            #color_rgb = ImageColor.hsv_to_rgb((hue, saturation, value))
            #hsv_color = (round(hue * 255), round(saturation * 255), round(value * 255))
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            color_tuple_rgb = (int(r * 255), int(g * 255), int(b * 255))
            color_name = webcolors.rgb_to_name(color_tuple_rgb)
            return color_name



        # Apply color conversion to a new column
        def add_hsv_to_df(self, obj):
            df['color_hsv'] = df['color'].apply(convert_color_to_hsv)

            print('==>', convert_color_to_hsv('red'))

            for i in range(len(df)):
                row = df.iloc[i]
                hue, saturation, value = row['color_hsv']
                df.loc[i, 'Hue'] = hue
                df.loc[i, 'Saturation'] = saturation
                df.loc[i, 'Value'] = value

            print(df)

            # Separate features (X) and target (y) for KNN
            X = df[['Hue', 'Saturation', 'Value']]
            y = df[['Hue', 'Saturation', 'Value']]  # Target variable (color preference)

            

class ClothRecommeder(BaseRecommender):
    
    __X = ['color', 'price', 'brand']
    __y = ['color', 'price', 'brand']
    BRANDS = ['Samsung', 'Apple', 'Microsoft', 'Acer', 'Toshiba', 'HP', 'Dell', 'Lenovo', 'Huwaei', 'other']
    __ENCODERS = {}
    __knn = KNeighborsRegressor(n_neighbors=20)
   

   def __init__(self, user):
       pass

   def fit(self):
       pass
   
   def predict(self):
       pass
