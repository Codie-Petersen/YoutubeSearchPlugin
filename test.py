#Test youtube transcript API
import youtube_transcript_api as yta
from search.utils import get_tokens

#Get transcript
transcript = yta.YouTubeTranscriptApi.get_transcript("ZkgFaC-Jug4")

#Scrape text
text = ""
for t in transcript:
    text += t['text'] + " "

#Get token count
tokens, count = get_tokens(text)
print(count)