import json
import requests
from bs4 import BeautifulSoup

urls = {
    "CodeClub Pro": "https://codeclub1-pro.vercel.app",
    "TrustGov": "https://trustgov.vercel.app",
    "SVIT Attend Hub": "https://svit-attend-hub.vercel.app",
    "JobGuard": "https://job-offer-guardian.vercel.app",
    "Forest Pro": "https://forest-pro.vercel.app",
    "IntelliFlow": "https://intelliflow-dbt.vercel.app",
    "AI Guardian": "https://ai-guardian-ruddy.vercel.app",
    "Pulse": "https://pulse-check-opal.vercel.app",
    "Jarvis AI": "https://jarvis-ai-hazel.vercel.app",
    "Mission Control / OnboardFlow": "https://mission-control-onboarding.vercel.app",
    "Excel Study AI": "https://excel-study-ai.vercel.app",
    "GramSetu": "https://gramsetu-sch.vercel.app",
    "SkillVfy": "https://skillvfy.vercel.app",
    "Jarvis v2": "https://jarvis-pink-seven.vercel.app",
    "DeepMerge": "https://deepmerge.vercel.app",
    "Verdant": "https://verdant-alpha.vercel.app",
    "Todo List": "https://todo-list-rho-topaz.vercel.app"
}

results = {}

for name, url in urls.items():
    print(f"Fetching {name} ({url})...")
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else "No Title"
            
            desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
            desc = desc_tag.get("content", "No Description").strip() if desc_tag else "No Description"
            
            results[name] = {
                "title": title,
                "desc": desc,
                "status": 200
            }
        else:
            results[name] = {
                "status": r.status_code,
                "desc": f"Status {r.status_code}"
            }
    except Exception as e:
        results[name] = {
            "status": "error",
            "desc": str(e)
        }

with open("scratch/metadata.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("Finished!")
