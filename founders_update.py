"""
ShortsMinter™ — Founders Update Script
Masondogg Studios, LLC

Pulls name submissions from Google Sheet → builds clean founders.json
Run this whenever you're ready to update the Founders page.

SETUP (one time):
1. Open your Google Form responses sheet
2. Click Share → change to "Anyone with link can view"
3. Copy the Sheet ID from the URL:
   https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
4. Paste it below as SHEET_ID

USAGE:
   python founders_update.py

OUTPUT:
   founders.json — ready to push via deploy.bat
"""

import csv, json, os, urllib.request
from datetime import datetime

# ══════════════════════════════════════════════════════════════════
# CONFIGURE THIS — paste your Google Sheet ID here
# Get it from the URL of your Form responses spreadsheet
# ══════════════════════════════════════════════════════════════════
SHEET_ID = "YOUR_GOOGLE_SHEET_ID_HERE"

# Max founders allowed — matches Gumroad limit
MAX_FOUNDERS = 100

# Output file — saves in same folder as this script
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "founders.json")

# ══════════════════════════════════════════════════════════════════
# Column names from your Google Form
# These match your form field labels exactly
# ══════════════════════════════════════════════════════════════════
COL_NAME      = "display_name"     # display name field
COL_KEY_HASH  = "key_hash"         # hashed license key
COL_TIER      = "tier"             # should always be "founding"
COL_TIMESTAMP = "timestamp"        # submission timestamp
COL_SECRET    = "secret"           # SM2026FOUNDERS

EXPECTED_SECRET = "SM2026FOUNDERS"

# ══════════════════════════════════════════════════════════════════
# DO NOT EDIT BELOW THIS LINE
# ══════════════════════════════════════════════════════════════════

def fetch_sheet_data(sheet_id):
    """Download Google Sheet as CSV."""
    url = (f"https://docs.google.com/spreadsheets/d/{sheet_id}"
           f"/export?format=csv&gid=0")
    print(f"  Fetching sheet data...")
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            content = r.read().decode("utf-8")
        return content
    except Exception as e:
        print(f"  ERROR fetching sheet: {e}")
        print(f"  Make sure the sheet is shared as 'Anyone with link can view'")
        return None


def parse_csv(content):
    """Parse CSV content into list of dicts."""
    rows = []
    reader = csv.DictReader(content.splitlines())
    for row in reader:
        # Normalize column names — strip whitespace, lowercase
        normalized = {k.strip().lower().replace(" ","_"): v.strip()
                      for k, v in row.items()}
        rows.append(normalized)
    return rows


def validate_row(row):
    """
    Validate a single row from the sheet.
    Returns True if row is legitimate.
    """
    # Must have correct secret
    secret = row.get(COL_SECRET, "")
    if secret != EXPECTED_SECRET:
        return False

    # Must be founding tier
    tier = row.get(COL_TIER, "")
    if tier != "founding":
        return False

    # Must have a key hash
    key_hash = row.get(COL_KEY_HASH, "")
    if not key_hash or len(key_hash) < 8:
        return False

    return True


def build_founders_json(rows):
    """
    Build clean founders.json from validated rows.
    - Deduplicates by key_hash (one entry per license)
    - Deduplicates by name (one entry per name)
    - Named entries show name
    - Anonymous entries increment counter but show no name
    - Sorts by submission timestamp
    """
    seen_key_hashes = set()
    seen_names      = set()
    founders        = []
    skipped         = 0

    for row in rows:
        if not validate_row(row):
            skipped += 1
            continue

        key_hash = row.get(COL_KEY_HASH, "").strip()
        name     = row.get(COL_NAME,     "").strip()
        ts       = row.get(COL_TIMESTAMP, "")

        # Deduplicate by key_hash — one entry per license key
        if key_hash in seen_key_hashes:
            continue
        seen_key_hashes.add(key_hash)

        # Parse date for display
        try:
            dt = datetime.fromisoformat(ts)
            date_str = dt.strftime("%Y-%m-%d")
        except:
            date_str = datetime.now().strftime("%Y-%m-%d")

        # Deduplicate by name — one entry per display name
        # Anonymous entries (empty name) are never deduped
        if name:
            name_lower = name.lower().strip()
            if name_lower in seen_names:
                # Same name submitted twice — count once only
                continue
            seen_names.add(name_lower)

        founders.append({
            "name": name,       # empty string = anonymous
            "date": date_str,
        })

    # Sort by date submitted
    founders.sort(key=lambda x: x["date"])

    return founders, skipped


def save_json(founders):
    """Save founders.json to disk."""
    total   = len(founders)
    named   = sum(1 for f in founders if f.get("name"))
    anon    = total - named

    data = {
        "total":         total,
        "max_founders":  MAX_FOUNDERS,
        "last_updated":  datetime.now().strftime("%Y-%m-%d"),
        "founders":      founders,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return total, named, anon


def main():
    print()
    print("=" * 52)
    print("  ShortsMinter™ — Founders Update Script")
    print("  Masondogg Studios, LLC")
    print("=" * 52)
    print()

    # Check Sheet ID is configured
    if SHEET_ID == "YOUR_GOOGLE_SHEET_ID_HERE":
        print("  ERROR: SHEET_ID not configured.")
        print("  Open this script and paste your Google Sheet ID.")
        print()
        input("  Press Enter to close...")
        return

    # Fetch data
    content = fetch_sheet_data(SHEET_ID)
    if not content:
        print()
        input("  Press Enter to close...")
        return

    # Parse
    rows = parse_csv(content)
    print(f"  Found {len(rows)} total form submission(s)")

    # Build
    founders, skipped = build_founders_json(rows)
    print(f"  Skipped {skipped} invalid/test submission(s)")
    print()

    if not founders:
        print("  No valid founders found yet.")
        print("  founders.json will show 0 of 100.")

    # Preview
    print("  PREVIEW — founders to be written:")
    print("  " + "-" * 40)
    for i, f in enumerate(founders):
        name_display = f['name'] if f['name'] else "(anonymous)"
        print(f"  #{i+1:03d}  {name_display}  [{f['date']}]")
    print("  " + "-" * 40)
    print()

    # Confirm
    confirm = input(
        f"  Write founders.json with {len(founders)} "
        f"entry/entries? (Y/N): "
    )
    if confirm.strip().upper() != "Y":
        print()
        print("  Cancelled — nothing written.")
        print()
        input("  Press Enter to close...")
        return

    # Save
    total, named, anon = save_json(founders)

    print()
    print("=" * 52)
    print(f"  SUCCESS — founders.json written!")
    print("=" * 52)
    print()
    print(f"  Total founders : {total} of {MAX_FOUNDERS}")
    print(f"  Named          : {named}")
    print(f"  Anonymous      : {anon}")
    print(f"  File           : {OUTPUT_FILE}")
    print()
    print("  Next step: run deploy.bat to push to GitHub.")
    print("  Site updates in 1-2 minutes.")
    print()
    input("  Press Enter to close...")


if __name__ == "__main__":
    main()
