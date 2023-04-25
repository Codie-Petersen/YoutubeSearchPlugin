from search.youtube.routes import youtube_service
from search.youtube.service import search_videos

youtube_service()
videoSearch = None
# while True:
#     search = input("Search: ")
#     if search == "/next" and videoSearch != None:
#         videos, videoSearch = search_videos(search, video=videoSearch)
#     elif search == "/exit":
#         break
#     else:
#         videos, videoSearch = search_videos(search)

#     for video in videos:
#         print(video)
#         # print(f"### {video['title']}")
#         # print(f"[![img]({video['thumbnail']})]({video['url']})")
#         # print(f"**Views:** {video['views']} | **Duration:** {video['length']} | **Released:** {video['published']}")
#         # print(f"**Description:** {video['description']}")