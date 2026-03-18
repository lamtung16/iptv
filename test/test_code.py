import pandas as pd
import requests
from datetime import datetime, UTC
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_FILE = "test.csv"
OUTPUT_FILE = "test.csv"
MAX_WORKERS = 20

HEADERS = {
    "User-Agent": "Tivimate 5.1.6"
}

ADULT_KEYWORDS = ["adult", "xxx", "porn", "18+", "sex"]


def unix_to_date(ts):
    try:
        if ts in [None, "", 0, "0"]:
            return "NA"
        return datetime.fromtimestamp(int(ts), UTC).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "NA"


def has_adult_category(categories):
    try:
        for c in categories:
            name = str(c.get("category_name", "")).lower()
            if any(k in name for k in ADULT_KEYWORDS):
                return True
    except:
        pass
    return False


def process_row(row):
    host = str(row["host"]).rstrip("/")
    username = row["username"]
    password = row["password"]

    base_api = f"{host}/player_api.php?username={quote(username)}&password={quote(password)}"

    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        # 🔥 FAST FAIL: main API
        r = session.get(base_api, timeout=(1.5, 2))
        data = r.json()

        user_info = data.get("user_info", {})
        status = user_info.get("status")

        # ❌ skip disabled or invalid
        if not status or status.lower() == "disabled":
            return None

        created_at = unix_to_date(user_info.get("created_at"))
        exp_date = unix_to_date(user_info.get("exp_date"))
        active_cons = user_info.get("active_cons")
        max_connections = user_info.get("max_connections")

        # ⚡ OPTIONAL: skip heavy calls if already expired
        if exp_date != "NA" and "1970" not in exp_date:
            if pd.to_datetime(exp_date, errors="coerce") < pd.Timestamp.utcnow():
                return None

        # ---------------- LIGHT CHECK ONLY ----------------
        # Only count lengths quickly, no retries

        def safe_count(url):
            try:
                r = session.get(url, timeout=(1.5, 2))
                return len(r.json())
            except:
                return "NA"

        movies_count = safe_count(f"{base_api}&action=get_vod_streams")
        shows_count = safe_count(f"{base_api}&action=get_series")
        channels_count = safe_count(f"{base_api}&action=get_live_streams")

        # ---------------- ADULT CHECK (FAST) ----------------
        has_adult = False
        try:
            live_cat = session.get(f"{base_api}&action=get_live_categories", timeout=(1, 2)).json()
            if has_adult_category(live_cat):
                has_adult = True
            else:
                vod_cat = session.get(f"{base_api}&action=get_vod_categories", timeout=(1, 2)).json()
                if has_adult_category(vod_cat):
                    has_adult = True
        except:
            pass

        row["status"] = status
        row["created_at"] = created_at
        row["exp_date"] = exp_date
        row["active_cons"] = active_cons or "NA"
        row["max_connections"] = max_connections or "NA"
        row["movies_count"] = movies_count
        row["shows_count"] = shows_count
        row["channels_count"] = channels_count
        row["has_adult"] = has_adult

        return row

    except:
        return None


# ---------------- MAIN ----------------

df = pd.read_csv(INPUT_FILE, dtype=str)
df = df.drop_duplicates(subset=["host", "username", "password"])

rows = []

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(process_row, row.copy()) for _, row in df.iterrows()]

    for future in as_completed(futures):
        result = future.result()
        if result is not None:
            rows.append(result)


# ---------------- SAVE ----------------

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

out_df.to_csv(OUTPUT_FILE, index=False)

print("Done.")