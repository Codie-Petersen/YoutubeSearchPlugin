"""API routes for the youtube search module."""
from search.youtube.service import get_transcript
from quart import request
from quart_cors import cors
import quart
import json

app = cors(quart.Quart(__name__))

@app.route("/search/youtube/<string:youtube_url>", methods=["GET"])
async def search_youtube(youtube_url):
    """Search youtube for the given query."""
    transcript = get_transcript(youtube_url)
    return json.dumps({"transcript": transcript})

def youtube_service():
    """Run the YouTube Service app."""
    app.run(debug=True, host="0.0.0.0", port=5000)

if __name__ == "__main__":
    youtube_service()
