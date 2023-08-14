# YouTube Search and Summarize

This is a project of mine that I am now using to showcase the usage of [Promptate](https://www.promptate.com) for generating ads in a YouTube search and summarize OpenAI Plugin. It provides an API to search for YouTube videos and retrieve their transcripts. It fetches ads from [Promptate](https://www.promptate.com) for the user.

## Overview

The YouTube search and summarize plugin is built using Python and Quart framework for asynchronous web serving. The service allows users to perform the following actions:

1. **Search for YouTube Videos**: Users can perform a search query to find videos on YouTube.

2. **Get Video Transcripts**: Users can obtain the raw transcript of a specific YouTube video by providing its URL.

3. **Get Next Page of Search Results**: Users can retrieve the next page of search results for a particular search query.

4. **Fetch Ads from [Promptate](https://www.promptate.com)**: The service integrates with [Promptate](https://www.promptate.com) to fetch relevant ads for the users.

## Getting Started

To run the service on your local machine, follow these steps:

1. **Install Dependencies**: First, install the required Python packages using the following command:

   ```
   pip install -r requirements.txt
   ```

2. **Start the Service**: Run the Python script `app.py` to start the service:

   ```
   python app.py
   ```

   The service will be available at `http://localhost:5000`.

## API Endpoints

The service provides several API endpoints that can be accessed to interact with the YouTube search and summarize functionality. Below are the available endpoints:

### Get Video Transcript

- Endpoint: `POST /search/youtube/transcript`
- Input: JSON body with `url` field containing the YouTube video URL.
- Output: JSON response containing the `transcript` of the video.

### Search YouTube Videos

- Endpoint: `POST /search/youtube/query`
- Input: JSON body with `query`, `username`, `iso_3166-1_alpha-2_code`, and `iso_639-1_code` fields.
- Output: JSON response containing `videos` list and a `query_id` to get the next page of results.

### Get Next Page of Results

- Endpoint: `POST /search/youtube/next`
- Input: JSON body with `query_id` obtained from the `/search/youtube/query` endpoint.
- Output: JSON response containing the `videos` for the next page of results.

### Miscellaneous Endpoints

- `/search/youtube/logo.png`: Get the app logo.
- `/.well-known/ai-plugin.json`: OpenAI plugin manifest.
- `/search/youtube/openapi.yaml`: OpenAPI specification.
- `/search/youtube/ping`: A simple health check.

## Ad Integration with [Promptate](https://www.promptate.com)

The service includes a function `get_promptate_ad(user_id)` that fetches ads from [Promptate](https://www.promptate.com) based on the provided `user_id`. Currently, it uses hardcoded values for `plugin_name` and `developer_token`, but in a real-world scenario, you should register with [Promptate](https://www.promptate.com) to obtain your own tokens and handle them securely.

## Customization

You can customize the service according to your requirements. For instance, you may want to implement user authentication, handle more search parameters, or store user preferences in a database. The service is provided as a basic template, and you can extend it as per your needs.

Please note that this project serves as a demonstration of [Promptate](https://www.promptate.com) usage and does not represent a full-fledged production-ready service. It is intended to provide developers with a starting point for building their own plugins and services using [Promptate](https://www.promptate.com) and YouTube APIs.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to modify and use it as per your needs.

## Acknowledgments

This project uses the following third-party libraries:

- `youtube-transcript-api`: A Python library to fetch YouTube video transcripts.
- `youtube-search-python`: A Python library to perform YouTube video searches.
- `requests`: A Python library to make HTTP requests.
- `Quart`: A Python asynchronous web framework.
- `Quart-CORS`: A Quart extension for handling CORS.
- `tiktoken`: A Python library to count the number of tokens in a text string.

Please make sure to give proper credit to the authors and contributors of these libraries and include any additional licensing information if required.

## Note

The integration with [Promptate](https://www.promptate.com) is for demonstration purposes and uses hardcoded values. In a real-world application, you should follow the recommended practices for securing tokens and integrating with external services.
