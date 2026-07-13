import os
import requests
import json

USERNAME = "nishant020208"
repos = json.load(open('scratch/repos.json'))

os.makedirs("scratch/readmes", exist_ok=True)

for r in repos:
    name = r['name']
    default_branch = r.get('default_branch', 'main')
    print(f"Fetching README for {name}...")
    
    # Try README.md on default branch
    url = f"https://raw.githubusercontent.com/{USERNAME}/{name}/{default_branch}/README.md"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            with open(f"scratch/readmes/{name}.md", "w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"  Saved {name}.md")
            continue
    except Exception as e:
        print(f"  Error fetching raw README for {name}: {e}")
        
    # If raw files fails, try GitHub API readme endpoint
    api_url = f"https://api.github.com/repos/{USERNAME}/{name}/readme"
    try:
        resp = requests.get(api_url)
        if resp.status_code == 200:
            import base64
            content = resp.json().get('content', '')
            decoded = base64.b64decode(content).decode('utf-8', errors='ignore')
            with open(f"scratch/readmes/{name}.md", "w", encoding="utf-8") as f:
                f.write(decoded)
            print(f"  Saved {name}.md via API")
        else:
            print(f"  No README found for {name} (status {resp.status_code})")
    except Exception as e:
         print(f"  Error fetching API README for {name}: {e}")
