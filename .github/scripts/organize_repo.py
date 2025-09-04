import os, glob, shutil

# Mapping of file types to folders
RULES = {
    "*.csv": "data/raw",
    "*.xlsx": "data/raw",
    "*.ipynb": "notebooks",
    "*.py": "src",
    "*.sql": "sql",
    "*.png": "reports/figures",
    "*.jpg": "reports/figures",
    "*.jpeg": "reports/figures",
    "*.pdf": "docs",
}

IGNORE = {".git", ".github"}

def safe_move(src, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)
    base = os.path.basename(src)
    dst = os.path.join(dst_dir, base)
    if os.path.exists(dst):
        print(f"Skip (exists): {dst}")
        return
    print(f"Move: {src} -> {dst}")
    shutil.move(src, dst)

for pattern, target in RULES.items():
    for file in glob.glob(f"**/{pattern}", recursive=True):
        if any(part in IGNORE for part in file.split(os.sep)):
            continue
        if os.path.isdir(file):
            continue
        if file.startswith(tuple(RULES.values())):
            continue
        safe_move(file, target)
