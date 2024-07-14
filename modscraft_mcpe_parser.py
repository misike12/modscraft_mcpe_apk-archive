import re
import os
import random
import sys
from datetime import datetime, timezone

import bs4
import requests

if len(sys.argv) != 2:
    print(f"Error: This program needs 1 argument, got {len(sys.argv) - 1}\n")
    print(f"Usage: {sys.argv[0]} <file-to-write-to>\n")
    print("Parses all MCPE releases from Modscraft and writes to specified Markdown file.")
    sys.exit(1)

def pathify(string):
    return re.sub(r'[^a-z0-9_.-]', '', string.replace(' ', '_').lower())

def create_md_table(data, width):
    table = f"{'| ' * width}|\n{'|-' * width}|\n"
    for i in range(0, len(data), width):
        table += "| " + " | ".join(data[i:i + width]) + " |\n"
    return table

user_agents = [
    "Mozilla/5.0 (Linux; Android 13; SM-M127G Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.134 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 11; Mobile; rv:128.0) Gecko/128.0 Firefox/128.0",
    "Mozilla/5.0 (Android 12; Mobile; RV:92.0) Gecko/92.0 Firefox/92.0",
    "Mozilla/5.0 (Linux; Android 10; Pixel 3 Build/QQ2A.200305.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 11; Mobile; RV:91.0) Gecko/91.0 Firefox/91.0",
    "Mozilla/5.0 (Linux; Android 9; Galaxy S9 Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.116 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 13; Mobile; RV:106.0) Gecko/106.0 Firefox/106.0",
    "Mozilla/5.0 (Linux; Android 8.0.0; Nexus 6P Build/OPR6.170623.013; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 12; Mobile; RV:98.0) Gecko/98.0 Firefox/98.0",
    "Mozilla/5.0 (Linux; Android 11; Galaxy A32 Build/RP1A.200720.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.152 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Galaxy S21 Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0.6092.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 10; Mobile; RV:102.0) Gecko/102.0 Firefox/102.0",
    "Mozilla/5.0 (Linux; Android 8.1.0; LG G6 Build/N2G48H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.101 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; OnePlus 9 Pro Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/115.0.5790.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 12; Mobile; RV:105.0) Gecko/105.0 Firefox/105.0",
    "Mozilla/5.0 (Linux; Android 11; Galaxy A50 Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.90 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 9; Mobile; RV:101.0) Gecko/101.0 Firefox/101.0",
    "Mozilla/5.0 (Linux; Android 10; Galaxy Note 10 Build/QQ2A.200305.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/84.0.4147.125 Mobile Safari/537.36"
]
user_agent = random.choice(user_agents)
print(f"* Parser has started")
print(f"= User agent for today is \"{user_agent}\"")
markdown_output = f"- :open_file_folder: Source available at [**ModsCraft.Net**](https://modscraft.net/en/mcpe/)"
markdown_output += f"\n- :clock2: Updated **every 12 hours** at `00:00 UTC` and `12:00 UTC`"
markdown_output += f"\n- :rocket: **Last update:** `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC`\n"
print("* Creating directory 'version'")
writedir = os.path.dirname(sys.argv[1])
os.makedirs(os.path.join(writedir, "version"), exist_ok=True)
print("* Getting releases")
resp = requests.get("https://modscraft.net/en/mcpe/", headers={"User-Agent": user_agent})
if not resp.ok:
    print(f"! ModsCraft returned {resp.status_code}")
    sys.exit(1)
soup = bs4.BeautifulSoup(resp.text, "html.parser")
releases = {i.text: i["href"] for i in soup.find("div", class_="versions-history").find_all("a")}
version_links = []
for title, release in releases.items():
    print(f"\n= Starting work on version {title}")
    ver = requests.get(release, headers={"User-Agent": user_agent})
    if not ver.ok:
        print(f"! ModsCraft returned {resp.status_code}")
        sys.exit(1)
    rel_soup = bs4.BeautifulSoup(ver.text, "html.parser")
    version_output = f"## Minecraft {title} APKs\n"
    version_output += "| Download | Size |\n"
    version_output += "|----------|------|\n"
    for download in rel_soup.find_all("a", class_="download-item"):
        print("* Adding file ", end='')
        down_req = requests.get(download["href"], headers={"User-Agent": user_agent})
        if not down_req.ok:
            print(f"! ModsCraft returned {resp.status_code}")
            sys.exit(1)
        apk = bs4.BeautifulSoup(down_req.text, "html.parser")
        download_id = re.search(r'id=(\d+)', download["href"]).group(1)
        down_spans = download.find_all("span")
        file_name = apk.find("p").text
        print(file_name)
        size = down_spans[2].text[1:-1]
        download_link = f"https://modscraft.net/en/downloads/{download_id}"
        version_output += f"| [:package: `{file_name}`]({download_link}) | :floppy_disk: {size} \n"
    print(f"= Finished work on version {title}")
    filename = f"mc{pathify(title)}.md"
    try:
        with open(os.path.join(writedir, "version", filename), "w") as f:
            f.write(version_output)
    except PermissionError:
        print("! Unable to access file, not enough permissions")
        sys.exit(1)
    except IOError as e:
        print(f"! I/O error while writing to file: {e}")
        sys.exit(1)
    print("= Adding to main file")
    version_links.append(f"**[:package: Minecraft {title}](version/{filename})**")
markdown_output += f"\n{create_md_table(version_links, 3)}"

print("\n= All done, writing to file")
try:
    with open(os.path.join(sys.argv[1]), "w") as f:
        f.write(markdown_output)
except PermissionError:
    print("! Unable to access file, not enough permissions")
    sys.exit(1)
except IOError as e:
    print(f"! I/O error while writing to file: {e}")
    sys.exit(1)
print(f"* Wrote to '{sys.argv[1]}' successfully")
