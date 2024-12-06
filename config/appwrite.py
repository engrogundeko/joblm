from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID

# Initialize Appwrite Client
client = Client()
client.set_endpoint('YOUR_ENDPOINT')  # Set your Appwrite endpoint
client.set_project('YOUR_PROJECT_ID')  # Set your project ID
client.set_key('YOUR_API_KEY')  # Set your API key

# Initialize Database service
databases = Databases(client)

# Database and Collection IDs
DATABASE_ID = 'YOUR_DATABASE_ID'
SCHOLARSHIP_COLLECTION_ID = 'YOUR_COLLECTION_ID'
