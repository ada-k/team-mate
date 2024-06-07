import os
import asyncio
from .weaviate_interface import WeaviateInterface
from weaviate.auth import AuthApiKey
from dotenv import load_dotenv

load_dotenv()

async def setup_weaviate_interface_async() -> WeaviateInterface:
    openai_key = os.getenv("OPENAI_API_KEY")
    weaviate_url = os.getenv("WEAVIATE_URL")
    schema_file = "./weaviate_/schema.json"
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

    if not openai_key or not weaviate_url:
        raise ValueError("Missing OPENAI_API_KEY or WEAVIATE_URL or WEAVIATE_API_KEY")

    auth = AuthApiKey(api_key=weaviate_api_key)
    weaviate_interface = WeaviateInterface(weaviate_url, openai_key, schema_file, auth)
    await weaviate_interface.async_init()

    return weaviate_interface

# def setup_weaviate_interface():
#     return setup_weaviate_interface_async()


def setup_weaviate_interface():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    # loop = asyncio.get_event_loop()
    # loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop) 

    print(loop.is_running())
    if loop.is_running():
        task = asyncio.create_task(setup_weaviate_interface_async())
        print(task)
    #     return task
    # else:
        # return loop.run_until_complete(setup_weaviate_interface_async())
    # loop.close()

    # try:
    #     weaviate_interface = loop.run_until_complete(setup_weaviate_interface_async())
    #     return weaviate_interface
    # finally:
    #     loop.close()  # Close the event loop to prevent resource leaks

