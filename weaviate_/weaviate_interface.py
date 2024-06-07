from weaviate_.schema_manager import SchemaManager
from weaviate_.weaviate_client import WeaviateClient
from .http_client import HttpClient, HttpHandler
from weaviate.auth import AuthApiKey


class WeaviateInterface:
    def __init__(self, url: str, openai_key: str, schema_file: str, auth_client_secret):
        self.http_handler = HttpHandler(HttpClient(url, {"X-OpenAI-Api-Key": openai_key}, auth_client_secret=auth_client_secret))
        self.client = WeaviateClient(self.http_handler)
        self.schema = SchemaManager(self.client, schema_file)

    async def async_init(self):
        """
        Asynchronous initialization tasks for WeaviateInterface.
        """
        if not await self.schema.is_valid():
            await self.schema.reset()

    