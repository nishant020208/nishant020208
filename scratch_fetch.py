import requests
import json
import os

USERNAME = "nishant020208"
url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"

try:
    response = requests.get(url)
    response.raise_for_status()
    repos = response.json()
    
    # Ensure folder structure exists
    os.makedirs("scratch", exist_ok=True)
    with open("scratch/repos.json", "w") as f:
        json.dump(repos, f, indent=2)
    print(f"Successfully fetched and saved {len(repos)} repositories.")
except Exception as e:
    print(f"Error fetching repos: {e}")
