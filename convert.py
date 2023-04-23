import json

def load_json(filepath):
    with open(filepath) as f:
        data = json.load(f)
    return data

def pull_languages(data):
    languages = {}
    for item in data["items"]:
        name = item["snippet"]["name"]
        code = item["id"]
        languages[name] = code
    return languages

def pull_regions(data):
    regions = {}
    for item in data["items"]:
        name = item["snippet"]["name"]
        code = item["id"]
        regions[name] = code
    return regions

def save_json(data, filepath):
    with open(filepath, "w") as f:
        json.dump(data, f, indent = 4)

def main():
    languages_path = "D:/Git/AsteresAI/YoutubeSearchPlugin/search/youtube/resources/languages.json"
    regions_path = "D:/Git/AsteresAI/YoutubeSearchPlugin/search/youtube/resources/regions.json"
    languages = load_json(languages_path)
    regions = load_json(regions_path)
    languages = pull_languages(languages)
    regions = pull_regions(regions)
    save_json(languages, languages_path)
    save_json(regions, regions_path)

if __name__ == "__main__":
    main()
