import uvicorn
import socketio
from fastapi import FastAPI
from typing import Dict, List
from weaviate_ import setup_weaviate_interface, WeaviateInterface
import openai
import os

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# FastAPI and Socket.IO setup
app = FastAPI()
sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socket_app = socketio.ASGIApp(sio)
app.mount("/", socket_app)

# Session data storage
sessions: Dict[str, List[Dict[str, str]]] = {}

# Weaviate interface setup
weaviate_interface = setup_weaviate_interface()
# weaviate_interface = setup_weaviate_interface_async()



# weaviate_interface: WeaviateInterface = None

# async def start_weaviate():
#     global weaviate_interface
#     weaviate_interface = await setup_weaviate_interface()

# @app.on_event("startup")
# async def startup_event():
#     await start_weaviate()



# Function to generate response from OpenAI (updated for chat completion)
def generate_response(user_message: str, context: str = None) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": context}  # Include context from Weaviate
        ]
    )
    return response.choices[0].message["content"]



# Print {"Hello":"World"} on localhost:7777
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Logs when a client connects.
@sio.on("connect")
async def connect(sid, env):
    print("New Client Connected to This id :" + " " + str(sid))

# Logs when a client disconnects.
@sio.on("disconnect")
async def disconnect(sid):
    print("Client Disconnected: " + " " + str(sid))


# Acknowledges a client's connection.
@sio.on("connectionInit")
async def handle_connection_init(sid):
    await sio.emit("connectionAck", room=sid)


# Initializes a session and potentially loads chat history.
@sio.on("sessionInit")
async def handle_session_init(sid, data):
    print(f"===> Session {sid} initialized")
    session_id = data.get("sessionId")
    if session_id not in sessions:
        sessions[session_id] = []
    print(f"**** Session {session_id} initialized for {sid} session data: {sessions[session_id]}")
    await sio.emit("sessionInit", {"sessionId": session_id, "chatHistory": sessions[session_id]}, room=sid)



@sio.on("textMessage")
async def handle_chat_message(sid, data):
    print(f"Message from {sid}: {data}")
    session_id = data.get("sessionId")
    try:
        if session_id not in sessions:
            raise Exception(f"Session {session_id} not found")

        received_message = {
            "id": data.get("id"),
            "message": data.get("message"),
            "isUserMessage": True,
            "timestamp": data.get("timestamp"),
        }
        sessions[session_id].append(received_message)

        # results = weaviate_interface.search(data.get("message"))
        # print("RESULTS:")
        # print(results)


        # Perform semantic search across all classes (automatic)
        print("-----------------------")
        print("-----------------------")
        print(data.get("message"))
        weaviate_interface_instance = await weaviate_interface 
        print(weaviate_interface_instance)
        print(type(weaviate_interface_instance))
        print("-----------------------")
        print("-----------------------")
        # Await the search result since it is a coroutine
        results = weaviate_interface_instance.search(data.get("message"))
        # results = weaviate_interface.search(data.get("message"))

        print(results)

        # Extract and format context from Weaviate results
        context = "\n".join(
            [
                f"- {result['_additional']['id']}: {result.get('title', '') or result.get('content', '')}"
                for result in results.values()  # Iterate over the values of the results dictionary
            ]
        )

        # Generate a response using OpenAI
        openai_response = generate_response(
            user_message=data.get("message"), context=context
        )

        response_message = {
            "id": data.get("id") + "_response",
            "textResponse": openai_response,
            "isUserMessage": False,
            "timestamp": data.get("timestamp"),
            "isComplete": True,
        }
        await sio.emit("textResponse", response_message, room=sid)
        sessions[session_id].append(response_message)
    except Exception as e:
        error_message = {
            "id": data.get("id") + "_error",
            "textResponse": f"Error processing message: {str(e)}",
            "isUserMessage": False,
            "timestamp": data.get("timestamp"),
            "isComplete": True,
        }
        await sio.emit("textResponse", error_message, room=sid)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=6789, lifespan="on", reload=True)
