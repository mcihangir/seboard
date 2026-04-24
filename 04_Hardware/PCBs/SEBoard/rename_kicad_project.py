from pathlib import Path

TARGET_DIR = Path(r"D:\Projects\SEBoard\04_Hardware\PCBs\SEBoard")

OLD_TEXT = "SmartNFC"
NEW_TEXT = "SEBoard"

ALLOWED_EXTENSIONS = {
    ".kicad_sch",
    ".kicad_pcb",
    ".kicad_pro",
}

total_replacements = 0
modified_files = 0
renamed_files = 0

if not TARGET_DIR.exists():
    raise FileNotFoundError(f"Target folder not found: {TARGET_DIR}")

if not TARGET_DIR.is_dir():
    raise NotADirectoryError(f"Target path is not a folder: {TARGET_DIR}")

for file_path in TARGET_DIR.iterdir():
    # Do not enter subfolders
    if not file_path.is_file():
        continue

    if file_path.suffix not in ALLOWED_EXTENSIONS:
        continue

    text = file_path.read_text(encoding="utf-8")

    count = text.count(OLD_TEXT)

    if count == 0:
        print(f"No change: {file_path.name}")
    else:
        new_text = text.replace(OLD_TEXT, NEW_TEXT)
        file_path.write_text(new_text, encoding="utf-8")

        total_replacements += count
        modified_files += 1

        print(f"Modified: {file_path.name} | Replacements: {count}")

    # Rename file if OLD_TEXT exists in filename
    if OLD_TEXT in file_path.stem:
        new_name = file_path.name.replace(OLD_TEXT, NEW_TEXT)
        new_path = file_path.with_name(new_name)

        file_path.rename(new_path)
        renamed_files += 1

        print(f"Renamed : {file_path.name} -> {new_name}")

print("-" * 50)
print(f"Modified files : {modified_files}")
print(f"Renamed files  : {renamed_files}")
print(f"Total replacements: {total_replacements}")