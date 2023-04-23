#TODO: Replace youtube_transcript_api with youtubeseachpython.
import youtube_transcript_api as yta
from youtubesearchpython import VideosSearch
from search.utils import get_tokens, get_youtube_id

async def get_transcript(youtube_url, chunk_size_seconds=40, with_times=True):
    #Get transcript
    id = get_youtube_id(youtube_url)
    transcript = yta.YouTubeTranscriptApi.get_transcript(id)

    chunk = ""
    chunks = []
    times = []
    chunk_times = []

    #Loop through transcript and capture times and chunks.
    for line in transcript:
        text = line["text"]
        if chunk == "":
            chunk += text
            times = [line["start"], line["start"] + line["duration"]]
        else:
            chunk += " " + text
            times.append(line["start"] + line["duration"])
            if len(chunk.split(" ")) > chunk_size_seconds or text.endswith(".") or text.endswith("?") or text.endswith("!") or text.endswith("\""):
                times.sort()
                chunks.append(chunk)
                chunk_times.append([round(times[0]), round(times[-1])])
                chunk = ""
                times = []

    if chunk != "":
        times.sort()
        chunks.append(chunk)
        chunk_times.append([round(times[0]), round(times[-1])])
        chunk = ""
        times = []
    
    full_transcript = ""
    if not with_times:
        full_transcript = " ".join(chunks)
        return full_transcript
    
    for i in range(len(chunks)):
        full_transcript += f"{chunk_times[i][0]}-{chunk_times[i][1]}: {chunks[i]}\n"

    return full_transcript

#TODO: Add a way to get the next page of results.
def search_videos(search, limit=10):
    videosSearch = VideosSearch(search, limit = limit)
    return videosSearch.result()["result"]