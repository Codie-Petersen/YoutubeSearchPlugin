"""API routes for the youtube search module."""
from search.youtube.service import get_transcript, search_videos
from quart import request
from quart_cors import cors
import asyncio
import signal
import quart
import json
import uuid

BASE_ROUTE = "/search/youtube"
CONFIG_ROUTE = "./search/youtube/config"

# A dictionary of VideoSearch objects from youtubesearchpython.
# Object is created when a search is started.
# Used to get the next page of results.
active_queries = {}

app = cors(quart.Quart(__name__))

#TODO: Add a way to get the next page of results.

@app.route(f"{BASE_ROUTE}/transcript", methods=["POST"])
async def get_video_transcript():
    """ 
    Get the raw transcript of a YouTube video.
    url: The URL of the YouTube video.
    """
    data = await quart.request.get_json()
    youtube_url = data["url"]
    try:
        transcript = await asyncio.wait_for(
            get_transcript(youtube_url), timeout=60)
    except asyncio.TimeoutError:
        return json.dumps({"error": "Timeout while getting transcript."})
    if transcript is None:
        return json.dumps({"error": "Invalid YouTube URL."})
    
    return json.dumps({"transcript": transcript})

@app.route(f"{BASE_ROUTE}/query", methods=["POST"])
#TODO: Add region and language parameters.
async def query():
    """
    Searches YouTube for videos and returns a list of dictionaries containing
    information about each video as well as a query_id that can be used to get
    the next page of results.
    query: The search query.
    query_id: A UID of the query session.
    """
    data = await quart.request.get_json()
    search = data["query"]
    try:
        query_id = str(uuid.uuid4())
        videos, videoSearch = await asyncio.wait_for(search_videos(search), timeout=60)
        active_queries[query_id] = videoSearch
        return json.dumps({"videos": videos, "query_id": query_id})
    except asyncio.TimeoutError:
        return json.dumps({"error": "Timeout while searching videos."})

@app.route(f"{BASE_ROUTE}/logo.png", methods=["GET"])
async def plugin_logo():
    """Return the app logo."""
    filename = f"{CONFIG_ROUTE}/logo.png"
    return await quart.send_file(filename, mimetype="image/png")

@app.route(f"/.well-known/ai-plugin.json", methods=["GET"])
async def plugin_manifest():
    """Return the app manifest."""
    host = request.headers["Host"]
    filename = f"{CONFIG_ROUTE}/ai-plugin.json"
    with open(filename) as file:
        text = file.read()
        text = text.replace("PLUGIN_HOSTNAME", f"http://{host}")
        return quart.Response(text, mimetype="application/json")

@app.route(f"{BASE_ROUTE}/openapi.yaml", methods=["GET"])
async def openapi_specification():
    """Return the OpenAPI specification."""
    host = request.headers["Host"]
    filename = f"{CONFIG_ROUTE}/openapi.yaml"
    with open(filename) as file:
        text = file.read()
        text = text.replace("PLUGIN_HOSTNAME", f"http://{host}")
        return quart.Response(text, mimetype="text/yaml")

@app.route(f"{BASE_ROUTE}/ping", methods=["GET"])
async def ping():
    """Return a simple health check."""
    return "pong"

# -------------------------- #
# App shutdown and startup.  #
# -------------------------- #

def handle_sigint(sig, frame):
    """Help shutdown the app."""
    print("Received SIGINT, shutting down...")
    asyncio.create_task(app.shutdown())

def add_signal_handlers(loop):
    """Add signal handlers to the event loop."""
    for signal_name in {"SIGINT", "SIGTERM", "SIGBREAK"}:
        if hasattr(signal, signal_name):
            try:
                loop.add_signal_handler(getattr(signal, signal_name), handle_sigint)
            except NotImplementedError:
                signal.signal(getattr(signal, signal_name), handle_sigint)

def youtube_service(host="0.0.0.0", port=5000):
    """
    A YouTube search and transcript service.
    host: The host to run the service on.
    port: The port to run the service on.
    
    Routes:
    /search/youtube/transcript
        Get the raw transcript of a YouTube video.

    /search/youtube/search
        Searches YouTube for videos and returns a list of dictionaries containing
        video information.

    /search/youtube/logo.png
        Retreive the app logo.

    /.well-known/ai-plugin.json
        OpenAI plugin manifest.

    /search/youtube/openapi.yaml
        OpenAPI specification.

    /search/youtube/ping
        A simple health check.

    """
    loop = asyncio.get_event_loop()
    add_signal_handlers(loop)
    app.run(debug=True, host=host, port=port)