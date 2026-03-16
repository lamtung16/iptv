# %%
import pandas as pd
import requests
from datetime import datetime, UTC
from urllib.parse import quote

# %%
INPUT_FILE = "test.csv"

# %%
def unix_to_date(ts):
    try:
        if ts in [None, "", 0, "0"]:
            return "NA"
        return datetime.fromtimestamp(int(ts), UTC).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "NA"

# %%
headers = {
    "User-Agent": "Tivimate 5.1.6"
}

ADULT_KEYWORDS = ["adult", "xxx", "porn", "18+", "sex"]

def has_adult_category(categories):
    try:
        for c in categories:
            name = str(c.get("category_name", "")).lower()
            if any(k in name for k in ADULT_KEYWORDS):
                return True
    except:
        pass
    return False


df = pd.read_csv(INPUT_FILE, dtype=str)

df = df.drop_duplicates(subset=["host", "username", "password"])

rows = []

for _, row in df.iterrows():

    host = str(row["host"]).rstrip("/")
    username = row["username"]
    password = row["password"]

    try:

        base_api = f"{host}/player_api.php?username={quote(username)}&password={quote(password)}"

        r = requests.get(base_api, headers=headers, timeout=3)
        data = r.json()

        user_info = data.get("user_info", {})
        status = user_info.get("status")

        if status and status.lower() == "disabled":
            continue

        created_at = unix_to_date(user_info.get("created_at"))
        exp_date = unix_to_date(user_info.get("exp_date"))
        active_cons = user_info.get("active_cons")
        max_connections = user_info.get("max_connections")

        # ---------------- MOVIES ----------------
        try:
            vod_r = requests.get(f"{base_api}&action=get_vod_streams", headers=headers, timeout=5)
            movies_count = len(vod_r.json())
        except:
            movies_count = "NA"

        # ---------------- SERIES ----------------
        try:
            series_r = requests.get(f"{base_api}&action=get_series", headers=headers, timeout=5)
            shows_count = len(series_r.json())
        except:
            shows_count = "NA"

        # ---------------- CHANNELS ----------------
        try:
            live_r = requests.get(f"{base_api}&action=get_live_streams", headers=headers, timeout=5)
            channels_count = len(live_r.json())
        except:
            channels_count = "NA"

        # ---------------- ADULT CHECK ----------------
        has_adult = False
        try:
            live_cat = requests.get(f"{base_api}&action=get_live_categories", headers=headers, timeout=5).json()
            vod_cat = requests.get(f"{base_api}&action=get_vod_categories", headers=headers, timeout=5).json()
            series_cat = requests.get(f"{base_api}&action=get_series_categories", headers=headers, timeout=5).json()

            if (
                has_adult_category(live_cat)
                or has_adult_category(vod_cat)
                or has_adult_category(series_cat)
            ):
                has_adult = True
        except:
            pass

        row["status"] = status or "NA"
        row["created_at"] = created_at
        row["exp_date"] = exp_date
        row["active_cons"] = active_cons or "NA"
        row["max_connections"] = max_connections or "NA"
        row["movies_count"] = movies_count
        row["shows_count"] = shows_count
        row["channels_count"] = channels_count
        row["has_adult"] = has_adult

        rows.append(row)

    except:
        continue

# %%
out_df = pd.DataFrame(rows)

out_df["active_cons"] = pd.to_numeric(out_df["active_cons"], errors="coerce")
out_df["max_connections"] = pd.to_numeric(out_df["max_connections"], errors="coerce")
out_df["created_at"] = pd.to_datetime(out_df["created_at"], errors="coerce")
out_df["exp_date"] = pd.to_datetime(out_df["exp_date"], errors="coerce")

out_df = out_df.sort_values(
    by=["host", "active_cons", "max_connections", "created_at", "exp_date"],
    ascending=[True, True, False, True, False]
)

out_df["created_at"] = out_df["created_at"].astype(str)
out_df["exp_date"] = out_df["exp_date"].astype(str)

out_df.to_csv(INPUT_FILE, index=False)