"""
ShortsMinter™ — Nav Update Script
Masondogg Studios, LLC

DROP this script in the same folder as your .html files.
RUN:  python update_nav.py

Updates the nav links in every .html file at once.
When you add a new page, just update NAV_LINKS below and run.
"""

import os
import re

# ══════════════════════════════════════════════════════════════════
# EDIT THIS SECTION WHEN YOU ADD OR CHANGE NAV LINKS
# Each entry: ("display text", "href", "cta True/False")
# cta=True makes it the gold "Get ShortsMinter →" style button
# ══════════════════════════════════════════════════════════════════
NAV_LINKS = [
    ("Home",              "index.html",                                      False),
    ("Founders",          "founders_beta.html",                              False),
    ("Support",           "support.html",                                    False),
    ("Guides",            "guides.html",                                     False),
    ("Terms",             "terms.html",                                      False),
    ("Get ShortsMinter →","https://masondoggs.gumroad.com/l/founding",       True),
]

# Files to update — add new pages here as you create them
HTML_FILES = [
    "index.html",
    "founders_beta.html",
    "support.html",
    "terms.html",
    "guides.html",
    "shortsminter_guide_v1_0b.html",
]

# ══════════════════════════════════════════════════════════════════
# DO NOT EDIT BELOW THIS LINE
# ══════════════════════════════════════════════════════════════════

def build_nav_links(active_file):
    """Build the nav links block for a given file (sets active class on current page)."""
    lines = []
    for label, href, is_cta in NAV_LINKS:
        is_active = (href == active_file)
        if is_cta:
            lines.append(
                f'    <a href="{href}" target="_blank" '
                f'style="color:var(--gold);font-weight:700">{label}</a>'
            )
        elif is_active:
            lines.append(f'    <a href="{href}" class="active">{label}</a>')
        else:
            lines.append(f'    <a href="{href}">{label}</a>')
    return "\n".join(lines)


def update_file(filepath):
    """Replace the nav links block in a single HTML file."""
    filename = os.path.basename(filepath)

    if not os.path.exists(filepath):
        print(f"  ⚠  SKIP  — file not found: {filename}")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Match everything inside <div class="nav-links">...</div>
    pattern = r'(<div class="nav-links">)(.*?)(</div>)'
    new_links = "\n" + build_nav_links(filename) + "\n  "

    new_content, count = re.subn(pattern, r'\1' + new_links + r'\3', content, flags=re.DOTALL)

    if count == 0:
        print(f"  ⚠  SKIP  — nav-links div not found in: {filename}")
        return False

    if new_content == content:
        print(f"  ✓  NO CHANGE  — already up to date: {filename}")
        return True

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  ✅  UPDATED  — {filename}")
    return True


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print()
    print("=" * 52)
    print("  ShortsMinter™ — Nav Update Script")
    print("  Masondogg Studios, LLC")
    print("=" * 52)
    print()

    updated = 0
    skipped = 0

    for filename in HTML_FILES:
        filepath = os.path.join(script_dir, filename)
        result = update_file(filepath)
        if result:
            updated += 1
        else:
            skipped += 1

    print()
    print(f"  Done — {updated} file(s) processed, {skipped} skipped.")
    print()
    input("  Press Enter to close...")


if __name__ == "__main__":
    main()
