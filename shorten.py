import os

# Define the exact channel names you want to keep (case-insensitive)
TARGET_CHANNELS = {
    "tennis channel",
    "sky sports tennis",
    "sky sports main event",
    "sky sports premier league",
    "usa network",
    "sky sports plus",
    "tnt sports 1",
    "tnt sports 2",
    "tnt sports 3",
    "tnt sports 4"
}

def filter_m3u(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found in the current directory.")
        return

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    new_lines = []
    
    # Keep the #EXTM3U header if present
    if lines and lines[0].startswith("#EXTM3U"):
        new_lines.append(lines[0])
        start_idx = 1
    else:
        start_idx = 0

    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith("#EXTINF"):
            # Channel name is typically after the last comma in the #EXTINF line
            parts = line.split(",", 1)
            channel_name = parts[1].strip() if len(parts) > 1 else ""
            
            # Check if channel name matches any of our targets
            is_match = any(target in channel_name.lower() for target in TARGET_CHANNELS)
            
            # Collect the metadata line and the stream URL line that follows it
            if is_match:
                new_lines.append(lines[i]) # #EXTINF line
                if i + 1 < len(lines) and not lines[i+1].startswith("#"):
                    new_lines.append(lines[i+1]) # URL line
                    i += 2
                else:
                    i += 1
            else:
                # Skip this channel and its stream URL
                i += 1
                while i < len(lines) and not lines[i].startswith("#EXTINF") and not lines[i].startswith("#EXTM3U"):
                    i += 1
        else:
            i += 1

    # Overwrite the original file with the filtered content
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    
    print(f"Successfully filtered '{file_path}'. Playlist is now shorter!")

if __name__ == "__main__":
    filter_m3u("tung_iptv.m3u")