from search.youtube.routes import youtube_service
from search.youtube.service import search_videos

YOUTUBE_URL = "https://www.youtube.com/watch?v=-Vy12e0LjX4&ab_channel=BabishCulinaryUniverse"

#youtube_service()
videosSearch = None
while True:
    search = input("Search: ")
    videos = search_videos(search)
    for video in videos:
        print(f"### {video['title']}")
        print(f"[![img]({video['thumbnail']})]({video['url']})")
        print(f"**Views:** {video['views']} | **Duration:** {video['length']} | **Released:** {video['published']}")
        print(f"**Description:** {video['description']}")
        