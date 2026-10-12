#!/usr/bin/env python3
import os
import sys
import re
import math
import requests
import urllib3
from datetime import date, timedelta
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USERNAME = "nishant020208"
GRAPHQL_URL = "https://api.github.com/graphql"

LANG_COLORS = {
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Python": "#3572A5",
    "HTML": "#e34c26", "CSS": "#563d7c", "C": "#555555", "C++": "#f34b7d",
    "Java": "#b07219", "Shell": "#89e051", "Rust": "#dea584", "Go": "#00ADD8",
    "Ruby": "#701516", "PHP": "#4F5D95", "Dart": "#00B4AB", "Kotlin": "#A97BFF",
    "Swift": "#F05138", "Jupyter Notebook": "#DA5B0B", "Vue": "#41b883",
    "SCSS": "#c6538c", "Dockerfile": "#384d54", "Makefile": "#427819",
    "PowerShell": "#012456", "Batchfile": "#C1F12E", "EJS": "#a91e50",
    "Svelte": "#ff3e00", "Lua": "#000080", "R": "#198CE7",
}

def fetch_github_api_stats():
    """Fetch followers, repos, and stars from GitHub REST API."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    if token:
        headers["Authorization"] = f"token {token}"
        
    followers = 0
    public_repos = 0
    stars = 0
    repos_data = []
    
    try:
        # Fetch user profile
        user_url = f"https://api.github.com/users/{USERNAME}"
        r = requests.get(user_url, headers=headers, timeout=20)
        r.raise_for_status()
        user_data = r.json()
        followers = user_data.get("followers", 0)
        public_repos = user_data.get("public_repos", 0)
        
        # Fetch repos to count stars
        repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
        r = requests.get(repos_url, headers=headers, timeout=20)
        r.raise_for_status()
        repos_data = r.json()
        if isinstance(repos_data, list):
            stars = sum(repo.get("stargazers_count", 0) for repo in repos_data)
    except Exception as e:
        print(f"Warning: Failed to fetch GitHub API stats: {e}", file=sys.stderr)
        
    # Safe fallbacks if API is rate-limited or fails
    if followers == 0:
        followers = 16
    if public_repos == 0:
        public_repos = 21
    if stars == 0:
        stars = 16
        
    return followers, public_repos, stars, repos_data   

GRAPHQL_QUERY = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""

def fetch_contributions_graphql(year, token):
    """Fetch contribution days for a specific year using GitHub GraphQL API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    }
    resp = requests.post(
        GRAPHQL_URL,
        headers=headers,
        json={
            "query": GRAPHQL_QUERY,
            "variables": {
                "username": USERNAME,
                "from": f"{year}-01-01T00:00:00Z",
                "to": f"{year}-12-31T23:59:59Z",
            },
        },
        timeout=30,
        verify=False,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data or "data" not in data or not data.get("data") or not data["data"].get("user"):
        raise RuntimeError(f"GraphQL error or empty response: {data.get('errors')}")
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = []
    for week in cal["weeks"]:
        for d in week["contributionDays"]:
            days.append({"date": d["date"], "count": d["contributionCount"]})
    return days

def fetch_contributions_html(year, retries=3):
    """Fetch contribution days for a specific year using HTML scraping with retries."""
    url = f"https://github.com/users/{USERNAME}/contributions?from={year}-01-01&to={year}-12-31"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=headers, verify=False, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            tds = soup.find_all('td', class_='ContributionCalendar-day')
            day_map = {td.get('id'): td.get('data-date') for td in tds if td.get('id') and td.get('data-date')}
            if not day_map:
                buttons = soup.find_all('button', class_='ContributionCalendar-day')
                day_map = {b.get('id'): b.get('data-date') for b in buttons if b.get('id') and b.get('data-date')}
            
            tooltips = soup.find_all('tool-tip')
            days = []
            parsed_dates = set()
            
            for tt in tooltips:
                for_id = tt.get('for')
                if for_id in day_map:
                    date_str = day_map[for_id]
                    if date_str in parsed_dates:
                        continue
                    parsed_dates.add(date_str)
                    
                    text = tt.get_text().strip()
                    if text.startswith('No contributions'):
                        count = 0
                    else:
                        m = re.match(r'^([0-9,]+)\s+contribution', text)
                        if m:
                            count = int(m.group(1).replace(',', ''))
                        else:
                            count = 0
                    days.append({"date": date_str, "count": count})
                    
            # Fallback to fill in any days missing tooltips as 0
            all_days = []
            for d_id, d_str in day_map.items():
                matching = [x for x in days if x["date"] == d_str]
                if matching:
                    all_days.append(matching[0])
                else:
                    all_days.append({"date": d_str, "count": 0})
                    
            all_days.sort(key=lambda x: x["date"])
            res = [x for x in all_days if x["date"].startswith(str(year))]
            if res:
                return res
        except Exception as e:
            print(f"Scraping attempt {attempt}/{retries} for {year} failed: {e}", file=sys.stderr)
            import time
            time.sleep(2 * attempt)
            
    return []

def fetch_contributions_for_year(year):
    """Fetch contribution days for a year, preferring GraphQL when token is present, else scraping."""
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        try:
            days = fetch_contributions_graphql(year, token)
            if days:
                return days
        except Exception as e:
            print(f"GraphQL fetch failed for {year} ({e}), falling back to HTML scraping...", file=sys.stderr)

    return fetch_contributions_html(year)

def calc_daily_streaks(all_days):
    today = date.today()
    day_map = {d["date"]: d["count"] for d in all_days}

    tomorrow_str = (today + timedelta(1)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    yesterday_str = (today - timedelta(1)).strftime("%Y-%m-%d")

    # Determine starting point for current streak (accounts for timezone variations)
    if day_map.get(tomorrow_str, 0) > 0:
        start_check = today + timedelta(1)
    elif day_map.get(today_str, 0) > 0:
        start_check = today
    elif day_map.get(yesterday_str, 0) > 0:
        start_check = today - timedelta(1)
    else:
        start_check = None

    # Current streak
    cur = 0
    cur_s = cur_e = None
    if start_check:
        cur_e = start_check
        d = start_check
        while True:
            if day_map.get(d.strftime("%Y-%m-%d"), 0) > 0:
                cur += 1
                cur_s = d
                d -= timedelta(1)
            else:
                break

    # Longest streak
    lng = 0
    lng_s = lng_e = None
    run = 0
    run_s = None
    for day in sorted(all_days, key=lambda x: x["date"]):
        dt = date.fromisoformat(day["date"])
        if day["count"] > 0:
            run += 1
            if run == 1:
                run_s = dt
            if run > lng:
                lng = run
                lng_s = run_s
                lng_e = dt
        else:
            run = 0

    return cur, cur_s, cur_e, lng, lng_s, lng_e

def build_week_map(all_days):
    """Group days into ISO weeks (Mon–Sun)."""
    week_contributions = {}
    for day in all_days:
        dt = date.fromisoformat(day["date"])
        week_start = dt - timedelta(days=dt.weekday())
        key = week_start.strftime("%Y-%m-%d")
        week_contributions[key] = week_contributions.get(key, 0) + day["count"]
    return sorted(week_contributions.items())

def calc_weekly_streaks(weeks):
    today = date.today()
    this_week_start = today - timedelta(days=today.weekday())
    last_week_start = this_week_start - timedelta(7)

    week_map = {w[0]: w[1] for w in weeks}

    this_week_count = week_map.get(this_week_start.strftime("%Y-%m-%d"), 0)
    last_week_count = week_map.get(last_week_start.strftime("%Y-%m-%d"), 0)

    if this_week_count > 0:
        check_week = this_week_start
    elif last_week_count > 0:
        check_week = last_week_start
    else:
        check_week = None

    cur = 0
    cur_s = cur_e = None
    if check_week:
        cur_e = check_week + timedelta(6)
        w = check_week
        while True:
            key = w.strftime("%Y-%m-%d")
            if week_map.get(key, 0) > 0:
                cur += 1
                cur_s = w
                w -= timedelta(7)
            else:
                break

    lng = 0
    lng_s = lng_e = None
    run = 0
    run_s = None
    for key, count in weeks:
        ws = date.fromisoformat(key)
        if count > 0:
            run += 1
            if run == 1:
                run_s = ws
            if run > lng:
                lng = run
                lng_s = run_s
                lng_e = ws + timedelta(6)
        else:
            run = 0

    return cur, cur_s, cur_e, lng, lng_s, lng_e, this_week_count

def fmt_range(s, e):
    if not s or not e:
        return "No active streak"
    if s == e:
        return s.strftime("%b %d, %Y")
    return f"{s.strftime('%b %d')} – {e.strftime('%b %d, %Y')}"

def fmt_range_weekly(s, e):
    if not s or not e:
        return "No active streak"
    if s == e or (e - s).days <= 6:
        return f"Week of {s.strftime('%b %d, %Y')}"
    return f"{s.strftime('%b %d')} – {e.strftime('%b %d, %Y')}"

def fmt_week(s):
    if not s:
        return ""
    return f"Week of {s.strftime('%b %d, %Y')}"

def generate_legacy_streak_svg(total, cur, cur_s, cur_e, lng, lng_s, lng_e):
    today = date.today()
    cur_sub = fmt_range(cur_s, cur_e) if cur > 0 else "No active streak"
    lng_sub = fmt_range(lng_s, lng_e)
    year_label = f"2020 – {today.year}"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 195" width="900" height="195">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FF6EC7"/>
      <stop offset="100%" stop-color="#c44ea8"/>
    </linearGradient>
    <linearGradient id="g2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#36BCF7"/>
      <stop offset="100%" stop-color="#1a7db5"/>
    </linearGradient>
    <clipPath id="cl"><rect rx="10" ry="10" width="900" height="195"/></clipPath>
  </defs>
  <rect clip-path="url(#cl)" width="900" height="195" fill="#0D1117"/>
  <rect width="900" height="2" fill="url(#g1)" opacity="0.85"/>
  <line x1="300" y1="18" x2="300" y2="177" stroke="#21262d" stroke-width="1"/>
  <line x1="600" y1="18" x2="600" y2="177" stroke="#21262d" stroke-width="1"/>
  <g transform="translate(150,97)">
    <text x="0" y="-30" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="14" fill="#36BCF7">Total Contributions</text>
    <text x="0" y="16" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="40" font-weight="800" fill="url(#g1)">{total}</text>
    <text x="0" y="42" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="11" fill="#8b949e">{year_label}</text>
  </g>
  <g transform="translate(450,97)">
    <circle cx="0" cy="-22" r="52" fill="none" stroke="#FF6EC712" stroke-width="10"/>
    <circle cx="0" cy="-22" r="52" fill="none" stroke="url(#g1)" stroke-width="2.5" opacity="0.9"/>
    <text x="0" y="-12" text-anchor="middle" font-size="28">🔥</text>
    <text x="0" y="52" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="40" font-weight="800" fill="#FFFFFF">{cur}</text>
    <text x="0" y="74" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="14" fill="#36BCF7">Current Streak</text>
    <text x="0" y="93" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="11" fill="#8b949e">{cur_sub}</text>
  </g>
  <g transform="translate(750,97)">
    <text x="0" y="-30" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="14" fill="#36BCF7">Longest Streak</text>
    <text x="0" y="16" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="40" font-weight="800" fill="url(#g1)">{lng}</text>
    <text x="0" y="42" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="11" fill="#8b949e">{lng_sub}</text>
  </g>
</svg>"""

def generate_legacy_weekly_streak_svg(this_week, cur, cur_s, cur_e, lng, lng_s, lng_e):
    cur_sub = fmt_week(cur_s) if cur > 0 else "No active streak"
    lng_sub = fmt_range_weekly(lng_s, lng_e)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 195" width="500" height="195">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#36BCF7"/>
      <stop offset="100%" stop-color="#1a7db5"/>
    </linearGradient>
    <linearGradient id="g2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FF6EC7"/>
      <stop offset="100%" stop-color="#c44ea8"/>
    </linearGradient>
    <clipPath id="cl"><rect rx="10" ry="10" width="500" height="195"/></clipPath>
  </defs>
  <rect clip-path="url(#cl)" width="500" height="195" fill="#0D1117"/>
  <rect width="500" height="2" fill="url(#g1)" opacity="0.85"/>
  <line x1="166" y1="18" x2="166" y2="177" stroke="#21262d" stroke-width="1"/>
  <line x1="334" y1="18" x2="334" y2="177" stroke="#21262d" stroke-width="1"/>
  <g transform="translate(83,97)">
    <text x="0" y="-30" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="12" fill="#FF6EC7">This Week</text>
    <text x="0" y="14" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="36" font-weight="800" fill="url(#g1)">{this_week}</text>
    <text x="0" y="38" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="10" fill="#8b949e">contributions</text>
  </g>
  <g transform="translate(250,97)">
    <circle cx="0" cy="-22" r="44" fill="none" stroke="#36BCF712" stroke-width="8"/>
    <circle cx="0" cy="-22" r="44" fill="none" stroke="url(#g1)" stroke-width="2.5" opacity="0.9"/>
    <text x="0" y="-12" text-anchor="middle" font-size="24">🔥</text>
    <text x="0" y="46" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="36" font-weight="800" fill="#FFFFFF">{cur}</text>
    <text x="0" y="66" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="12" fill="#FF6EC7">Weekly Streak</text>
    <text x="0" y="84" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="10" fill="#8b949e">{cur_sub}</text>
  </g>
  <g transform="translate(417,97)">
    <text x="0" y="-30" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="12" fill="#FF6EC7">Longest Weekly</text>
    <text x="0" y="14" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="36" font-weight="800" fill="url(#g2)">{lng}</text>
    <text x="0" y="38" text-anchor="middle" font-family="'Segoe UI',Ubuntu,sans-serif" font-size="10" fill="#8b949e">{lng_sub}</text>
  </g>
</svg>"""

def fetch_language_stats(repos_data):
    """Fetch detailed language byte counts across all non-fork repos."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    language_bytes = {}
    for repo in repos_data:
        if not isinstance(repo, dict) or repo.get("fork"):
            continue
        lang_url = repo.get("languages_url", "")
        if not lang_url:
            continue
        try:
            r = requests.get(lang_url, headers=headers, timeout=10)
            if r.status_code == 200:
                for lang, byte_count in r.json().items():
                    language_bytes[lang] = language_bytes.get(lang, 0) + byte_count
        except Exception:
            continue
    return language_bytes

def generate_github_stats_svg(total_contribs, cur_streak, lng_streak, followers, repos, stars):
    """Generate a self-hosted GitHub stats card SVG in radical theme."""
    score = (stars * 2) + (total_contribs * 0.5) + (followers * 3) + (repos * 1)
    if score >= 5000: rank = "S+"
    elif score >= 2000: rank = "S"
    elif score >= 1000: rank = "A++"
    elif score >= 500: rank = "A+"
    elif score >= 200: rank = "A"
    elif score >= 100: rank = "B+"
    else: rank = "B"

    radius = 40
    circ = 2 * 3.14159265 * radius
    progress = min(score / 2000, 1.0)
    dash = circ * progress
    gap = circ - dash

    items = [
        ("Total Stars Earned", str(stars), "#f8d847"),
        ("Total Contributions", str(total_contribs), "#fe428e"),
        ("Current Streak", f"{cur_streak} days", "#a9fef7"),
        ("Public Repos", str(repos), "#36bcf7"),
        ("Followers", str(followers), "#39d353"),
    ]

    rows = ""
    for i, (label, value, color) in enumerate(items):
        y = 25 * i
        rows += (
            f'    <g transform="translate(0, {y})">'
            f'<circle cx="8" cy="-4" r="5" fill="{color}"/>'
            f'<text x="22" y="0" font-family="\'Segoe UI\', Ubuntu, \'Helvetica Neue\', sans-serif" font-size="14" fill="#a9fef7">{label}:</text>'
            f'<text x="270" y="0" text-anchor="end" font-family="\'Segoe UI\', Ubuntu, \'Helvetica Neue\', sans-serif" font-size="14" fill="#a9fef7" font-weight="bold">{value}</text>'
            f'</g>\n'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195">
  <defs>
    <linearGradient id="rg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fe428e"/>
      <stop offset="100%" stop-color="#f8d847"/>
    </linearGradient>
  </defs>
  <rect x="0.5" y="0.5" rx="4.5" width="494" height="194" fill="#141321"/>
  <g transform="translate(25, 35)">
    <text font-family="'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif" font-size="18" font-weight="bold" fill="#fe428e">Nishant's GitHub Stats</text>
  </g>
  <g transform="translate(25, 65)">
{rows}  </g>
  <g transform="translate(420, 97)">
    <circle cx="0" cy="0" r="{radius}" fill="none" stroke="#f8d84720" stroke-width="6"/>
    <circle cx="0" cy="0" r="{radius}" fill="none" stroke="url(#rg)" stroke-width="6" stroke-dasharray="{dash:.1f} {gap:.1f}" transform="rotate(-90)" stroke-linecap="round"/>
    <text x="0" y="10" text-anchor="middle" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="30" font-weight="bold" fill="#f8d847">{rank}</text>
  </g>
</svg>"""

def generate_top_langs_svg(language_bytes):
    """Generate a self-hosted top languages card SVG in radical theme."""
    if not language_bytes:
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="495" height="120" viewBox="0 0 495 120">'
                '<rect x="0.5" y="0.5" rx="4.5" width="494" height="119" fill="#141321"/>'
                '<text x="25" y="35" font-family="\'Segoe UI\', Ubuntu, sans-serif" font-size="18" font-weight="bold" fill="#fe428e">Most Used Languages</text>'
                '<text x="25" y="70" font-family="\'Segoe UI\', Ubuntu, sans-serif" font-size="14" fill="#a9fef7">No language data available</text>'
                '</svg>')

    total = sum(language_bytes.values())
    sorted_langs = sorted(language_bytes.items(), key=lambda x: x[1], reverse=True)[:8]
    bar_w = 445

    segs = ""
    xo = 0.0
    for lang, bc in sorted_langs:
        w = bar_w * (bc / total)
        c = LANG_COLORS.get(lang, "#8b949e")
        segs += f'      <rect x="{xo:.1f}" y="0" width="{max(w, 0.5):.1f}" height="8" fill="{c}"/>\n'
        xo += w

    legend = ""
    for i, (lang, bc) in enumerate(sorted_langs):
        pct = bc / total * 100
        c = LANG_COLORS.get(lang, "#8b949e")
        x = (i % 2) * 220
        y = (i // 2) * 25
        legend += (
            f'    <g transform="translate({x}, {y})">'
            f'<circle cx="5" cy="-3" r="5" fill="{c}"/>'
            f'<text x="15" y="1" font-family="\'Segoe UI\', Ubuntu, sans-serif" font-size="11.5" fill="#a9fef7">{lang} {pct:.2f}%</text>'
            f'</g>\n'
        )

    n_rows = (len(sorted_langs) + 1) // 2
    th = 80 + n_rows * 25 + 5

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="{th}" viewBox="0 0 495 {th}">
  <rect x="0.5" y="0.5" rx="4.5" width="494" height="{th - 1}" fill="#141321"/>
  <text x="25" y="35" font-family="'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif" font-size="18" font-weight="bold" fill="#fe428e">Most Used Languages</text>
  <g transform="translate(25, 50)">
    <clipPath id="lc">
      <rect x="0" y="0" width="{bar_w}" height="8" rx="5"/>
    </clipPath>
    <g clip-path="url(#lc)">
{segs}    </g>
  </g>
  <g transform="translate(25, 75)">
{legend}  </g>
</svg>"""

def generate_contribution_skyline_svg(all_days, total_contributions, cur_streak, lng_streak, cur_w_streak, this_week_contribs):
    """Generate 3D Isometric Contribution Skyline and Activity Matrix SVG."""
    day_counts = {d["date"]: d["count"] for d in all_days}
    today = date.today()
    start_date = today - timedelta(days=52 * 7 - 1)
    start_date -= timedelta(days=(start_date.weekday() + 1) % 7)

    YAW_3D = math.pi / 4
    ELEV_3D = (34 * math.pi) / 180
    cs = math.cos(YAW_3D)
    sn = math.sin(YAW_3D)
    se = math.sin(ELEV_3D)
    ce = math.cos(ELEV_3D)

    scale = 16.2
    ox = 185.0
    oy = 175.0

    def px(x, y, z):
        px_val = x * cs - y * sn
        return ox + px_val * scale

    def py(x, y, z):
        py_val = (x * sn + y * cs) * se - z * ce
        return oy + py_val * scale

    max_count = max(day_counts.values()) if day_counts else 100
    bars = []
    month_anchors = []
    prev_month = None

    for w in range(53):
        for d in range(7):
            dt = start_date + timedelta(days=w * 7 + d)
            if dt > today:
                continue
            c = day_counts.get(dt.strftime("%Y-%m-%d"), 0)
            depth = (w + 0.5) * sn + (d + 0.5) * cs
            bars.append((depth, w, d, c, dt))

            if d == 0:
                m_str = dt.strftime("%b")
                if m_str != prev_month:
                    month_anchors.append((w, m_str))
                    prev_month = m_str

    bars.sort(key=lambda b: b[0])

    w_bar = 0.82
    off = (1.0 - w_bar) / 2.0
    svg_elements = []

    for depth, w, d, c, dt in bars:
        x0 = w + off
        y0 = d + off
        x1 = x0 + w_bar
        y1 = y0 + w_bar

        if c > 0:
            h = 0.35 + math.pow(c / max_count, 0.85) * 5.2
        else:
            h = 0.12

        if c == 0:
            top_color = "#161b22"
            left_color = "#0e1319"
            right_color = "#0a0e14"
            edge_color = "#21262d"
        elif c <= 5:
            top_color = "#238636"
            left_color = "#196c2e"
            right_color = "#145524"
            edge_color = "#2ea043"
        elif c <= 20:
            top_color = "#2ea043"
            left_color = "#238636"
            right_color = "#1b682b"
            edge_color = "#3fb950"
        elif c <= 60:
            top_color = "#36bcf7"
            left_color = "#2298cc"
            right_color = "#17739e"
            edge_color = "#79c0ff"
        else:
            top_color = "#fe428e"
            left_color = "#d93275"
            right_color = "#ab2159"
            edge_color = "#ff79b8"

        pt1 = f"{px(x0, y0, h):.1f},{py(x0, y0, h):.1f}"
        pt2 = f"{px(x1, y0, h):.1f},{py(x1, y0, h):.1f}"
        pt3 = f"{px(x1, y1, h):.1f},{py(x1, y1, h):.1f}"
        pt4 = f"{px(x0, y1, h):.1f},{py(x0, y1, h):.1f}"

        pl1 = f"{px(x0, y1, 0):.1f},{py(x0, y1, 0):.1f}"
        pl2 = f"{px(x1, y1, 0):.1f},{py(x1, y1, 0):.1f}"
        pl3 = pt3
        pl4 = pt4

        pr1 = f"{px(x1, y0, 0):.1f},{py(x1, y0, 0):.1f}"
        pr2 = f"{px(x1, y1, 0):.1f},{py(x1, y1, 0):.1f}"
        pr3 = pt3
        pr4 = pt2

        svg_elements.append(f'<polygon points="{pl1} {pl2} {pl3} {pl4}" fill="{left_color}" />')
        svg_elements.append(f'<polygon points="{pr1} {pr2} {pr3} {pr4}" fill="{right_color}" />')
        svg_elements.append(f'<polygon points="{pt1} {pt2} {pt3} {pt4}" fill="{top_color}" stroke="{edge_color}" stroke-width="0.4" />')

    month_svgs = []
    for mw, mname in month_anchors:
        mx = px(mw + 0.5, 7.2, 0)
        my = py(mw + 0.5, 7.2, 0) + 4
        month_svgs.append(f'<text x="{mx:.1f}" y="{my:.1f}" font-family="\'Segoe UI\',Ubuntu,sans-serif" font-size="9.5" fill="#8b949e" text-anchor="middle">{mname}</text>')

    skyline_bars_str = "\\n    ".join(svg_elements)
    month_labels_str = "\\n    ".join(month_svgs)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 540" width="950" height="540">
  <defs>
    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#36BCF7" />
      <stop offset="50%" stop-color="#fe428e" />
      <stop offset="100%" stop-color="#f8d847" />
    </linearGradient>
    <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#36BCF7" stop-opacity="0.4" />
      <stop offset="50%" stop-color="#fe428e" stop-opacity="0.6" />
      <stop offset="100%" stop-color="#f8d847" stop-opacity="0.4" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <rect x="1" y="1" width="948" height="538" rx="18" fill="#0D1117" stroke="url(#borderGrad)" stroke-width="1.5" />
  <circle cx="475" cy="270" r="280" fill="#36bcf7" opacity="0.02" filter="url(#glow)" />
  <circle cx="800" cy="380" r="220" fill="#fe428e" opacity="0.025" filter="url(#glow)" />

  <g transform="translate(30, 36)">
    <text x="0" y="0" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="18" font-weight="bold" fill="url(#headerGrad)" letter-spacing="0.5">
      CONTRIBUTION SKYLINE &amp; ACTIVITY MATRIX
    </text>
    <text x="0" y="20" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="12" fill="#8b949e">
      Isometric Trajectory Analysis · {total_contributions:,} Total Contributions · Active Neural Uplink
    </text>
    <g transform="translate(770, -14)">
      <rect x="0" y="0" width="115" height="26" rx="6" fill="#161b22" stroke="#30363d" stroke-width="1" />
      <rect x="2" y="2" width="56" height="22" rx="4" fill="#21262d" />
      <text x="30" y="16" text-anchor="middle" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="11" font-weight="600" fill="#36BCF7">3D Skyline</text>
      <text x="85" y="16" text-anchor="middle" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="11" font-weight="500" fill="#8b949e">2D Grid</text>
    </g>
  </g>

  <g transform="translate(30, 78)">
    <rect x="0" y="0" width="205" height="46" rx="8" fill="#161b22" stroke="#21262d" stroke-width="1" />
    <text x="14" y="18" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="11" fill="#8b949e">1 Year Total</text>
    <text x="14" y="37" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="16" font-weight="bold" fill="#36BCF7">{total_contributions:,} <tspan font-size="11" font-weight="normal" fill="#8b949e">contribs</tspan></text>

    <rect x="225" y="0" width="205" height="46" rx="8" fill="#161b22" stroke="#21262d" stroke-width="1" />
    <text x="239" y="18" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="11" fill="#8b949e">Current Streak</text>
    <text x="239" y="37" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="16" font-weight="bold" fill="#FF6EC7">{cur_streak} Days <tspan font-size="12">🔥</tspan></text>

    <rect x="450" y="0" width="205" height="46" rx="8" fill="#161b22" stroke="#21262d" stroke-width="1" />
    <text x="464" y="18" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="11" fill="#8b949e">Longest Streak</text>
    <text x="464" y="37" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="16" font-weight="bold" fill="#39d353">{lng_streak} Days <tspan font-size="11" font-weight="normal" fill="#8b949e">(unbroken)</tspan></text>

    <rect x="675" y="0" width="210" height="46" rx="8" fill="#161b22" stroke="#21262d" stroke-width="1" />
    <text x="689" y="18" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="11" fill="#8b949e">Busiest Day</text>
    <text x="689" y="37" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="16" font-weight="bold" fill="#f8d847">{max_count} <tspan font-size="11" font-weight="normal" fill="#8b949e">in 24 hrs</tspan></text>
  </g>

  <g id="skyline-bars">
    {skyline_bars_str}
  </g>

  <g id="month-labels">
    {month_labels_str}
  </g>

  <g transform="translate(30, 485)">
    <g transform="translate(0, 8)">
      <text x="0" y="9" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="11" fill="#8b949e">Less</text>
      <rect x="30" y="0" width="10" height="10" rx="2" fill="#161b22" stroke="#21262d" stroke-width="0.5" />
      <rect x="44" y="0" width="10" height="10" rx="2" fill="#238636" />
      <rect x="58" y="0" width="10" height="10" rx="2" fill="#2ea043" />
      <rect x="72" y="0" width="10" height="10" rx="2" fill="#36bcf7" />
      <rect x="86" y="0" width="10" height="10" rx="2" fill="#fe428e" />
      <text x="102" y="9" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="11" fill="#8b949e">More</text>
    </g>

    <g transform="translate(420, 0)">
      <text x="0" y="17" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="11" font-weight="600" fill="#8b949e">TOP NODES:</text>
      <g transform="translate(80, 0)">
        <rect x="0" y="0" width="130" height="24" rx="12" fill="#161b22" stroke="#30363d" stroke-width="1" />
        <circle cx="12" cy="12" r="7" fill="#fe428e" />
        <text x="12" y="15" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#fff">M</text>
        <text x="26" y="16" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="600" fill="#fff">META</text>
        <text x="118" y="16" text-anchor="end" font-family="'Segoe UI', sans-serif" font-size="10" fill="#36BCF7">94% Acc</text>
      </g>
      <g transform="translate(220, 0)">
        <rect x="0" y="0" width="130" height="24" rx="12" fill="#161b22" stroke="#30363d" stroke-width="1" />
        <circle cx="12" cy="12" r="7" fill="#36BCF7" />
        <text x="12" y="15" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#fff">S</text>
        <text x="26" y="16" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="600" fill="#fff">SVIT ERP</text>
        <text x="118" y="16" text-anchor="end" font-family="'Segoe UI', sans-serif" font-size="10" fill="#39d353">10k+ N</text>
      </g>
      <g transform="translate(360, 0)">
        <rect x="0" y="0" width="125" height="24" rx="12" fill="#161b22" stroke="#30363d" stroke-width="1" />
        <circle cx="12" cy="12" r="7" fill="#f8d847" />
        <text x="12" y="15" text-anchor="middle" font-family="'Segoe UI', sans-serif" font-size="9" font-weight="bold" fill="#141321">V</text>
        <text x="26" y="16" font-family="'Segoe UI', sans-serif" font-size="11" font-weight="600" fill="#fff">Vardant</text>
        <text x="113" y="16" text-anchor="end" font-family="'Segoe UI', sans-serif" font-size="10" fill="#f8d847">DeFi</text>
      </g>
    </g>
  </g>
</svg>"""

def main():
    print("Fetching GitHub REST API stats...")
    followers, repos, stars, repos_data = fetch_github_api_stats()
    print(f"API stats: followers={followers}, repos={repos}, stars={stars}")

    print("Fetching contribution data year-by-year...")
    today = date.today()
    all_days = []
    total_contributions = 0
    start_year = 2020
    
    for yr in range(start_year, today.year + 1):
        print(f"  Fetching {yr}...")
        year_days = fetch_contributions_for_year(yr)
        year_total = sum(x["count"] for x in year_days)
        total_contributions += year_total
        all_days.extend(year_days)
        print(f"  Year {yr}: {year_total} contributions")

    # De-duplicate and sort
    all_days = sorted({d["date"]: d for d in all_days}.values(), key=lambda x: x["date"])

    # Safety guardrail: Never wipe valid streak data with 0 if fetch was rate-limited or failed
    if total_contributions == 0 or len(all_days) == 0:
        print("CRITICAL ERROR: Failed to fetch contribution data (0 contributions found).", file=sys.stderr)
        print("Aborting update to prevent overwriting existing valid streak files with zeros.", file=sys.stderr)
        sys.exit(1)

    # Compute daily streaks
    cur_streak, cur_s, cur_e, lng_streak, lng_s, lng_e = calc_daily_streaks(all_days)
    print(f"Daily Streak: Current={cur_streak}, Longest={lng_streak}")

    # Compute weekly streaks
    weeks = build_week_map(all_days)
    cur_w_streak, cur_w_s, cur_w_e, lng_w_streak, lng_w_s, lng_w_e, this_week_contribs = calc_weekly_streaks(weeks)
    print(f"Weekly Streak: Current={cur_w_streak}, Longest={lng_w_streak}, This Week={this_week_contribs}")

    # Save SVG outputs using templates
    if not os.path.exists("dark_template.svg") or not os.path.exists("light_template.svg"):
        print("Warning: templates not found. Running ascii_to_svg.py first...")
        os.system("python ascii_to_svg.py")
        
    with open("dark_template.svg", "r", encoding="utf-8") as f:
        dark_svg = f.read()
    with open("light_template.svg", "r", encoding="utf-8") as f:
        light_svg = f.read()

    # Replacements dictionary
    replacements = {
        "{{TOTAL_CONTRIBUTIONS}}": str(total_contributions),
        "{{CURRENT_STREAK}}": str(cur_streak),
        "{{LONGEST_STREAK}}": str(lng_streak),
        "{{WEEKLY_STREAK}}": str(cur_w_streak),
        "{{LONGEST_WEEKLY}}": str(lng_w_streak),
        "{{THIS_WEEK_CONTRIBUTIONS}}": str(this_week_contribs),
        "{{FOLLOWERS}}": str(followers),
        "{{REPOS}}": str(repos),
        "{{STARS}}": str(stars),
    }

    # Perform replacements
    for key, val in replacements.items():
        dark_svg = dark_svg.replace(key, val)
        light_svg = light_svg.replace(key, val)

    with open("dark.svg", "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print("Saved dark.svg")

    with open("light.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    print("Saved light.svg")

    # Generate and save legacy streak panel SVGs
    os.makedirs("profile", exist_ok=True)
    
    legacy_streak_svg = generate_legacy_streak_svg(total_contributions, cur_streak, cur_s, cur_e, lng_streak, lng_s, lng_e)
    with open("profile/streak.svg", "w", encoding="utf-8") as f:
        f.write(legacy_streak_svg)
    print("Saved profile/streak.svg")

    legacy_weekly_streak_svg = generate_legacy_weekly_streak_svg(this_week_contribs, cur_w_streak, cur_w_s, cur_w_e, lng_w_streak, lng_w_s, lng_w_e)
    with open("profile/streak-weekly.svg", "w", encoding="utf-8") as f:
        f.write(legacy_weekly_streak_svg)
    print("Saved profile/streak-weekly.svg")

    # Generate self-hosted stats cards (replaces external github-readme-stats)
    print("Fetching language stats...")
    language_bytes = fetch_language_stats(repos_data)
    print(f"  Languages found: {len(language_bytes)}")

    github_stats_svg = generate_github_stats_svg(
        total_contributions, cur_streak, lng_streak, followers, repos, stars
    )
    with open("profile/github-stats.svg", "w", encoding="utf-8") as f:
        f.write(github_stats_svg)
    print("Saved profile/github-stats.svg")

    top_langs_svg = generate_top_langs_svg(language_bytes)
    with open("profile/top-langs.svg", "w", encoding="utf-8") as f:
        f.write(top_langs_svg)
    print("Saved profile/top-langs.svg")

    # Generate Contribution Skyline & Activity Matrix SVG
    skyline_svg = generate_contribution_skyline_svg(
        all_days, total_contributions, cur_streak, lng_streak, cur_w_streak, this_week_contribs
    )
    with open("profile/contribution-skyline.svg", "w", encoding="utf-8") as f:
        f.write(skyline_svg)
    print("Saved profile/contribution-skyline.svg")

if __name__ == "__main__":
    main()
