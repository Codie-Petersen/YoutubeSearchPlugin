from typing import List, Dict, Tuple
from urllib.parse import urlparse
from rake_nltk import Rake
import requests
import re

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
    match = re.search(pattern, url)
    
    # If a match is found, return the video ID as a string
    if match:
        return match.group()
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

def levenshtein_distance(s1, s2) -> List[List[int]]:
    """
    Return the Levenshtein distance between two strings.
    Levenshtein distance is the number of edits needed to transform 
    one string into the other.
    """
    # Create a matrix to store the distances
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize the matrix with base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # Fill in the matrix using dynamic programming
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,       # Deletion
                dp[i][j - 1] + 1,       # Insertion
                dp[i - 1][j - 1] + cost  # Substitution
            )

    return dp[m][n]

def clean_extracted(extracted) -> List[Tuple[int, str]]:
    """Remove special characters from extracted keywords."""
    cleaned = []
    for i in range(len(extracted)):
        text = re.sub(r"[^a-zA-Z0-9]+", ' ', extracted[i][1])
        text = text.strip()
        cleaned.append((extracted[i][0], text))
    return cleaned

def get_all_distances(extracted) -> List[List[int]]:
    """Get the Levenshtein distance between each keyword."""
    #Better results in sibling dictionary if we start with shorter keywords.
    extracted.reverse() 
    distances = []
    for i in range(len(extracted)):
        _distances = []
        for j in range(len(extracted)):
            if i != j:
                #Don't use string to string distance. Use word to word distance.
                #Ie. "hello world" and "hello world" should have a distance of 0.
                #But "hello world" and "hello" or "hello bob" should have a distance of 1.
                _distances.append(
                    levenshtein_distance(
                        extracted[i][1].split(" "), 
                        extracted[j][1].split(" "))
                    )
            else:
                _distances.append(0)
        distances.append(_distances)
    return distances

def get_siblings_dictionary(extracted, distances, leven_threshold=0.5) -> Dict[str, List[str]]:
    """Build a dictionary of keywords and keywords with close Levenshtein distances."""
    sibling_list = {}
    for i in range(len(distances)):
        siblings = []
        keyword = extracted[i][1]

        for j in range(len(distances[i])):
            keysibling = extracted[j][1]
            if i == j:
                continue

            #Check to see if the distance is within the threshold.
            target = len(keysibling.split(" "))
            if distances[i][j]/target <= leven_threshold:
                siblings.append(keysibling)
        sibling_list[keyword] = siblings

    return sibling_list

def build_condensed_keywords(extracted, siblings) -> Dict[str, int]:
    """Build a dictionary of keywords and their scores."""
    #The dictionary should not contain siblings of keywords that have been added.
    keywords = {}
    represented = []
    for i in range(len(extracted)):
        keyword = extracted[i][1]
        if keyword in represented:
            continue

        keywords[keyword] = extracted[i][0]
        keywords[keyword] *= len(siblings[keyword])+1 #Multiply score by sibling count.
        represented.extend(siblings[keyword])
        represented.append(keyword)
    return keywords


def best_keyword_candidates(keywords) -> list:
    """
    Reduce the keyword dictionary down to simple phrases and scores higher than 2.
    Then grabs the top 5 keywords by score.
    """
    keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
    selected = []
    for i in range(len(keywords)):
        if keywords[i][1] >= 2 and len(keywords[i][0].split(" ")) <= 3 and len(keywords[i][0]) > 3:
            selected.append((keywords[i][0], keywords[i][1]))

    return selected[:5]

def get_keywords(text) -> list:
    """Get keywords from a text with the a modified RAKE algorithm."""
    rake = Rake()
    rake.extract_keywords_from_text(text)
    extracted = clean_extracted(rake.get_ranked_phrases_with_scores())
    distances = get_all_distances(extracted)
    siblings = get_siblings_dictionary(extracted, distances)
    keywords = build_condensed_keywords(extracted, siblings)

    #Return only the keywords without their scores
    keywords = best_keyword_candidates(keywords)
    return [keyword[0] for keyword in keywords]