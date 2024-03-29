import youtube_transcript_api as yta
from youtubesearchpython import VideosSearch, Video, ResultMode
from search.utils import get_youtube_id, create_description
import requests

search_instructions = "For each URL, using markdown, add a clickable image link to the video's thumbnail and the title of the video."

async def get_transcript(youtube_url, chunk_size_seconds=40, with_times=True):
    '''
    Returns the transcript of a YouTube video. 
    youtube_url: The URL of the YouTube video.
    chunk_size_seconds: The maximum number of seconds a chunk can be.
    with_times: Whether or not to include the times of each chunk.
    '''
    #Get transcript
    id = get_youtube_id(youtube_url)

    try:
        transcript = yta.YouTubeTranscriptApi.get_transcript(id)
    except yta.TranscriptsDisabled:
        return "Transcripts are disabled for this video."

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
            if len(chunk.split(" ")) > chunk_size_seconds or text.endswith(".") or \
                    text.endswith("?") or text.endswith("!") or text.endswith("\""):
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

async def search_videos(search, limit=5, region="US", language="en", video=None):
    '''
    Searches YouTube for videos and returns a list of dictionaries containing
    the title, description, views, length, thumbnail, and url of each video.
    search: The search query.
    limit: The maximum number of videos to return. (Keep around 5 because urls chew up tokens.)
    region: The ISO 3166-1 alpha-2 country code of the region to search in.
    language: The ISO 639-1 language code of the language to search in.
    '''
    if video == None:
        video = VideosSearch(search, limit=limit, region=region, language=language)
    else:
        video.next()

    video_list = [search_instructions]
    for result in video.result()["result"]:
        try:
            description = Video.get(result["id"], mode=ResultMode.json)["description"]
        except:
            description = create_description(result["descriptionSnippet"])

        video_list.append({
            "title": result["title"],
            "description": description,
            "views": result["viewCount"]["short"],
            "length": result["duration"],
            "published": result["publishedTime"],
            "thumbnail": result["thumbnails"][0]["url"].split("?")[0],
            "url": result["link"]
        })

    return video_list, video

async def get_promptate_ad(user_id):
    """
    Gets an ad from Promptate.
    user_id: The user ID of the user to get the ad for. (Or session ID)

    These are hardcoded, but in the future you should register with Promptate and get your
    own and store them in an env or some other config method of your choice.
    plugin_name: The name of the plugin to get the ad for.
    developer_token: The developer token to use to get the ad.
    """
    plugin_name = "demo"
    developer_token = "promptate:qnkg1zpurm0wjrw6"

    headers = {"Authorization": f"Bearer {developer_token}", "OpenAI-User-ID": user_id}
    ad = requests.get(f"https://ads.promptate.com/getad/{plugin_name}", headers=headers).json()["message"]

    return ad