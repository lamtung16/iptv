import csv

# host = "http://v3tv.live:80"
# mac = "00:1A:79:C2:01:8B"
host = "http://line.smootvone.vip"
mac = "00:1A:79:AB:E8:8C"

# Prepare output
m3u_lines = ['#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz"\n']

# Read channels.csv
with open("channels.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        group = row["group"]
        channel = row["channel"]
        tvg_id = row["tvg_id"]
        id = row["id"]
        logo = f'https://raw.githubusercontent.com/lamtung16/iptv/refs/heads/main/logos/{channel.lower().replace(" ", "-")}.png'
        extinf = (f'#EXTINF:-1 tvg-id="{tvg_id}" group-title="{group}" tvg-logo="{logo}", {channel}')
        m3u_lines.append(extinf)
        m3u_lines.append(f"{host}/play/live.php?mac={mac}&stream={id}&extension=m3u8")
        m3u_lines.append("")

# Write output file
with open("stbemu_iptv.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(m3u_lines))