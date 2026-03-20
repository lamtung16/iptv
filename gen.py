import csv
import re

def parse_id_list(s):
    if not s or s.strip() == "[]":
        return []
    return re.findall(r'\d+', s)

# Load sources.csv into dict keyed by server_id
sources = {}
with open("sources.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sources[row["server_id"]] = row

# Prepare output
m3u_lines = ["#EXTM3U"]

# Read channels.csv
with open("channels.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        group = row["group"]
        channel = row["channel"]

        for source_name in reader.fieldnames[2:]:
            ids = parse_id_list(row[source_name])
            if not ids:
                continue
            
            src = sources[source_name]
            host = src["host"]
            username = src["username"]
            password = src["password"]
            url_format = src["url_format"]
            
            for cid in ids:
                url = url_format.format(host=host, username=username, password=password,channel_id=cid)                
                logo = f'https://raw.githubusercontent.com/lamtung16/iptv/refs/heads/main/logos/{channel.lower().replace(" ", "-")}.png'
                extinf = (f'#EXTINF:-1 group-title="{group}" tvg-logo="{logo}", {channel} ({source_name[0]})')
                m3u_lines.append(extinf)
                m3u_lines.append(url)
                m3u_lines.append("")

# Write output file
with open("full.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(m3u_lines))