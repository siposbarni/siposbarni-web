import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_site_contract():
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    assert 'data-netlify="true"' in index
    assert 'name="contact"' in index
    assert 'data-lang-option="hu"' not in index
    assert 'data-lang-option="en"' not in index
    assert 'id="gallery-list"' in index
    assert 'id="lightbox"' in index
    assert 'id="artwork-field"' not in index
    assert 'id="tiktok-link"' in index
    assert 'id="email-link"' not in index

    content = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
    assert content["defaultLanguage"] == "hu"
    assert set(content["languages"]) == {"hu", "en"}
    assert content["contact"]["email"]
    assert content["links"]["tiktok"]
    assert "artwork" not in content["contact"]
    assert content["about"]["body"]["hu"]
    assert (ROOT / content["about"]["image"]).exists()

    script = (ROOT / "script.js").read_text(encoding="utf-8")
    assert 'lang: "hu"' in script
    assert "localStorage" not in script
    assert "data-lang-option" not in script
    assert "artwork-field" not in script
    assert "tiktok-link" in script
    assert "email-link" not in script
    assert "message-field" in script

    artworks = json.loads((ROOT / "artworks.json").read_text(encoding="utf-8"))
    source_folders = [
        path
        for path in (ROOT / "assets" / "artworks").iterdir()
        if path.is_dir() and path.name != "thumbs"
    ]
    folder_names = [folder.name for folder in source_folders]
    category_names = [category["title"]["hu"] for category in artworks["categories"]]
    assert sorted(category_names) == sorted(folder_names)
    assert len(artworks["categories"]) == len(source_folders)
    total_artworks = sum(len(category["works"]) for category in artworks["categories"])
    assert total_artworks >= 8

    folders_by_name = {folder.name: folder for folder in source_folders}
    for category in artworks["categories"]:
        folder = folders_by_name[category["title"]["hu"]]
        assert category["title"]["hu"]
        assert category["title"]["en"]
        txt_files = list(folder.glob("*.txt"))
        if txt_files:
            expected_description = txt_files[0].read_text(encoding="utf-8-sig").strip()
            assert category["description"]["hu"] == expected_description
        for work in category["works"]:
            assert work["id"]
            assert work["title"]["hu"]
            assert work["image"]
            assert work["thumb"]
            assert (ROOT / work["image"]).exists()
            assert (ROOT / work["thumb"]).exists()


if __name__ == "__main__":
    test_site_contract()
