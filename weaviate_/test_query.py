import os
import pandas as pd
from weaviate import AuthApiKey
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

# Weaviate Configuration
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")  # Get the API key from environment variable

auth = AuthApiKey(WEAVIATE_API_KEY)  # Create an authentication object
client = Client(WEAVIATE_URL, auth_client_secret=auth)  # Pass authentication to the client



result = client.query.get("JobPosting", ["title", "company", "location"]).with_limit(5).do()
pprint(result) 
