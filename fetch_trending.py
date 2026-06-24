#!/usr/bin/env python3
"""Fetch GitHub trending repos (last 3 days) and update README + records."""

import requests, json, os
from datetime import datetime, timedelta

TOKEN = os.environ["GH_TOKEN"]
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}

# Query: repos created in last 3 days, sorted by stars
since = (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d")
url = f"https://api.github.com/search/repositories?q=created:>{since}&sort=stars&order=desc&per_page=10"

r = requests.get(url, headers=HEADERS)
data = r.json()

today = datetime.utcnow().strftime("%Y-%m-%d")
lines = [f"# GitHub Trending — {today}\n"]
lines.append(f"| # | Repo | Language | Stars | Description |")
lines.append(f"|---|------|----------|-------|-------------|")

for i, repo in enumerate(data.get("items", [])[:10], 1):
    name = repo["full_name"]
    lang = repo.get("language") or "—"
    stars = repo["stargazers_count"]
    desc = (repo.get("description") or "").replace("|", "/")[:80]
    lines.append(f"| {i} | [{name}](https://github.com/{name}) | {lang} | ⭐{stars} | {desc} |")

# Save record
os.makedirs("records", exist_ok=True)
with open(f"records/{today}.md", "w") as f:
    f.write("\n".join(lines))

# Update README
with open("README.md", "r") as f:
    readme = f.read()

header_end = readme.find("## Latest:")
record_section = readme.find("## Archive")
new_header = readme[:header_end] + f"## Latest: {today}\n\n" + "\n".join(lines[1:]) + "\n\n"

archive_start = readme.rfind("| Date")
new_archive = f"| [{today}](records/{today}.md) | {data['items'][0]['full_name']} | {data['items'][0]['stargazers_count']} |\n"
remaining = readme[readme.rfind("\n", archive_start)+1:] if readme.rfind("\n", archive_start) > 0 else ""

# Insert new archive entry
old_archive = readme[archive_start:]
new_archive_full = f"| Date | Top Repo | Stars Gained |\n|------|----------|-------------|\n{new_archive}" + "\n".join(old_archive.split("\n")[2:])

final = new_header + "## Archive\n\n" + new_archive_full

with open("README.md", "w") as f:
    f.write(final)

print(f"Updated for {today}")
