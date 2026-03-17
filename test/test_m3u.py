# %%
import requests
import csv
import time

M3U_FILE = "../tung_iptv.m3u"
OUTPUT_FILE = "channel_status.csv"

HEADERS = {
    "User-Agent": "TiviMate/5.2.0 (Linux; Android 10)"
}

def parse_m3u(file_path):
    channels = []
    name = None
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#EXTINF"):
                name = line.split(",")[-1]
            elif line.startswith("http"):
                channels.append({
                    "name": name,
                    "url": line
                })
    return channels

def check_stream_performance(url):
    try:
        # Measure full connection + first byte
        start_time = time.perf_counter()
        r = requests.get(url, headers=HEADERS, timeout=3, stream=True)
        first_byte_time = time.perf_counter()
        response_ms = (first_byte_time - start_time) * 1000

        # Measure stream load for 1 second
        total_bytes = 0
        stream_start = time.perf_counter()
        for chunk in r.iter_content(chunk_size=1024*64):  # 64 KB chunks
            total_bytes += len(chunk)
            if time.perf_counter() - stream_start >= 1:
                break
        stream_elapsed = time.perf_counter() - stream_start
        load_mbps = (total_bytes / 1024 / 1024) / stream_elapsed  # MB/s

        if r.status_code == 200:
            return "ONLINE", f"{response_ms:.2f}ms", f"{load_mbps:.2f}MB/s"
        else:
            return f"HTTP {r.status_code}", "N/A", "N/A"
    except Exception:
        return "OFFLINE", "N/A", "N/A"


channels = parse_m3u(M3U_FILE)
rows = []

for ch in channels:
    status, response, load = check_stream_performance(ch["url"])
    rows.append([
        ch["name"],
        ch["url"],
        status,
        response,
        load
    ])

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Channel Name", "URL", "Status", "Response", "Load (MB/s)"])
    writer.writerows(rows)

print("Done. Results saved to:", OUTPUT_FILE)