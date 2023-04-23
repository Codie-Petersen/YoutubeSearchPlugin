from search.youtube.routes import youtube_service
from youtubesearchpython import VideosSearch

YOUTUBE_URL = "https://www.youtube.com/watch?v=-Vy12e0LjX4&ab_channel=BabishCulinaryUniverse"

#youtube_service()
videosSearch = None
while True:
    search = input("Search: ")
    if search == "/next" and videosSearch is not None:
        videosSearch.next()
    else:
        videosSearch = VideosSearch(search, limit = 10)
    for result in videosSearch.result()["result"]:
        print(f"### {result['title']}")
        print(f"[![img]({result['thumbnails'][0]['url']})]({result['link']})")
        