import os
import pandas as pd
from weaviate import Client, AuthApiKey  # Import AuthApiKey
from dotenv import load_dotenv

load_dotenv()

# Weaviate Configuration
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")  # Get the API key from environment variable

auth = AuthApiKey(WEAVIATE_API_KEY)  # Create an authentication object
client = Client(WEAVIATE_URL, auth_client_secret=auth)  # Pass authentication to the client


# Load your processed DataFrame (after dropping and renaming columns)
df = pd.read_csv("/Users/adakibet/cosmology/platform/refined.csv")
# Convert date to RFC3339 format
df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
print(df.shape)
df.dropna(subset=['date'], inplace=True)
print(df.shape)
# Iterate through rows and create JobPosting objects
for index, row in df.iterrows():
    # Find all NaN values in the row
    nan_cols = row.index[row.isnull()].tolist()
    # Replace NaN values with empty strings
    for col in nan_cols:
        row[col] = ""

    # Now load the modified row
    client.data_object.create(
        {
            "title": row["title"],
            "company": row["company"],
            "company_link": row["company_link"],
            "location": row["location"],
            "date_posted": row["date"],  # Assuming it's already in ISO 8601 format
            "apply_link": row["apply_link"],
            "post_link": row["post_link"],
            "seniority_level": row["seniority_level"],
            "employment_type": row["employmnet_type"],
            "description": row["description"]
        },
        "JobPosting",
        # get_uuid(row["title"])  # Use job title as unique identifier
    )


