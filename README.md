# AI-Insights-Python-SQL-data-analysis

#How to use SQL- Option 1 local db file

Open local db file:

raw_df = pd.read_excel("CostarExport.xlsx")
df = raw_df.copy()  #make a working copy to not mess up with original data
df["size"]=pd.to_numeric(df["size"]),errors="coerce")  
# convert values like 12,500 to 12500, If conversion fails: Python replaces it withNaN (missing value)


conn = sqlite3.connect("data.db")


df.to_sql(
    name="Property_Data",
    con=conn,
    if_exists="replace",  # or "append"
    index=False
)

df = pd.read_sql("SELECT * FROM Property_Data LIMIT 200", conn) #Looks inside the database,Goes to a table called Property_Data, Takes only the first 5 rows
print(df)

print("Excel data imported successfully!")
conn.close()

# Step 1: Activate your virtual environment (optional but recommended)
python -m venv formi_venv      # create virtual environment named 'venv'
formi_venv\Scripts\Activate.ps1  # activate it

# install dependables: 
pip install -r requirements.txt

# for Linix Ubuntu 22.04
sudo ACCEPT_EULA=Y apt install msodbcsql18


# Always install pyodbc after installing unixodbc-dev and ODBC driver on Linux

# connect to Azure server 
1. option 1 (SQL authentication enabled must ) 
 ------------------------------
# Azure SQL connection details
# ------------------------------
server = "propertyai.database.windows.net"
database = "Property Data"
username = "xxxx"          # SQL login you created
password = "xxx"             # SQL login password
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

2. Option 2 - AAD 

# Replace with your database details , this is using Azure database
server = "propertyai.database.windows.net"
database = "Property Data"
driver = "ODBC Driver 18 for SQL Server"
excel_file = "CostarExport.xlsx" 

# Build connection string with AAD interactive login
params = urllib.parse.quote_plus(
    f"Driver={driver};"
    f"Server={server};"
    f"Database={database};"
    "Authentication=ActiveDirectoryInteractive;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)



Model: 
Value=Net Operating Income (NOI)/Cap Rate
Value=Cap Rate/ Net Operating Income (NOI)
	​
Model market rent & vacancy
Model cap rate independently

Everything else exists to:


# Remove a column called 'extra_info'
df = df.drop('extra_info','old_rent", axis=1)

# Remove rows where 'sale_price' is missing, dropna is a special version of drop for missing values
df = df.dropna(subset=['sale_price']) 
