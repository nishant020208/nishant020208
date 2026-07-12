#!/usr/bin/env python3
"""
Generate GitHub streak stats SVG using GitHub GraphQL API.
Produces profile/streak.svg with real contribution data.
"""

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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
        verify=False,
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


def calc_streaks(all_days):
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


def fmt_range(s, e):
    if not s or not e:
        return "No active streak"
    if s == e:
        return s.strftime("%b %d, %Y")
    return f"{s.strftime('%b %d')} – {e.strftime('%b %d, %Y')}"


def make_svg(total, cur, cur_s, cur_e, lng, lng_s, lng_e):
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


def main():
    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    today = date.today()
    all_days = []
    total = 0

    start_year = 2020
    for yr in range(start_year, today.year + 1):
        print(f"  Fetching {yr}...")
        t, days = fetch_year(yr)
        total += t
        all_days.extend(days)

    print(f"  Total contributions: {total}")
    cur, cur_s, cur_e, lng, lng_s, lng_e = calc_streaks(all_days)
    print(f"  Current streak : {cur}")
    print(f"  Longest streak : {lng}")

    svg = make_svg(total, cur, cur_s, cur_e, lng, lng_s, lng_e)
    os.makedirs("profile", exist_ok=True)
    with open("profile/streak.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("  Saved profile/streak.svg")


if __name__ == "__main__":
    main()
