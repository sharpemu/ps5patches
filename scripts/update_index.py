"""Build the title-ID/version index consumed by SharpEmu's patch downloader."""

import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def build_index(root: Path) -> dict:
    files = []
    names = set()
    for path in sorted((root / "prospero_patches").iterdir()):
        if not path.is_file() or path.suffix.lower() != ".xml":
            continue
        if not re.fullmatch(r"[A-Za-z0-9._ -]+\.xml", path.name, re.IGNORECASE):
            raise ValueError(f"Unsafe patch filename: {path.name}")
        if path.name.casefold() in names:
            raise ValueError(f"Duplicate patch filename: {path.name}")
        names.add(path.name.casefold())
        patch = ET.parse(path).getroot()
        if patch.tag != "Patch":
            raise ValueError(f"Invalid XML root: {path.name}")
        title_ids = sorted({(node.text or "").strip().upper() for node in patch.findall("TitleID/ID")})
        versions = sorted({node.get("AppVer", "") for node in patch.findall("Metadata")})
        if not title_ids or any(not re.fullmatch(r"PPSA[0-9]{5}", title_id) for title_id in title_ids):
            raise ValueError(f"Missing or invalid title IDs: {path.name}")
        if not versions or any(version.casefold() != "mask" and not re.fullmatch(r"[0-9]+(?:\.[0-9]+){1,3}", version) for version in versions):
            raise ValueError(f"Missing or invalid game versions: {path.name}")
        files.append({"file": path.name, "titleIds": title_ids, "versions": versions})
    return {"formatVersion": 1, "files": files}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if patches.json needs updating.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    output = root / "patches.json"
    text = json.dumps(build_index(root), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != text:
            raise SystemExit("patches.json is out of date; run python scripts/update_index.py")
        print("patches.json matches the XML title IDs and versions.")
    else:
        output.write_text(text, encoding="utf-8", newline="\n")
        print("Updated patches.json")


if __name__ == "__main__":
    main()
