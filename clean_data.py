import pandas as pd

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

cols_to_use = ['Property Address','Submarket Name', 'Market', 'Size','Sale Price','Sale Date', 'Age', 'Price Per SF (Net)', 'Building Class', 'Typical Floor (SF)','Zoning', 'Parking Ratio' , 'Number Of Tenants']
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
print("Rows:", len(df))
print("Numeric columns:", numeric_cols)
print("Missing values per column:\n", df.isna().sum())
print(df.sample(5))
print(df.dtypes)

#Method 1:  Median price and average price per sf
df['sale_price'] = pd.to_numeric(df['sale_price'], errors='coerce')
df['size'] = pd.to_numeric(df['size'], errors='coerce')
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
print(similar_properties[['property_address','size']])
estimated_price_similar_mean = similar_properties['price_per_sf'].mean() * new_listing_size
estimated_price_similar_median = similar_properties['price_per_sf'].median()* new_listing_size
print(f"Estimated Price - similar sizes (Mean): ${estimated_price_similar_mean:,.0f}")
print(f"Estimated Price - similar sizes (Median): ${estimated_price_similar_median:,.0f}")


