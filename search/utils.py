import tiktoken as tk
from urllib.parse import urlparse
import requests
import re

ENCODING_MODEL = "text-davinci-003"

def get_tokens(text: str) -> list and int:
    '''
    Returns a list of tokens and the number of tokens in the text.
    text: The text to tokenize.
    '''
    encoder = tk.encoding_for_model(ENCODING_MODEL)
    tokens = encoder.encode(text)
    return tokens, len(tokens)

#Get the YouTube ID from a YouTube URL.
#TODO: Add support for shortened YouTube URLs and check if the URL is valid.
def get_youtube_id(url):
    """
    Extracts the YouTube video ID from a URL.
    url: The URL of the YouTube video.
    """
    #Check URL validity first.
    parsed_url = urlparse(url)
    if all([parsed_url.scheme, parsed_url.netloc]):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return None
        except:
            return None
    else:
        return None
    
    # Define a regular expression pattern to match the video ID
    pattern = r"(?<=v=)[\w-]+|(?<=be/)[\w-]+"
    
    # Use the regular expression to search for a match in the input URL
    match = re.search(pattern, url)
    
    # If a match is found, return the video ID as a string
    if match:
        return match.group()
    
    # If no match is found, return None
    else:
        return None

def create_description(snippet):
    '''
    Youtube returns a description snippet which is a list of text with formatting. This function
    creates an unformatted description from the snippet.
    snippet: The descriptionSnippet from the video search result.
    '''
    description = ""
    for chunk in snippet:
        description += chunk["text"]
    return description