from pathlib import Path
import re

LIB_PATH = Path("000MCLib.kicad_sym")

TARGET_SYMBOL = "SE250B4"
TARGET_UNIT_NAME = "Power"

text = LIB_PATH.read_text(encoding="utf-8")


def find_block(txt, start_idx):
    depth = 0
    for i in range(start_idx, len(txt)):
        if txt[i] == "(":
            depth += 1
        elif txt[i] == ")":
            depth -= 1
            if depth == 0:
                return start_idx, i + 1
    raise RuntimeError("Block end not found")


def repl_slice(s, a, b, r):
    return s[:a] + r + s[b:]


# --------------------------------------------------
# Ana sembolü bul
# --------------------------------------------------
root_pat = f'(symbol "{TARGET_SYMBOL}"'
root_start = text.find(root_pat)

if root_start < 0:
    raise RuntimeError("SE250B4 bulunamadı")

root_s, root_e = find_block(text, root_start)
root_block = text[root_s:root_e]


# --------------------------------------------------
# Power unit bul
# --------------------------------------------------
target = None

for m in re.finditer(r'\(symbol\s+"SE250B4_[^"]+"', root_block):
    cs, ce = find_block(root_block, m.start())
    blk = root_block[cs:ce]

    if '(unit_name "Power")' in blk:
        target = (cs, ce, blk)
        break

if target is None:
    raise RuntimeError("Power unit bulunamadı")

cs, ce, unit_block = target


# --------------------------------------------------
# GND_* pinlerini işle
# --------------------------------------------------
new_unit = unit_block
offset = 0

count_hide = 0
count_passive = 0
count_total = 0

for m in re.finditer(r'\(pin\s+\S+', unit_block):
    ps, pe = find_block(unit_block, m.start())
    pin = unit_block[ps:pe]

    nm = re.search(r'\(name\s+"([^"]+)"', pin)
    if not nm:
        continue

    pin_name = nm.group(1)

    if not pin_name.startswith("GND_"):
        continue

    count_total += 1
    new_pin = pin

    # passive yap
    if not new_pin.startswith("(pin passive"):
        new_pin = re.sub(r'^\(pin\s+\S+', '(pin passive', new_pin, count=1)
        count_passive += 1

    # hide yes ekle
    if "(hide yes)" not in new_pin:
        lm = re.search(r'\(length\s+[-0-9.]+\)', new_pin)

        if lm:
            pos = lm.end()
            new_pin = new_pin[:pos] + '\n        (hide yes)' + new_pin[pos:]
        else:
            new_pin = new_pin.replace("\n", "\n        (hide yes)\n", 1)

        count_hide += 1

    aps = ps + offset
    ape = pe + offset

    new_unit = repl_slice(new_unit, aps, ape, new_pin)
    offset += len(new_pin) - len(pin)


# --------------------------------------------------
# Dosyaya yaz
# --------------------------------------------------
new_root = repl_slice(root_block, cs, ce, new_unit)
new_text = repl_slice(text, root_s, root_e, new_root)

LIB_PATH.write_text(new_text, encoding="utf-8")


# --------------------------------------------------
# Sonuç
# --------------------------------------------------
print("Tamamlandı.")
print("İşlenen toplam GND_* pin:", count_total)
print("Hide yapılan pin sayısı:", count_hide)
print("Passive yapılan pin sayısı:", count_passive)
print("Dosya güncellendi: 000MCLib.kicad_sym")