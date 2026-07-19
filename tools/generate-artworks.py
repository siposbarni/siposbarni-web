import json
import re
import unicodedata
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ARTWORKS_DIR = ROOT / "assets" / "artworks"
THUMBS_DIR = ARTWORKS_DIR / "thumbs"
OUT = ROOT / "artworks.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def localized(value):
    return {"hu": value, "en": value}


def slugify(value):
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-") or "artwork"


def read_text(path):
    for encoding in ("utf-8-sig", "utf-8", "cp1250"):
        try:
            return path.read_text(encoding=encoding).strip()
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="ignore").strip()


def relative_path(path):
    return path.relative_to(ROOT).as_posix()


def unique_id(base, used):
    candidate = base
    counter = 2
    while candidate in used:
        candidate = f"{base}-{counter}"
        counter += 1
    used.add(candidate)
    return candidate


def parse_artwork_name(path):
    stem = path.stem.strip()
    year = ""

    year_match = re.search(r"(?:^|[\s,(-])((?:19|20)\d{2})(?:$|[\s,)-])", stem)
    if year_match:
        year = year_match.group(1)
        stem = (stem[: year_match.start(1)] + stem[year_match.end(1) :]).strip(" ,-()")

    size = ""
    size_match = re.search(r"(\d{2,3}\s*[xX]\s*\d{2,3}\s*cm?)", stem)
    if size_match:
        size = re.sub(r"\s+", "", size_match.group(1)).replace("X", "x")
        before_size = stem[: size_match.start()].strip(" ,-")
        after_size = stem[size_match.end() :].strip(" ,-")
        stem_without_size = (stem[: size_match.start()] + stem[size_match.end() :]).strip(" ,-")
    else:
        before_size = ""
        after_size = ""
        stem_without_size = stem

    title = stem_without_size
    medium = ""
    delimiter_match = re.search(r"\s+-\s+|\s+-|-\s+", stem_without_size)
    if delimiter_match:
        title = stem_without_size[: delimiter_match.start()].strip(" ,-")
        medium = stem_without_size[delimiter_match.end() :].strip(" ,-")
    elif "," in stem_without_size:
        title, medium = [part.strip(" ,-") for part in stem_without_size.split(",", 1)]
    elif size and before_size and after_size:
        title = before_size
        medium = after_size

    return {
        "title": title or stem,
        "year": year,
        "medium": medium,
        "size": size,
    }


def build_thumb(source, category_slug, artwork_slug):
    target_dir = THUMBS_DIR / category_slug
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{artwork_slug}.jpg"

    if target.exists() and target.stat().st_mtime >= source.stat().st_mtime:
        return target

    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((700, 700), Image.Resampling.LANCZOS)
        image.save(target, "JPEG", quality=78, optimize=True, progressive=True)

    return target


def generate():
    categories = []
    used_ids = set()

    if not ARTWORKS_DIR.exists():
        raise FileNotFoundError(f"Missing artworks folder: {ARTWORKS_DIR}")

    for folder in sorted(ARTWORKS_DIR.iterdir(), key=lambda item: item.name.lower()):
        if not folder.is_dir() or folder.name == "thumbs":
            continue

        category_slug = slugify(folder.name)
        txt_files = sorted(folder.glob("*.txt"), key=lambda item: item.name.lower())
        description = read_text(txt_files[0]) if txt_files else ""
        works = []

        image_files = [
            path
            for path in sorted(folder.iterdir(), key=lambda item: item.name.lower())
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        ]

        for image_path in image_files:
            parsed = parse_artwork_name(image_path)
            artwork_slug = slugify(f"{parsed['title']} {parsed['medium']} {parsed['size']}")
            item_id = unique_id(f"{category_slug}-{artwork_slug}", used_ids)
            thumb = build_thumb(image_path, category_slug, artwork_slug)

            works.append(
                {
                    "id": item_id,
                    "title": localized(parsed["title"]),
                    "year": parsed["year"],
                    "medium": localized(parsed["medium"]),
                    "size": parsed["size"],
                    "description": localized(description),
                    "image": relative_path(image_path),
                    "thumb": relative_path(thumb),
                }
            )

        categories.append(
            {
                "id": category_slug,
                "title": localized(folder.name),
                "description": localized(description),
                "works": works,
            }
        )

    OUT.write_text(json.dumps({"categories": categories}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return OUT


def main():
    output = generate()
    total = sum(len(category["works"]) for category in json.loads(output.read_text(encoding="utf-8"))["categories"])
    print(f"Generated {output} with {total} artworks")


if __name__ == "__main__":
    main()
