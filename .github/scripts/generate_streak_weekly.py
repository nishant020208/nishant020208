#!/usr/bin/env python3
"""
Generate GitHub weekly streak stats SVG using GitHub GraphQL API.
Produces profile/streak-weekly.svg with real weekly contribution data.
"""

import os
import sys
import requests
from datetime import date, timedelta

USERNAME = "nishant020208"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
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


def fetch_year(year):
    resp = requests.post(
        GRAPHQL_URL,
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        json={
            "query": QUERY,
            "variables": {
                "username": USERNAME,
                "from": f"{year}-01-01T00:00:00Z",
                "to": f"{year}-12-31T23:59:59Z",
            },
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = []
    for week in cal["weeks"]:
        for d in week["contributionDays"]:
            days.append({"date": d["date"], "count": d["contributionCount"]})
    return cal["totalContributions"], days


def build_week_map(all_days):
    """Group days into ISO weeks (Mon–Sun), return ordered list of weeks."""
    week_contributions = {}
    for day in all_days:
        dt = date.fromisoformat(day["date"])
        # ISO week: Monday = 0
        week_start = dt - timedelta(days=dt.weekday())
        key = week_start.strftime("%Y-%m-%d")
        week_contributions[key] = week_contributions.get(key, 0) + day["count"]

    weeks = sorted(week_contributions.items())  # [(date_str, count), ...]
    return weeks


def calc_weekly_streaks(weeks):
    today = date.today()
    # Current week start (Monday)
    this_week_start = today - timedelta(days=today.weekday())
    last_week_start = this_week_start - timedelta(7)

    week_map = {w[0]: w[1] for w in weeks}

    # This week's contributions
    this_week_count = week_map.get(this_week_start.strftime("%Y-%m-%d"), 0)
    last_week_count = week_map.get(last_week_start.strftime("%Y-%m-%d"), 0)

    # Current weekly streak — count backward from this week or last week
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

    # Longest weekly streak
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
    if s == e or (e - s).days <= 6:
        return f"Week of {s.strftime('%b %d, %Y')}"
    return f"{s.strftime('%b %d')} – {e.strftime('%b %d, %Y')}"


def fmt_week(s):
    if not s:
        return ""
    return f"Week of {s.strftime('%b %d, %Y')}"


def make_svg(this_week, cur, cur_s, cur_e, lng, lng_s, lng_e):
    cur_sub = fmt_week(cur_s) if cur > 0 else "No active streak"
    lng_sub = fmt_range(lng_s, lng_e)

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
    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    today = date.today()
    all_days = []

    start_year = 2020
    for yr in range(start_year, today.year + 1):
        print(f"  Fetching {yr}...")
        _, days = fetch_year(yr)
        all_days.extend(days)

    weeks = build_week_map(all_days)
    cur, cur_s, cur_e, lng, lng_s, lng_e, this_week = calc_weekly_streaks(weeks)

    print(f"  This week     : {this_week}")
    print(f"  Weekly streak : {cur}")
    print(f"  Longest weekly: {lng}")

    svg = make_svg(this_week, cur, cur_s, cur_e, lng, lng_s, lng_e)
    os.makedirs("profile", exist_ok=True)
    with open("profile/streak-weekly.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("  Saved profile/streak-weekly.svg")


if __name__ == "__main__":
    main()
