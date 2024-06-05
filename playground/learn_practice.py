
import numpy as np
import pandas as pd
from sklearn.neighbors import (KNeighborsClassifier, KNeighborsRegressor)
from sklearn.preprocessing import LabelEncoder
import csv
import cv2
import colorsys
import PIL
from PIL import ImageColor
import webcolors
"""
tops_knn = KNeighborsClassifier(n_neighbors=10)
with open('user_purchase_data.csv', 'r', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    purchase_data = list(reader)

features = purchase_data[0].keys()
u_data_dict = {f:[] for f in features}

for k in u_data_dict:
    for u_data in purchase_data:
        u_data_dict[k] += [u_data[k]]

test_list = [{k: None for k in p} for p in purchase_data]
i = 0
for dct in test_list:
    for k,v in u_data_dict.items():
        dct[k] = v[i]
    i += 1

df = pd.DataFrame(u_data_dict)
label_encoder = LabelEncoder()
df['color_encoded'] = label_encoder.fit_transform(df['color'])
df['brand_encoded'] = label_encoder.fit_transform(df['brand'])

def convert_color_to_hsv(color_str):
    bgr_color = [int(val) for val in color_str.split(',')]
    
    hsv_color = cv2.cvtColor(np.uint8([[bgr_color]]), cv2.COLOR_BGR2HSV)[0][0]
    return hsv_color

df['color_hsv'] = df['color'].apply(convert_color_to_hsv)

X = df[['price', 'color_encoded', 'brand_encoded', *df['color_hsv']]]
y = df['color_encoded']
knn.fit(X, y)
print(purchase_data == test_list)
"""


# Sample data (replace with your actual data)
data = {
    'user_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    'color': ['red', 'blue', 'green', 'orange', 'black', 'white', 'pink', 'purple', 'yellow', 'gray', 'olive', 'silver', 'aqua', 'navy', 'gold', 'indigo', 'orchid', 'indigo', 'orchid', 'teal'],
    'price': [100, 200, 150, 120, 130, 140, 150, 120, 200, 140, 110, 125, 135, 145, 155, 170, 190, 160, 180, 200],
    'brand': ['A', 'B', 'C', 'A', 'D', 'B', 'A', 'C', 'B', 'A', 'B', 'C', 'D', 'A', 'B', 'C', 'A', 'B', 'C', 'A']
}

df = pd.DataFrame(data)

# Encode categorical data (color and brand)
label_encoder = LabelEncoder()
#df['color_encoded'] = label_encoder.fit_transform(df['color'])
df['brand_encoded'] = label_encoder.fit_transform(df['brand'])

# Function to convert color string to HSV values
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
def hsv_to_color_string(hue, saturation, value):
    
    #color_rgb = ImageColor.hsv_to_rgb((hue, saturation, value))
    #hsv_color = (round(hue * 255), round(saturation * 255), round(value * 255))
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    color_tuple_rgb = (int(r * 255), int(g * 255), int(b * 255))
    color_hexa = ImageColor.getrgbstring(color_tuple_rgb)
    return color_name



# Apply color conversion to a new column
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
X = df[['price', 'brand_encoded']]
y = df[['price', 'brand_encoded']]  # Target variable (color preference)

# Split data into training and testing sets (optional, can be done later)
# from sklearn.model_selection import train_test_split
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Create and train the KNeighborsClassifier model (adjust n_neighbors as needed)
knn = KNeighborsRegressor(n_neighbors=4)
knn.fit(X, y)

# Example: Predict color preference for a new user
new_user_data = {'price': 100, 'brand': 'A', 'color': 'green'}  # Replace with actual data

# Encode categorical data for the new user
#new_user_data['color_encoded'] = label_encoder.transform([new_user_data['color']])[0]
#new_user_data['color_hsv'] = convert_color_to_hsv(new_user_data['color'])

# Convert new user data to a DataFrame (single row)
new_user_df = pd.DataFrame(new_user_data, index=[0])  # Create a single-row DataFrame
new_user_df['brand_encoded'] = label_encoder.fit_transform(new_user_df['brand'])
new_user_df['color_hsv'] = new_user_df['color'].apply(convert_color_to_hsv)

for i in range(len(new_user_df)):
    row = new_user_df.iloc[i]
    hue, saturation, value = row['color_hsv']
    new_user_df.loc[i, 'Hue'] = hue
    new_user_df.loc[i, 'Saturation'] = saturation
    new_user_df.loc[i, 'Value'] = value

# Extract features (X) for the new user
new_user_X = new_user_df[['price', 'brand_encoded']]

# Predict color preference for the new user
predicted_hsv = knn.predict(new_user_X)[0]
predicted_price, predicted_brand = predicted_hsv[-2:]
#predicted_color = label_encoder.inverse_transform([predicted_color_index])[0]
print(predicted_price, predicted_brand)

#print("Predicted color preference for the new user:", predicted_hue, predicted_saturation, predicted_value)

#print("Predcited color name:", hsv_to_color_string(predicted_hue, predicted_saturation, predicted_value))
