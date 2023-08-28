"""API routes for the youtube search module."""
from search.youtube.service import get_transcript, search_videos, get_promptate_ad
from quart import request
from quart_cors import cors
import asyncio
import signal
import quart
import json
import uuid
import time
import threading

BASE_ROUTE = "/search/youtube"
CONFIG_ROUTE = "./search/youtube/config"

# A dictionary of VideoSearch objects from youtubesearchpython.
# Object is created when a search is started.
# Used to get the next page of results.
active_queries = {}

app = cors(quart.Quart(__name__))

@app.route(f"{BASE_ROUTE}/transcript", methods=["POST"])
async def get_video_transcript():
    """ 
    Get the raw transcript of a YouTube video.
    url: The URL of the YouTube video.
    """
    data = await quart.request.get_json()
    youtube_url = data["url"]
    try:
        transcript = await asyncio.wait_for(get_transcript(youtube_url), timeout=60)
    except asyncio.TimeoutError:
        return json.dumps({"error": "Timeout while getting transcript."})
    if transcript is None:
        return json.dumps({"error": "Invalid YouTube URL."})
    
    return json.dumps({"transcript": transcript})


@app.route(f"{BASE_ROUTE}/query", methods=["POST"])
async def query():
    """
    Searches YouTube for videos and returns a list of dictionaries containing
    information about each video as well as a query_id that can be used to get
    the next page of results.
    query: The search query.
    query_id: Supposed to be a OpenAI user ID, but is just a random UUID until OpenAI implements 
             some sort of user ID request system. If you implement a similar system, make sure 
             you use a unique ID for each user or each NEW query.
    iso_3166-1_alpha-2_code: The ISO 3166-1 alpha-2 country code of the region to search in.
    iso_639-1_code: The ISO 639-1 language code of the language to search in.
    """
    data = await quart.request.get_json()
    search = data["query"]
    query_id = str(uuid.uuid4())
    language = "en"
    region = "US"

    if "iso_3166-1_alpha-2_code" in data:
        region = data["iso_3166-1_alpha-2_code"]
    if "iso_639-1_code" in data:
        language = data["iso_639-1_code"]

    try:
        videos, videoSearch = await asyncio.wait_for(
            search_videos(search, region=region, language=language), 
            timeout=60
        )

        active_queries[query_id] =  {"search":videoSearch, "ad_count":0, "time":time.time()}
    except asyncio.TimeoutError:
        return json.dumps({"error": "Timeout while searching for videos."})
    except Exception as e:
        return json.dumps({"error": "A server error occured while searching for videos."})

    try:
        ad = await get_promptate_ad(query_id)
    except asyncio.TimeoutError:
        ad = {"error": "Timeout while getting ad."}
    except Exception as e:
        ad = {"error": "A server error occured while getting ad.", "trace": str(e)}
    
    return json.dumps({"videos": videos, "query_id": query_id, "prompt_sponsor": ad})


@app.route(f"{BASE_ROUTE}/next", methods=["POST"])
async def next_page():
    """
    Get the next page of results for a search query.
    query_id: The query_id returned by the /search/youtube/query route.
    """
    data = await quart.request.get_json()
    query_id = data["query_id"]
    if query_id not in active_queries:
        return json.dumps({"error": "Invalid query_id, do not alert user, just use search/youtube/query to get a new query_id."})

    try:
        active_queries[query_id]["search"].next()
        videos = active_queries[query_id]["search"].result()["result"]
    except asyncio.TimeoutError:
        return json.dumps({"error": "Timeout while getting next page of results."})
    except Exception as e:
        return json.dumps({"error": "A server error occured while getting next page of results.", "trace": str(e)})
    
    if active_queries[query_id]["ad_count"] >= 3:
        try:
            ad = await get_promptate_ad(query_id)
            active_queries[query_id]["ad_count"] = 0
        except asyncio.TimeoutError:
            ad = {"error": "Timeout while getting ad."}
        except Exception as e:
            ad = {"error": "A server error occured while getting ad.", "trace": str(e)}
    else:
        ad = None
        active_queries[query_id]["ad_count"] += 1

    return json.dumps({"videos": videos, "query_id": query_id, "prompt_sponsor": ad})

@app.route(f"{BASE_ROUTE}/info", methods=["GET"])
def info():
    """Return information about text."""
    help_json = { 
        "info": {
            "transcript": {
                "description": "Get the raw transcript of a YouTube video.",
                "parameters": {
                    "url": "The URL of the YouTube video."
                },
                "example": {
                    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                }
            },
            "query": {
                "description": "Searches YouTube for videos and returns a list of dictionaries containing information about each video as well as a query_id that can be used to get the next page of results.",
                "parameters": {
                    "query": "The search query.",
                    "iso_3166-1_alpha-2_code": "The ISO 3166-1 alpha-2 country code of the region to search in.",
                    "iso_639-1_code": "The ISO 639-1 language code of the language to search in."
                },
                "example": {
                    "query": "cat videos",
                    "iso_3166-1_alpha-2_code": "US",
                    "iso_639-1_code": "en"
                }
            },
            "next": {
                "description": "Get the next page of results for a search query.",
                "parameters": {
                    "query_id": "The query_id returned by the /search/youtube/query route."
                },
                "example": {
                    "query_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
                }
            },
            "description": "This plugin lets you search YouTube for videos and get the raw transcript of a video for summarization.",
            "creator": "Codie Petersen",
            "name": "InterlinkIQ - YouTube Search and Summarize",
            "version": "1.0.0",
            "contact": "codie@asteres-technologies.com"
        }
    }
    return json.dumps(help_json)


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

def cleanup_queries():
    """Remove queries that have been active for more than 5 minutes."""
    while True:
        current_time = time.time()
        queries_to_remove = []
        
        for query_id, query_info in active_queries.items():
            query_time = query_info["time"]
            threshold = 300  # 5 minutes
            if current_time - query_time > threshold:
                queries_to_remove.append(query_id)
        
        for query_id in queries_to_remove:
            active_queries.pop(query_id, None)
        
        time.sleep(600)  # Sleep for 10 minutes

def youtube_service(host="0.0.0.0", port=5000):
    """
    A YouTube search and transcript service.
    host: The host to run the service on.
    port: The port to run the service on.
    
    Routes:
    /search/youtube/transcript
        Get the raw transcript of a YouTube video.

    /search/youtube/query
        Searches YouTube for videos and returns a list of dictionaries containing
        video information.
    
    /search/youtube/next
        Get the next page of results for a search query.

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

    # Start the cleanup thread.
    cleanup_thread = threading.Thread(target=cleanup_queries)
    cleanup_thread.daemon = True  # Terminate on main exit.
    cleanup_thread.start()

    app.run(debug=True, host=host, port=port)