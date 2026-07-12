#!/usr/bin/env python3
import os
import sys
from PIL import Image

def image_to_ascii(image_path, width=56, is_light=False):
    if not os.path.exists(image_path):
        print(f"Error: {image_path} does not exist.", file=sys.stderr)
        return ""

    # Open image
    img = Image.open(image_path)
    
    # Crop to a square centered around the middle
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    img = img.crop((left, top, right, bottom))
    
    # Convert to grayscale
    img = img.convert("L")
    
    # We want rows to fit nicely. Monospace font characters are typically 1.6x taller than wide.
    # To maintain aspect ratio when converting to characters:
    # row_height = col_width * 1.6
    # So to get a square image, we make height = int(width / 1.3)
    height = int(width / 1.3)
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    # Density ramps
    # For dark background: 0 (black) is space (dark bg shows), 255 (white) is dense char (glowy cyan shows)
    # For light background: 255 (white) is space (light bg shows), 0 (black) is dense char (dark ink shows)
    if is_light:
        ramp = "@%#*+=-:. "
    else:
        ramp = " .:-=+*#%@"
        
    ascii_rows = []
    for y in range(img.height):
        row_chars = []
        for x in range(img.width):
            val = img.getpixel((x, y))
            idx = int(val / 256 * len(ramp))
            row_chars.append(ramp[idx])
        ascii_rows.append("".join(row_chars))
        
    return ascii_rows

def generate_svg_text(ascii_rows, x=30, dy=8.2):
    lines = []
    for i, row in enumerate(ascii_rows):
        # Escape XML entities in ASCII characters
        escaped_row = row.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        current_dy = 0 if i == 0 else dy
        lines.append(f'<tspan x="{x}" dy="{current_dy}">{escaped_row}</tspan>')
    return "\n  ".join(lines)

def make_templates():
    profile_img = "profile.png"
    if not os.path.exists(profile_img):
        print(f"Warning: {profile_img} not found. Running with placeholder ASCII.", file=sys.stderr)
        # Create a placeholder image
        img = Image.new("L", (100, 100), color=128)
        img.save(profile_img)
        
    print("Converting profile image to ASCII...")
    dark_ascii_rows = image_to_ascii(profile_img, width=56, is_light=False)
    light_ascii_rows = image_to_ascii(profile_img, width=56, is_light=True)
    
    dark_ascii_svg = generate_svg_text(dark_ascii_rows, x=30, dy=8.2)
    light_ascii_svg = generate_svg_text(light_ascii_rows, x=30, dy=8.2)
    
    # Dark template SVG
    dark_template = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 470" width="100%" height="100%">
  <style>
    @keyframes blink {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0; }}
    }}
    @keyframes flicker {{
      0%, 19.999%, 22%, 62.999%, 64%, 64.999%, 70%, 100% {{ opacity: 0.99; filter: drop-shadow(0 0 2px rgba(0,255,240,0.4)); }}
      20%, 21.999%, 63%, 63.999%, 65%, 69.999% {{ opacity: 0.95; filter: drop-shadow(0 0 1px rgba(0,255,240,0.15)); }}
    }}
    .cursor {{
      animation: blink 1s infinite;
      fill: #00fff0;
    }}
    .flicker-group {{
      animation: flicker 6s infinite;
    }}
    .ascii-text {{
      font-family: 'Fira Code', 'JetBrains Mono', Consolas, Monaco, monospace;
      font-size: 9.5px;
      fill: #00fff0;
      white-space: pre;
    }}
    .terminal-text {{
      font-family: 'Fira Code', 'JetBrains Mono', Consolas, Monaco, monospace;
      font-size: 12.5px;
    }}
    .label {{
      fill: #ff00d4;
      font-weight: bold;
    }}
    .value {{
      fill: #ffffff;
    }}
    .command {{
      fill: #00fff0;
      font-weight: bold;
    }}
    .prompt {{
      fill: #39d353;
      font-weight: bold;
    }}
    .metric-label {{
      fill: #00fff0;
      font-weight: bold;
    }}
  </style>
  
  <defs>
    <linearGradient id="windowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#161b22" />
      <stop offset="100%" stop-color="#0d1117" />
    </linearGradient>
    <linearGradient id="scanlineGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#00fff0" stop-opacity="0" />
      <stop offset="50%" stop-color="#00fff0" stop-opacity="0.06" />
      <stop offset="100%" stop-color="#00fff0" stop-opacity="0" />
    </linearGradient>
  </defs>

  <!-- Terminal Shell Outline -->
  <rect x="15" y="15" width="920" height="440" rx="12" fill="#0d1117" stroke="#30363d" stroke-width="1.5" />
  <rect x="15" y="15" width="920" height="40" rx="12" fill="url(#windowGrad)" />
  <line x1="15" y1="55" x2="935" y2="55" stroke="#30363d" stroke-width="1" />
  
  <!-- Window Buttons -->
  <circle cx="40" cy="35" r="6" fill="#ff5f56" />
  <circle cx="60" cy="35" r="6" fill="#ffbd2e" />
  <circle cx="80" cy="35" r="6" fill="#27c93f" />
  
  <!-- Window Title -->
  <text x="475" y="40" text-anchor="middle" font-family="'Fira Code', 'JetBrains Mono', Consolas, monospace" font-size="13" fill="#8b949e">profile.sh --live</text>

  <!-- Split Panel Line -->
  <line x1="400" y1="55" x2="400" y2="455" stroke="#30363d" stroke-width="1" />

  <!-- Left Panel: ASCII Art -->
  <g class="flicker-group" transform="translate(0, 0)">
    <text class="ascii-text" x="30" y="85" xml:space="preserve">
  {dark_ascii_svg}
    </text>
    
    <!-- Scanning bar -->
    <rect x="30" y="75" width="340" height="3" fill="#00fff0" opacity="0.35" rx="1">
      <animate attributeName="y" values="75;425;75" dur="5s" repeatCount="indefinite" />
    </rect>
  </g>
  
  <!-- Scanline Screen Effect -->
  <rect x="25" y="75" width="355" height="360" fill="url(#scanlineGrad)" pointer-events="none" clip-path="url(#asciiClip)" opacity="0.4" />
  <clipPath id="asciiClip">
    <rect x="25" y="75" width="355" height="360" rx="6" />
  </clipPath>

  <!-- Right Panel: Terminal Output -->
  <g transform="translate(420, 75)">
    <text class="terminal-text" xml:space="preserve">
      <!-- Command prompt -->
      <tspan x="0" y="20" class="prompt">root@nishant-core:~#</tspan> <tspan class="command">cat profile.sh --live</tspan>
      
      <!-- Profile fields -->
      <tspan x="0" y="50" class="label">Subject:</tspan> <tspan class="value" dx="20">Nishant</tspan>
      <tspan x="0" y="75" class="label">Role:</tspan> <tspan class="value" dx="48">BE Undergrad — Full-Stack Dev</tspan>
      <tspan x="0" y="100" class="label">Origin:</tspan> <tspan class="value" dx="32">Gujarat, India</tspan>
      <tspan x="0" y="125" class="label">Education:</tspan> <tspan class="value" dx="8">B.Tech CE, SVIT Vasad (GTU)</tspan>
      <tspan x="0" y="150" class="label">Status:</tspan> <tspan class="value" dx="32">Building 3D renders + shipping web apps</tspan>
      
      <tspan x="0" y="180" class="label">Core Lang:</tspan> <tspan class="value" dx="10">C, JavaScript, Python</tspan>
      <tspan x="0" y="205" class="label">Frontend:</tspan> <tspan class="value" dx="18">React, HTML, CSS</tspan>
      <tspan x="0" y="230" class="label">Backend:</tspan> <tspan class="value" dx="26">Node.js, Supabase</tspan>
      <tspan x="0" y="255" class="label">Creative:</tspan> <tspan class="value" dx="18">Blender (3D rendering, product/car scenes)</tspan>
      
      <!-- Contact Details -->
      <tspan x="0" y="285" class="label">Contact:</tspan> <tspan class="value" dx="26">nishant020208@gmail.com | nishant08-portfolio.vercel.app</tspan>
      
      <!-- Command prompt 2 -->
      <tspan x="0" y="315" class="prompt">root@nishant-core:~#</tspan> <tspan class="command">./fetch_stats.sh --live</tspan>
      
      <!-- Live GitHub Stats -->
      <tspan x="0" y="340" class="metric-label">Contributions:</tspan> <tspan class="value" dx="5">{{TOTAL_CONTRIBUTIONS}} (2020 – 2026)</tspan>
      <tspan x="0" y="360" class="metric-label">Daily Streak:</tspan> <tspan class="value" dx="15">{{CURRENT_STREAK}} days</tspan> <tspan class="label" dx="5">|</tspan> <tspan class="metric-label" dx="5">Longest:</tspan> <tspan class="value" dx="5">{{LONGEST_STREAK}} days</tspan>
      <tspan x="0" y="380" class="metric-label">Weekly Streak:</tspan> <tspan class="value" dx="5">{{WEEKLY_STREAK}} weeks (This Week: {{THIS_WEEK_CONTRIBUTIONS}})</tspan>
      <tspan x="0" y="400" class="metric-label">GitHub Nodes:</tspan> <tspan class="value" dx="10">Followers: {{FOLLOWERS}} | Repos: {{REPOS}} | Stars: {{STARS}}</tspan>
    </text>
    
    <!-- Blinking Cursor -->
    <rect x="290" y="303" width="8" height="15" class="cursor" />
  </g>
</svg>
"""

    # Light template SVG
    light_template = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 470" width="100%" height="100%">
  <style>
    @keyframes blink {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0; }}
    }}
    @keyframes flicker {{
      0%, 19.999%, 22%, 62.999%, 64%, 64.999%, 70%, 100% {{ opacity: 0.99; filter: drop-shadow(0 0 1px rgba(0,102,102,0.15)); }}
      20%, 21.999%, 63%, 63.999%, 65%, 69.999% {{ opacity: 0.96; }}
    }}
    .cursor {{
      animation: blink 1s infinite;
      fill: #006666;
    }}
    .flicker-group {{
      animation: flicker 8s infinite;
    }}
    .ascii-text {{
      font-family: 'Fira Code', 'JetBrains Mono', Consolas, Monaco, monospace;
      font-size: 9.5px;
      fill: #24292f;
      white-space: pre;
    }}
    .terminal-text {{
      font-family: 'Fira Code', 'JetBrains Mono', Consolas, Monaco, monospace;
      font-size: 12.5px;
    }}
    .label {{
      fill: #860d80;
      font-weight: bold;
    }}
    .value {{
      fill: #24292f;
    }}
    .command {{
      fill: #006666;
      font-weight: bold;
    }}
    .prompt {{
      fill: #1a7f37;
      font-weight: bold;
    }}
    .metric-label {{
      fill: #006666;
      font-weight: bold;
    }}
  </style>
  
  <defs>
    <linearGradient id="windowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#f6f8fa" />
      <stop offset="100%" stop-color="#eaeef2" />
    </linearGradient>
    <linearGradient id="scanlineGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#006666" stop-opacity="0" />
      <stop offset="50%" stop-color="#006666" stop-opacity="0.02" />
      <stop offset="100%" stop-color="#006666" stop-opacity="0" />
    </linearGradient>
  </defs>

  <!-- Terminal Shell Outline -->
  <rect x="15" y="15" width="920" height="440" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="1.5" />
  <rect x="15" y="15" width="920" height="40" rx="12" fill="url(#windowGrad)" />
  <line x1="15" y1="55" x2="935" y2="55" stroke="#d0d7de" stroke-width="1" />
  
  <!-- Window Buttons -->
  <circle cx="40" cy="35" r="6" fill="#ff5f56" />
  <circle cx="60" cy="35" r="6" fill="#ffbd2e" />
  <circle cx="80" cy="35" r="6" fill="#27c93f" />
  
  <!-- Window Title -->
  <text x="475" y="40" text-anchor="middle" font-family="'Fira Code', 'JetBrains Mono', Consolas, monospace" font-size="13" fill="#57606a">profile.sh --live</text>

  <!-- Split Panel Line -->
  <line x1="400" y1="55" x2="400" y2="455" stroke="#d0d7de" stroke-width="1" />

  <!-- Left Panel: ASCII Art -->
  <g class="flicker-group" transform="translate(0, 0)">
    <text class="ascii-text" x="30" y="85" xml:space="preserve">
  {light_ascii_svg}
    </text>
    
    <!-- Scanning bar -->
    <rect x="30" y="75" width="340" height="3" fill="#006666" opacity="0.12" rx="1">
      <animate attributeName="y" values="75;425;75" dur="5s" repeatCount="indefinite" />
    </rect>
  </g>
  
  <!-- Scanline Screen Effect -->
  <rect x="25" y="75" width="355" height="360" fill="url(#scanlineGrad)" pointer-events="none" clip-path="url(#asciiClip)" opacity="0.2" />
  <clipPath id="asciiClip">
    <rect x="25" y="75" width="355" height="360" rx="6" />
  </clipPath>

  <!-- Right Panel: Terminal Output -->
  <g transform="translate(420, 75)">
    <text class="terminal-text" xml:space="preserve">
      <!-- Command prompt -->
      <tspan x="0" y="20" class="prompt">root@nishant-core:~#</tspan> <tspan class="command">cat profile.sh --live</tspan>
      
      <!-- Profile fields -->
      <tspan x="0" y="50" class="label">Subject:</tspan> <tspan class="value" dx="20">Nishant</tspan>
      <tspan x="0" y="75" class="label">Role:</tspan> <tspan class="value" dx="48">BE Undergrad — Full-Stack Dev</tspan>
      <tspan x="0" y="100" class="label">Origin:</tspan> <tspan class="value" dx="32">Gujarat, India</tspan>
      <tspan x="0" y="125" class="label">Education:</tspan> <tspan class="value" dx="8">B.Tech CE, SVIT Vasad (GTU)</tspan>
      <tspan x="0" y="150" class="label">Status:</tspan> <tspan class="value" dx="32">Building 3D renders + shipping web apps</tspan>
      
      <tspan x="0" y="180" class="label">Core Lang:</tspan> <tspan class="value" dx="10">C, JavaScript, Python</tspan>
      <tspan x="0" y="205" class="label">Frontend:</tspan> <tspan class="value" dx="18">React, HTML, CSS</tspan>
      <tspan x="0" y="230" class="label">Backend:</tspan> <tspan class="value" dx="26">Node.js, Supabase</tspan>
      <tspan x="0" y="255" class="label">Creative:</tspan> <tspan class="value" dx="18">Blender (3D rendering, product/car scenes)</tspan>
      
      <!-- Contact Details -->
      <tspan x="0" y="285" class="label">Contact:</tspan> <tspan class="value" dx="26">nishant020208@gmail.com | nishant08-portfolio.vercel.app</tspan>
      
      <!-- Command prompt 2 -->
      <tspan x="0" y="315" class="prompt">root@nishant-core:~#</tspan> <tspan class="command">./fetch_stats.sh --live</tspan>
      
      <!-- Live GitHub Stats -->
      <tspan x="0" y="340" class="metric-label">Contributions:</tspan> <tspan class="value" dx="5">{{TOTAL_CONTRIBUTIONS}} (2020 – 2026)</tspan>
      <tspan x="0" y="360" class="metric-label">Daily Streak:</tspan> <tspan class="value" dx="15">{{CURRENT_STREAK}} days</tspan> <tspan class="label" dx="5">|</tspan> <tspan class="metric-label" dx="5">Longest:</tspan> <tspan class="value" dx="5">{{LONGEST_STREAK}} days</tspan>
      <tspan x="0" y="380" class="metric-label">Weekly Streak:</tspan> <tspan class="value" dx="5">{{WEEKLY_STREAK}} weeks (This Week: {{THIS_WEEK_CONTRIBUTIONS}})</tspan>
      <tspan x="0" y="400" class="metric-label">GitHub Nodes:</tspan> <tspan class="value" dx="10">Followers: {{FOLLOWERS}} | Repos: {{REPOS}} | Stars: {{STARS}}</tspan>
    </text>
    
    <!-- Blinking Cursor -->
    <rect x="290" y="303" width="8" height="15" class="cursor" />
  </g>
</svg>
"""

    with open("dark_template.svg", "w", encoding="utf-8") as f:
        f.write(dark_template)
    print("Generated dark_template.svg")
        
    with open("light_template.svg", "w", encoding="utf-8") as f:
        f.write(light_template)
    print("Generated light_template.svg")

if __name__ == "__main__":
    make_templates()
