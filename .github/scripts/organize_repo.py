import os, glob, shutil, sys
from datetime import datetime

DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# Where to put what
RULES = {
    # Data
    "*.csv": "data/raw",
    "*.tsv": "data/raw",
    "*.xlsx": "data/raw",
    "*.xls": "data/raw",
    "*.parquet": "data/raw",
    "*.json": "data/raw",

    # Notebooks
    "*.ipynb": "notebooks",

    # Python source
    "*.py": "src",

    # SQL
    "*.sql": "sql",

    # Figures / images
    "*.png": "reports/figures",
    "*.jpg": "reports/figures",
    "*.jpeg": "reports/figures",
    "*.svg": "reports/figures",
    "*.gif": "reports/figures",
    "*.bmp": "reports/figures",

    # Docs / reports
    "*.pdf": "docs",
    "*.pptx": "docs",
    "*.ppt": "docs",
    "*.docx": "docs",
    "*.md": None,  # leave markdown where it is (README etc.)

    # BI
    "*.pbix": "reports",   # Power BI files
    "*.pbit": "reports",
}

IGNORE_DIRS = {
    ".git", ".github", "venv", ".venv", "__pycache__", ".mypy_cache",
    ".pytest_cache", ".idea", ".vscode", "env", "node_modules"
}

TARGET_ROOTS = {"data", "notebooks", "src", "reports", "sql", "docs"}

LOG_PATH = ".github/auto-structure-log.txt"

def log(line: str):
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def is_ignored(path: str) -> bool:
    parts = set(os.path.normpath(path).split(os.sep))
    return bool(parts & IGNORE_DIRS)

def is_already_sorted(path: str) -> bool:
    # file already inside one of our target roots
    parts = os.path.normpath(path).split(os.sep)
    return len(parts) > 0 and parts[0] in TARGET_ROOTS

def ensure_dirs():
    for d in ["data/raw", "data/processed", "notebooks", "src", "reports/figures", "sql", "docs", ".github"]:
        os.makedirs(d, exist_ok=True)

def safe_move(src: str, dst_dir: str):
    os.makedirs(dst_dir, exist_ok=True)
    base = os.path.basename(src)
    dst = os.path.join(dst_dir, base)

    # Avoid name collisions
    if os.path.exists(dst):
        name, ext = os.path.splitext(base)
        i = 1
        while os.path.exists(dst):
            dst = os.path.join(dst_dir, f"{name}_{i}{ext}")
            i += 1

    if DRY_RUN:
        log(f"[DRY RUN] MOVE {src}  ->  {dst}")
    else:
        shutil.move(src, dst)
        log(f"[MOVED]    {src}  ->  {dst}")

def main():
    ensure_dirs()
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n=== Auto-Structure run @ {datetime.utcnow().isoformat()}Z (DRY_RUN={DRY_RUN}) ===\n")

    moved_count = 0

    for pattern, target in RULES.items():
        log(f"\n🔎 Scanning for {pattern}")
        for path in glob.glob(f"**/{pattern}", recursive=True):
            # skip directories and non-files
            if os.path.isdir(path):
                continue

            # leave README/markdown where they are
            if pattern == "*.md":
                if os.path.basename(path).lower() == "readme.md":
                    log(f"⏭️  Keep README in place: {path}")
                    continue

            if is_ignored(path):
                log(f"⏭️  Ignored (tooling): {path}")
                continue

            if target is None:
                log(f"⏭️  No target for {path} (left in place)")
                continue

            # don't re-move files already in target roots
            if is_already_sorted(path):
                log(f"📂 Already sorted: {path}")
                continue

            safe_move(path, target)
            moved_count += 1

    if moved_count == 0:
        log("\nℹ️  No files needed moving this run.")
    else:
        log(f"\n✅ Done. Files moved: {moved_count}")

if __name__ == "__main__":
    main()
