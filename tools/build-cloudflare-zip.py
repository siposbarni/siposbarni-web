import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUT = DIST / "cloudflare-upload"
ZIP_BASE = DIST / "siposbarni-cloudflare-upload"


def text_value(value):
    if isinstance(value, dict):
        return value.get("hu") or value.get("en") or next(iter(value.values()), "")
    return str(value or "")


def slugify(value):
    text = text_value(value).lower()
    for source, target in {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ö": "o",
        "ő": "o",
        "ú": "u",
        "ü": "u",
        "ű": "u",
    }.items():
        text = text.replace(source, target)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "artwork"


def reset_output():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    zip_path = ZIP_BASE.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()


def copy_core_files():
    for name in ["index.html", "styles.css", "script.js", "content.json", "netlify.toml"]:
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, OUT / name)

    shutil.copytree(ROOT / "assets" / "artworks" / "thumbs", OUT / "assets" / "artworks" / "thumbs")


def optimize_about_image(content):
    about_source_dir = ROOT / "assets" / "about"
    if not about_source_dir.exists():
        return content

    about_target_dir = OUT / "assets" / "about"
    about_target_dir.mkdir(parents=True, exist_ok=True)

    for source in about_source_dir.iterdir():
        if not source.is_file():
            continue
        with Image.open(source) as image:
            image = ImageOps.exif_transpose(image).convert("RGB")
            image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
            image.save(about_target_dir / "about.jpg", "JPEG", quality=82, optimize=True, progressive=True)
        content.setdefault("about", {})["image"] = "assets/about/about.jpg"
        break

    return content


def optimize_artworks():
    data = json.loads((ROOT / "artworks.json").read_text(encoding="utf-8"))
    full_dir = OUT / "assets" / "artworks" / "full"
    full_dir.mkdir(parents=True, exist_ok=True)
    used = set()

    for section in data["categories"]:
        section_slug = slugify(section["title"])
        for item in section.get("works", []):
            source_path = ROOT / Path(item["image"])
            base = f"{section_slug}-{slugify(item.get('title') or source_path.stem)}"
            name = f"{base}.jpg"
            counter = 2
            while name in used:
                name = f"{base}-{counter}.jpg"
                counter += 1
            used.add(name)

            with Image.open(source_path) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                image.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
                image.save(full_dir / name, "JPEG", quality=76, optimize=True, progressive=True)
            item["image"] = f"assets/artworks/full/{name}"

    (OUT / "artworks.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_content():
    content = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
    content = optimize_about_image(content)
    (OUT / "content.json").write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    reset_output()
    copy_core_files()
    write_content()
    optimize_artworks()
    archive = shutil.make_archive(str(ZIP_BASE), "zip", OUT)
    print(archive)
    print(f"{Path(archive).stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
