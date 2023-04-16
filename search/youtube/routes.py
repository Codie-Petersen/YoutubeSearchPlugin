"""API routes for the youtube search module."""
from search.youtube.service import get_transcript
from quart import request
from quart_cors import cors
import quart
import json

BASE_ROUTE = "/search/youtube"
CONFIG_ROUTE = "./search/youtube/config"
app = cors(quart.Quart(__name__))

@app.route(f"{BASE_ROUTE}/transcript", methods=["POST"])
async def get_video_transcript():
    data = await request.get_json()
    youtube_url = data["url"]
    transcript = get_transcript(youtube_url)
    if transcript is None:
        return json.dumps({"error": "Invalid YouTube URL."})
    return json.dumps({"transcript": transcript})

# App icon route.
@app.route(f"{BASE_ROUTE}/logo.png", methods=["GET"])
async def plugin_logo():
    filename = f"{CONFIG_ROUTE}/logo.png"
    return await quart.send_file(filename, mimetype="image/png")

# App manifest route.
@app.route(f"{BASE_ROUTE}/.well-known/ai-plugin.json", methods=["GET"])
async def plugin_manifest():
    host = request.headers["Host"]
    filename = f"{CONFIG_ROUTE}/ai-plugin.json"
    with open(filename) as file:
        text = file.read()
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return quart.Response(text, mimetype="text/json")

# OpenAPI route.
@app.route(f"{BASE_ROUTE}/openapi.yaml", methods=["GET"])
async def openapi_specification():
    host = request.headers["Host"]
    filename = f"{CONFIG_ROUTE}/openapi.yaml"
    with open(filename) as file:
        text = file.read()
        text = text.replace("PLUGIN_HOSTNAME", f"https://{host}")
        return quart.Response(text, mimetype="text/yaml")

# Health check route.
@app.route(f"{BASE_ROUTE}/ping", methods=["GET"])
async def ping():
    return "pong"

def youtube_service():
    """Run the YouTube Service app."""
    app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    youtube_service()
