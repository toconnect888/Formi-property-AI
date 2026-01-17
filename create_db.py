#Create a database & tabl
import pandas as pd
from sqlalchemy import create_engine, text
import urllib
import pyodbc
print(pyodbc.drivers())

# Replace with your database details , this is using Azure database
# Replace with your database details , this is using Azure database
server = "propertyai.database.windows.net"
database = "Property Data"
username = "cjab999"          # SQL login you created
password = "Tofi69ue88!"             # SQL login password
driver = "ODBC Driver 18 for SQL Server"

# Build the connection string
params = urllib.parse.quote_plus(
    f"Driver={driver};"
    f"Server={server};"
    f"Database={database};"
    f"UID={username};"
    f"PWD={password};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

excel_file = "CostarExport.xlsx" 

# Test connection
try:
    df = pd.read_excel(excel_file)
    print(f"'{excel_file}' loaded successfully!")
except Exception as e:
    print("Failed to load Excel:")
    print(e)
    exit()

table_name = "Property_Data"  # new table name

try:
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",  # replace if the table exists
        index=False
    )
    print(f"Data uploaded to table '{table_name}' successfully!")
except Exception as e:
    print("❌ Failed to upload data:")
    print(e)


# Clean data in Python
def normalize_columns(df):
    df.columns = (
        df.columns
        .str.strip() #Removes leading/trailing white spaces before and after the text like tabs(\t), new lines \n, and emptry space
        .str.lower()
        .str.replace(r"[^\W]+", "_", regex= True)  # ^\w→ anything that's NOT a letter, number, underscore, + →one or more time, regex=true, it is a regular expression(regex pattern), not a string
        .str.strip("_")
        )
    return df

cols_to_use = ['Property Address','Submarket Name', 'Market', 'Size','Sales Price','Sale Date', 'Age', 'Price Per SF(Net)', 'Builidng Class', 'Typica Floor(SF)','Zoning', 'Parking Ratio' , 'Number of Tenants"']
raw_df = pd.read_excel("CostarExport.xlsx", usecols = cols_to_use)
df = raw_df.copy()  #make a working copy to not mess up with original data
df= normalize_columns(df)

critical_cols = ['sales_price', 'size']
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
print("Rows:',len(df)")
print("Numeric columns:", numeric_cols)
print("Missing values per column:\n", df.isna().sum())