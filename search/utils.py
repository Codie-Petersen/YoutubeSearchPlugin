import tiktoken as tk

ENCODING_MODEL = "text-davinci-003"

def get_tokens(text: str) -> list and int:
    encoder = tk.encoding_for_model(ENCODING_MODEL)
    tokens = encoder.encode(text)
    return tokens, len(tokens)

def get_youtube_id(url: str) -> str:
    return url.split("v=")[1].split("&")[0]