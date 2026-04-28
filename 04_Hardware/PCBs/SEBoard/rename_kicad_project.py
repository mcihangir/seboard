from pathlib import Path
import re

TARGET_DIR = Path(r"D:\Projects\SEBoard\04_Hardware\PCBs\SEBoard")

OLD_PROJECT_NAME = "SmartNFC"
NEW_PROJECT_NAME = "SEBoard"

ALLOWED_EXTENSIONS = {
    ".kicad_sch",
    ".kicad_pcb",
    ".kicad_pro",
}

total_replacements = 0
modified_files = 0
renamed_files = 0

if not TARGET_DIR.exists():
    raise FileNotFoundError(TARGET_DIR)

for file_path in TARGET_DIR.iterdir():

    if not file_path.is_file():
        continue

    if file_path.suffix not in ALLOWED_EXTENSIONS:
        continue

    text = file_path.read_text(encoding="utf-8")

    # SmartNFC: şeklindekilere dokunma
    pattern = rf'\b{re.escape(OLD_PROJECT_NAME)}\b(?!:)'

    new_text, count = re.subn(
        pattern,
        NEW_PROJECT_NAME,
        text
    )

    if count > 0:
        file_path.write_text(new_text, encoding="utf-8")
        modified_files += 1
        total_replacements += count
        print(f"Modified: {file_path.name} | {count}")

    else:
        print(f"No change: {file_path.name}")

    # Dosya adı değiştir
    if OLD_PROJECT_NAME in file_path.stem:
        new_name = file_path.name.replace(
            OLD_PROJECT_NAME,
            NEW_PROJECT_NAME
        )
        new_path = file_path.with_name(new_name)
        file_path.rename(new_path)

        renamed_files += 1
        print(f"Renamed: {file_path.name} -> {new_name}")

print("-" * 50)
print("Modified files :", modified_files)
print("Renamed files  :", renamed_files)
print("Total replacements:", total_replacements)