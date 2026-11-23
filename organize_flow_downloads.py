import os
import shutil
import glob
from datetime import datetime

PROJECT_DIR = r"D:\social media\resrise-studio"
DOWNLOADS_DIR = os.path.expanduser(r"~\Downloads")
DRAFT_MEDIA_DIR = os.path.join(PROJECT_DIR, "draft_media")

# Target subdirectories
ACCOUNTS = ["avanyamehra", "mairamehraofficial", "iamgagankumar", "resrise", "gagankumarrocks"]
for acc in ACCOUNTS:
    os.makedirs(os.path.join(DRAFT_MEDIA_DIR, acc), exist_ok=True)


def find_recent_downloads(minutes: int = 60) -> list:
    """Finds image files downloaded in the last X minutes."""
    valid_exts = (".jpg", ".jpeg", ".png", ".webp")
    now = datetime.now().timestamp()
    recent = []

    for fname in os.listdir(DOWNLOADS_DIR):
        if fname.lower().endswith(valid_exts):
            fpath = os.path.join(DOWNLOADS_DIR, fname)
            mtime = os.path.getmtime(fpath)
            if now - mtime <= (minutes * 60):
                recent.append((mtime, fpath))

    # Sort chronologically
    recent.sort(key=lambda x: x[0])
    return [x[1] for x in recent]


def inspect_status():
    print("=" * 60)
    print("DRAFT MEDIA DIRECTORY STATUS (Days 8-14 Pipeline)")
    print("=" * 60)
    for acc in ACCOUNTS:
        dir_path = os.path.join(DRAFT_MEDIA_DIR, acc)
        files = [f for f in os.listdir(dir_path) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
        d8_files = [f for f in files if any(f"day{d:02d}" in f for d in range(8, 15))]
        print(f"@{acc:18s} -> Total: {len(files):2d} files | Days 8-14 ready: {len(d8_files):2d}")
    print("=" * 60)


if __name__ == "__main__":
    inspect_status()
    recent = find_recent_downloads(60)
    print(f"\nFound {len(recent)} recent image downloads in {DOWNLOADS_DIR}.")
    if recent:
        print("Recent files found:")
        for r in recent[:10]:
            print(" -", os.path.basename(r))
