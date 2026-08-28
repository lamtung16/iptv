import csv
import re

def parse_id_list(s):
    if not s or s.strip() == "[]":
        return []
    return re.findall(r'\d+', s)

sources = {}
with open("secruoc.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sources[row["server_id"]] = row

m3u_lines = ['#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz"\n']

with open("slnennahc.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        group = row["group"]
        channel = row["channel"]
        tvg_id = row["tvg_id"]

        for source_name in reader.fieldnames[3:]:
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
                extinf = (f'#EXTINF:-1 tvg-id="{tvg_id}" group-title="{group}", {channel}')
                m3u_lines.append(extinf)
                m3u_lines.append(url)
                m3u_lines.append("")

# Write output file
with open("../tung_iptv.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(m3u_lines))