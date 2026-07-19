# siposbarni.com weboldal

Ez a mappa tartalmazza a siposbarni.com statikus portfolio oldal forrasat.

## Fontos fajlok

- `index.html` - az oldal vazszerkezete
- `styles.css` - a fekete-feher minimalista design
- `script.js` - galeria, keplapozo es urlap mukodes
- `content.json` - szovegek es kontakt linkek
- `artworks.json` - galeria adatok
- `assets/artworks` - festmenyek es thumbnail kepek
- `assets/rolam` - a Rolam szekcio forrasanyagai

## Publikalas Cloudflare-re

Modositas utan futtasd:

```powershell
python tools/build-cloudflare-zip.py
```

Ez letrehozza a feltoltheto csomagot:

```text
dist/siposbarni-cloudflare-upload.zip
```

Cloudflare-ben:

1. Workers & Pages
2. `siposbarni`
3. New deployment
4. Toltsd fel a `dist/siposbarni-cloudflare-upload.zip` fajlt

