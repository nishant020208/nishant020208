#!/usr/bin/env python3
import os
import sys
import re
import requests
import urllib3
from datetime import date, timedelta
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USERNAME = "nishant020208"
GRAPHQL_URL = "https://api.github.com/graphql"

def fetch_github_api_stats():
    """Fetch followers, repos, and stars from GitHub REST API."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
        
    followers = 0
    public_repos = 0
    stars = 0
    
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
        # We will keep default values of 0 if API fails
        
    return followers, public_repos, stars

def fetch_contributions_for_year(year):
    """Fetch contribution days for a specific year using HTML scraping."""
    url = f"https://github.com/users/{USERNAME}/contributions?from={year}-01-01&to={year}-12-31"
    try:
        resp = requests.get(url, verify=False, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching contributions for year {year}: {e}", file=sys.stderr)
        return []
        
    soup = BeautifulSoup(resp.text, 'html.parser')
    tds = soup.find_all('td', class_='ContributionCalendar-day')
    day_map = {td.get('id'): td.get('data-date') for td in tds if td.get('id') and td.get('data-date')}
    
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
    # Return only days belonging to the requested year
    return [x for x in all_days if x["date"].startswith(str(year))]

def calc_daily_streaks(all_days):
    today = date.today()
    day_map = {d["date"]: d["count"] for d in all_days}

    today_str = today.strftime("%Y-%m-%d")
    yesterday_str = (today - timedelta(1)).strftime("%Y-%m-%d")

    # Determine starting point for current streak
    if day_map.get(today_str, 0) > 0:
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

def main():
    print("Fetching GitHub REST API stats...")
    followers, repos, stars = fetch_github_api_stats()
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

if __name__ == "__main__":
    main()
