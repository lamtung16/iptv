import pandas as pd
import requests
from datetime import datetime, UTC
from urllib.parse import quote

INPUT_FILE = "output.csv"
OUTPUT_FILE = "output.csv"

HEADERS = {
    "User-Agent": "Tivimate 5.1.6"
}

# ---------------- HELPERS ----------------
def to_datetime_str(ts):
    """Convert unix timestamp to readable string."""
    try:
        if not ts or ts in ["0", 0]:
            return "NA"
        return datetime.fromtimestamp(int(ts), UTC).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "NA"


# ---------------- CORE ----------------

def process_row(row):
    host = str(row["host"]).rstrip("/")
    username = row["username"]
    password = row["password"]

    base_api = f"{host}/player_api.php?username={quote(username)}&password={quote(password)}"

    session = requests.Session()
    session.headers.update(HEADERS)

    # Default result (ensures row is always returned)
    result = row.copy()
    result.update({
        "status": "invalid",
        "created_at": "NA",
        "exp_date": "NA",
        "active_cons": "NA",
        "max_connections": "NA"
    })

    try:
        response = session.get(base_api, timeout=2)
        data = response.json()

        user = data.get("user_info", {})
        status = user.get("status")

        # If no status → keep defaults
        if not status:
            return result

        result["status"] = status
        result["created_at"] = to_datetime_str(user.get("created_at"))
        result["exp_date"] = to_datetime_str(user.get("exp_date"))
        result["active_cons"] = user.get("active_cons") or "NA"
        result["max_connections"] = user.get("max_connections") or "NA"
        return result
    except:
        return result


# ---------------- MAIN ----------------

def main():
    df = pd.read_csv(INPUT_FILE, dtype=str)

    # Optional: keep duplicates if you want strict 1:1 row mapping
    df = df.drop_duplicates(subset=["host", "username", "password"])

    results = []

    for _, row in df.iterrows():
        processed = process_row(row)
        results.append(processed)  # always append

    out_df = pd.DataFrame(results)

    # --- CLEAN TYPES ---
    out_df["active_cons"] = pd.to_numeric(out_df["active_cons"], errors="coerce")
    out_df["max_connections"] = pd.to_numeric(out_df["max_connections"], errors="coerce")
    out_df["created_at"] = pd.to_datetime(out_df["created_at"], errors="coerce")
    out_df["exp_date"] = pd.to_datetime(out_df["exp_date"], errors="coerce")

    # --- SORT ---
    out_df = out_df.sort_values(
        by=["host", "active_cons", "max_connections", "created_at", "exp_date"],
        ascending=[True, True, False, True, False]
    )

    # Convert back to string
    out_df["created_at"] = out_df["created_at"].astype(str)
    out_df["exp_date"] = out_df["exp_date"].astype(str)

    # --- SAVE ---
    out_df.to_csv(OUTPUT_FILE, index=False)

    print("Done.")


if __name__ == "__main__":
    main()