import os, glob, shutil, subprocess
from datetime import datetime

# --- config ----
TARGETS = {
    # data
    "*.csv": "data/raw",
    "*.tsv": "data/raw",
    "*.xlsx": "data/raw",
    "*.xls": "data/raw",
    "*.parquet": "data/raw",
    "*.json": "data/raw",
    # notebooks
    "*.ipynb": "notebooks",
    # code
    "*.py": "src",
    # sql
    "*.sql": "sql",
    # images
    "*.png": "reports/figures",
    "*.jpg": "reports/figures",
    "*.jpeg": "reports/figures",
    "*.svg": "reports/figures",
    "*.gif": "reports/figures",
    # docs
    "*.pdf": "docs",
    "*.pptx": "docs",
    "*.ppt": "docs",
    "*.docx": "docs",
    # BI
    "*.pbix": "reports",
    "*.pbit": "reports",
}
IGNORE_DIRS = {".git", ".github", "venv", ".venv", "__pycache__", ".mypy_cache",
               ".pytest_cache", ".idea", ".vscode", "env", "node_modules"}
TARGET_ROOTS = {"data", "notebooks", "src", "reports", "sql", "docs"}
LOG_PATH = ".github/auto-structure-log.txt"
# ---------------

def log(msg):
    print(msg)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def already_sorted(path):
    parts = os.path.normpath(path).split(os.sep)
    return parts and parts[0] in TARGET_ROOTS

def ignored(path):
    parts = set(os.path.normpath(path).split(os.sep))
    return bool(parts & IGNORE_DIRS)

def ensure_dirs():
    for d in ["data/raw", "data/processed", "notebooks", "src", "reports/figures", "sql", "docs"]:
        os.makedirs(d, exist_ok=True)

def git_mv(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    # If destination exists, make a unique name
    base, ext = os.path.splitext(os.path.basename(dst))
    final = dst
    i = 1
    while os.path.exists(final):
        final = os.path.join(os.path.dirname(dst), f"{base}_{i}{ext}")
        i += 1
    # try git mv (so renames show nicely in PR)
    try:
        subprocess.run(["git", "mv", src, final], check=True)
        log(f"✅ git mv: {src} -> {final}")
    except subprocess.CalledProcessError:
        shutil.move(src, final)
        log(f"✅ move:   {src} -> {final}")

def main():
    log("\n=== Auto-Structure DEBUG ===")
    log(f"CWD: {os.getcwd()}")
    ensure_dirs()

    # list root for sanity
    root_list = "\n".join(sorted(os.listdir(".")))
    log(f"\nRoot contents:\n{root_list}")

    moved = 0
    for pattern, dest in TARGETS.items():
        log(f"\n🔎 Pattern: {pattern}  ->  {dest}")
        matched = glob.glob(f"**/{pattern}", recursive=True)
        if not matched:
            log("  (no matches)")
            continue
        for path in sorted(matched):
            if os.path.isdir(path):
                continue
            if ignored(path):
                log(f"⏭️  Ignored (tooling): {path}")
                continue
            if already_sorted(path):
                log(f"📂 Already sorted: {path}")
                continue
            if os.path.basename(path).lower() == "readme.md":
                log(f"⏭️  Keep README in place: {path}")
                continue
            target = os.path.join(dest, os.path.basename(path))
            git_mv(path, target)
            moved += 1

    if moved == 0:
        log("\nℹ️  No files moved (either none matched or already organized).")
    else:
        log(f"\n✅ Done. Files moved: {moved}")

    # always append timestamp so the workflow can open a PR even if nothing moved
    log(f"Run complete @ {datetime.utcnow().isoformat()}Z")

if __name__ == "__main__":
    main()
