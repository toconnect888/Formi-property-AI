import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import numpy as np
# Clean data in Python
def normalize_columns(df):
    df.columns = (
        df.columns
        .str.strip() #Removes leading/trailing white spaces before and after the text like tabs(\t), new lines \n, and emptry space
        .str.lower()
        .str.replace(r"[^0-9a-z]+", "_", regex= True)  # ^\w→ anything that's NOT a letter, number, underscore, + →one or more time, regex=true, it is a regular expression(regex pattern), not a string
        .str.strip("_")
        )
        
    return df

cols_to_use = ['Property Address','Submarket Name', 'Market', 'Property Type', 'Size','Sale Price','Sale Date', 'Age', 'Price Per SF (Net)', 'Building Class', 'Typical Floor (SF)','Zoning', 'Parking Ratio' , 'Number Of Tenants']
raw_df = pd.read_excel("CostarExport.xlsx", usecols = cols_to_use)
df = raw_df.copy()  #make a working copy to not mess up with original data
df= normalize_columns(df)
print("Columns:", df.columns.tolist())

critical_cols = ['sale_price', 'size']
df= df.dropna(subset = critical_cols)

if 'property_address' in df.columns:
    df = df.drop_duplicates(subset=['property_address','size'])
else:
    df = df.drop_duplicates()  # fallback: drop exact duplicate rows

numeric_cols = df.select_dtypes(include=['number']).columns  #return data colomns names ['size_sf', 'net_rent', 'additional_rent', 'sale_price']
for col in numeric_cols:
    df[col +'missing'] = df[col].isna().astype(int)
    
#df[numeric_cols].isna().sum() #how many missing values each numeric column has.

text_cols = df.select_dtypes(include=['object']).columns
df[text_cols] = df[text_cols].apply(lambda x: x.str.strip())
# print("Rows:", len(df))
#print("Numeric columns:", numeric_cols)
# print("Missing values per column:\n", df.isna().sum())
# print(df.iloc[:,:8].sample(5))
# print(df.dtypes)

#Method 1:  Median price and average price per sf
numeric_cols = ['sale_price', 'size','age','typical_floor_sf','parking_ratio','number_of_tenants']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce') # convert nerumic columns to numeric, coerce errors to NaN

df['price_per_sf'] = df['sale_price'] / df['size']
df = df.dropna(subset=['price_per_sf'])

mean_price_per_sf = df['price_per_sf'].mean()
median_price_per_sf = df['price_per_sf'].median()
print(f"Mean Price Per SF : ${mean_price_per_sf:,.2f}")
print(f"Median Price Per SF : ${median_price_per_sf:,.2f}")

new_listing_size = 5000  # SF of the new property
# Using mean
estimated_price_mean = mean_price_per_sf * new_listing_size

# Using median
estimated_price_median = median_price_per_sf * new_listing_size

print(f"Estimated Price (Mean Price/SF): ${estimated_price_mean:,.0f}")
print(f"Estimated Price (Median Price/SF): ${estimated_price_median:,.0f}")

# option 2  Filter past properties within +/- 20% of new listing size
size_lower = new_listing_size * 0.8
size_upper = new_listing_size * 1.2
similar_properties = df[(df['size'] >= size_lower) & (df['size'] <= size_upper)]
print(similar_properties[['property_address','size','sale_price','price_per_sf','age','building_class','number_of_tenants']])

estimated_price_similar_mean = similar_properties['price_per_sf'].mean() * new_listing_size
estimated_price_similar_median = similar_properties['price_per_sf'].median()* new_listing_size
print(f"Estimated Price - similar sizes (Mean): ${estimated_price_similar_mean:,.0f}")
print(f"Estimated Price - similar sizes (Median): ${estimated_price_similar_median:,.0f}")

# Method 3: Random Forest Model
catetorical_cols = ['building_class']
df = df[df['property_type'].isin(['Retail'])] ## Keep only rows where property_type is Office or Retail
df = df.reset_index(drop=True)
#print (df.iloc[:,:8])  #print first 8 columns
numeric_cols = ['size','age','number_of_tenants','typical_floor_sf','parking_ratio']
x= df.drop(columns=['sale_price','property_address','sale_date','submarket_name','market',
    'zoning','agemissing','sizemissing','typical_floor_sfmissing','parking_ratiomissing',
    'number_of_tenantsmissing','sale_pricemissing','agemissing','price_per_sf_netmissing',
    'price_per_sf_net','property_type','price_per_sf'])
print(f"Factors considered in models:", x.columns.tolist())
y_lr = df['sale_price']  #target variable is sale price

# Fill numeric columns that has NaN values with median value
# num_imputer = SimpleImputer(strategy='median')
# x[numeric_cols] = pd.DataFrame(num_imputer.fit_transform(x[numeric_cols]), columns=numeric_cols, index=x.index)

# Clean categorical columns
x[catetorical_cols] = x[catetorical_cols].apply(lambda col: col.astype(str).str.strip())
print(df['building_class'].value_counts())

x[catetorical_cols] = x[catetorical_cols].replace({'': pd.NA})
catetorical_cols = [col for col in catetorical_cols if not x[col].isna().all()]  ## Remove categorical columns that are completely missing

cat_imputer = SimpleImputer(strategy='most_frequent')
x[catetorical_cols] = pd.DataFrame(cat_imputer.fit_transform(x[catetorical_cols]), columns=catetorical_cols, index=x.index)

x = pd.get_dummies(x, columns=catetorical_cols, drop_first=True)
dummy_building = pd.get_dummies(df['building_class'], drop_first=True)
print(dummy_building.columns.tolist())


# Predict price for a new listing
new_property_features = pd.DataFrame(0.0, index=[0], columns=x.columns) #only one row, index 0, all columns from x, initialized to 0.0 (floart type)
new_property_features.loc[0, ['size', 'age', 'typical_floor_sf', 'parking_ratio', 'number_of_tenants']] = [
    new_listing_size, 50, 1500, 0.5, 0]  # Set numeric features for the new property
# Fill categorical dummies if needed # Example: building_class_B = 1 if the new listing is class B, Example: property_type_Retail = 1 if property type is Retail
if 'building_class_B' in new_property_features.columns:
    new_property_features.at[0, 'building_class_B'] = 0
if 'building_class_C' in new_property_features.columns:
    new_property_features.at[0, 'building_class_C'] = 1

# random forest model  - learning from many real examples instead of forcing a straight-line formula.

y_rf = df['sale_price']  #target variable is sale price
rf_model = RandomForestRegressor(n_estimators=300, random_state=42, min_samples_leaf=5)

#  ask 300 individual trees to make decisions; Each final decision (leaf) must be based on at least 5 properties, random
rf_model.fit(x, y_rf)
predicted_price_rf = rf_model.predict(new_property_features)[0]

#pred_price_per_sf = rf_model.predict(new_property_features)[0]
#predicted_price_rf = pred_price_per_sf * new_property_features.at[0, 'size']

print(f"Estimated Price-Random Forest: ${predicted_price_rf:,.0f}")
feature_importance = pd.Series(
    rf_model.feature_importances_,
    index=x.columns
).sort_values(ascending=False)

print(feature_importance.head(10))

# SSplit/test
x_train, x_test, y_train, y_test = train_test_split(x, y_rf, test_size=0.2, random_state=42) #use 20% for testing
rf_model.fit(x_train, y_train)

y_pred = rf_model.predict(x_test)
print("Predicted vs Actual Prices:")
for actual, predicted in zip(y_test.head(10), y_pred[:10]):
    print(f"Actual: ${actual:,.0f}, Predicted: ${predicted:,.0f}")
mae = mean_absolute_error(y_test, y_pred)
print(f"MAE: ${mae:,.0f}")
r2 = r2_score(y_test, y_pred)

mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse) 
#print(f"RMSE: ${rmse:,.0f}")
print(f"R²: {r2:.2f}")