"""API routes for the youtube search module."""
from search.youtube.service import get_transcript
from quart import request
from quart_cors import cors
import quart
import json

app = cors(quart.Quart(__name__))

@app.route("/search/youtube/transcript", methods=["POST"])
async def search_youtube():
    """Search youtube for the given query."""
    data = await request.get_json()
    youtube_url = data["url"]
    transcript = get_transcript(youtube_url)
    if transcript is None:
        return json.dumps({"error": "Invalid YouTube URL."})
    return json.dumps({"transcript": transcript})

def youtube_service():
    """Run the YouTube Service app."""
    app.run(debug=True, host="0.0.0.0", port=5000)

if __name__ == "__main__":
    youtube_service()
