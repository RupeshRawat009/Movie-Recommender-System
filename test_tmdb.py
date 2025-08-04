import requests
import re

TMDB_API_KEY = "1a196a90f88da08f5159770dbffd5a19"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w200"

def get_poster_url(title):
    clean_title = re.sub(r"\s\(\d{4}\)$", "", title)
    params = {"api_key": TMDB_API_KEY, "query": clean_title}
    
    try:
        print(f"Searching poster for: {clean_title}")
        response = requests.get(f"{TMDB_BASE_URL}/search/movie", params=params, timeout=5)
        response.raise_for_status()  # Raises exception for HTTP errors

        data = response.json()
        results = data.get("results", [])
        if results and results[0].get("poster_path"):
            poster_url = f"{TMDB_IMAGE_BASE_URL}{results[0]['poster_path']}"
            print("✅ Poster URL found:", poster_url)
        else:
            print("❌ No poster found in API results.")

    except requests.exceptions.RequestException as e:
        print("❌ Connection or API error:", e)

# Run test
get_poster_url("Inception (2010)")
